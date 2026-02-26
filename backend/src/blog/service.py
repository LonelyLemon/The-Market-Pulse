"""Blog service layer — business logic for posts, comments, likes, shares."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.models import User
from src.blog.exceptions import (
    CommentNotFound,
    NotCommentOwner,
    NotPostOwner,
    PostNotFound,
)
from src.blog.models import (
    Category,
    Comment,
    Like,
    Post,
    PostTag,
    Share,
    Tag,
)
from src.utils.markdown import markdown_to_html
from src.utils.slug import slugify, unique_slug


# ──────────────────────────────────────────────────────────────
#  POSTS
# ──────────────────────────────────────────────────────────────

async def create_post(
    db: AsyncSession,
    *,
    author_id: uuid.UUID,
    title: str,
    content_markdown: str,
    excerpt: str | None = None,
    cover_image_url: str | None = None,
    status: str = "draft",
    category_id: uuid.UUID | None = None,
    tag_names: list[str] | None = None,
) -> Post:
    """Create a new blog post with auto-generated slug and HTML."""
    slug = slugify(title)

    # Check for slug collision
    existing = await db.execute(select(Post).where(Post.slug == slug))
    if existing.scalar_one_or_none():
        slug = unique_slug(title)

    content_html = markdown_to_html(content_markdown)

    post = Post(
        author_id=author_id,
        title=title,
        slug=slug,
        content_markdown=content_markdown,
        content_html=content_html,
        excerpt=excerpt or content_markdown[:300],
        cover_image_url=cover_image_url,
        status=status,
        category_id=category_id,
    )
    db.add(post)
    await db.flush()

    # Handle tags
    if tag_names:
        await _sync_post_tags(db, post.id, tag_names)

    await db.commit()
    await db.refresh(post)
    return post


async def update_post(
    db: AsyncSession,
    *,
    post_id: uuid.UUID,
    current_user: User,
    title: str | None = None,
    content_markdown: str | None = None,
    excerpt: str | None = None,
    cover_image_url: str | None = None,
    status: str | None = None,
    category_id: uuid.UUID | None = None,
    tag_names: list[str] | None = None,
) -> Post:
    """Update a post. Only the author or admin can update."""
    post = await get_post_by_id(db, post_id)
    if not post:
        raise PostNotFound()

    user_role = getattr(current_user, "role", "reader")
    if post.author_id != current_user.id and user_role != "admin":
        raise NotPostOwner()

    if title is not None:
        post.title = title
        post.slug = slugify(title)
        # Check collision
        existing = await db.execute(
            select(Post).where(Post.slug == post.slug, Post.id != post_id)
        )
        if existing.scalar_one_or_none():
            post.slug = unique_slug(title)

    if content_markdown is not None:
        post.content_markdown = content_markdown
        post.content_html = markdown_to_html(content_markdown)

    if excerpt is not None:
        post.excerpt = excerpt
    if cover_image_url is not None:
        post.cover_image_url = cover_image_url
    if status is not None:
        post.status = status
    if category_id is not None:
        post.category_id = category_id

    if tag_names is not None:
        await _sync_post_tags(db, post_id, tag_names)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(
    db: AsyncSession,
    post_id: uuid.UUID,
    current_user: User,
) -> None:
    """Delete a post. Author or admin only."""
    post = await get_post_by_id(db, post_id)
    if not post:
        raise PostNotFound()

    user_role = getattr(current_user, "role", "reader")
    if post.author_id != current_user.id and user_role != "admin":
        raise NotPostOwner()

    await db.delete(post)
    await db.commit()


async def get_post_by_id(db: AsyncSession, post_id: uuid.UUID) -> Post | None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    return result.scalar_one_or_none()


async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
    result = await db.execute(select(Post).where(Post.slug == slug))
    return result.scalar_one_or_none()


async def list_posts(
    db: AsyncSession,
    *,
    status_filter: str = "published",
    category_slug: str | None = None,
    tag_slug: str | None = None,
    author_id: uuid.UUID | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[Sequence[Post], int]:
    """List posts with optional filters. Returns (posts, total_count)."""
    stmt = select(Post).where(Post.status == status_filter)
    count_stmt = select(func.count()).select_from(Post).where(Post.status == status_filter)

    if category_slug:
        stmt = stmt.join(Category).where(Category.slug == category_slug)
        count_stmt = count_stmt.join(Category).where(Category.slug == category_slug)

    if tag_slug:
        stmt = stmt.join(PostTag).join(Tag).where(Tag.slug == tag_slug)
        count_stmt = count_stmt.join(PostTag).join(Tag).where(Tag.slug == tag_slug)

    if author_id:
        stmt = stmt.where(Post.author_id == author_id)
        count_stmt = count_stmt.where(Post.author_id == author_id)

    stmt = stmt.order_by(Post.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(stmt)
    count_result = await db.execute(count_stmt)

    return result.scalars().all(), count_result.scalar_one()


async def increment_view_count(db: AsyncSession, post_id: uuid.UUID) -> None:
    post = await get_post_by_id(db, post_id)
    if post:
        post.view_count = (post.view_count or 0) + 1
        await db.commit()


# ──────────────────────────────────────────────────────────────
#  TAGS (helper)
# ──────────────────────────────────────────────────────────────

async def _sync_post_tags(
    db: AsyncSession,
    post_id: uuid.UUID,
    tag_names: list[str],
) -> None:
    """Replace all tags for a post. Creates tags that don't exist yet."""
    # Remove existing associations
    await db.execute(delete(PostTag).where(PostTag.post_id == post_id))

    for name in tag_names:
        name = name.strip()
        if not name:
            continue
        tag_slug = slugify(name)
        result = await db.execute(select(Tag).where(Tag.slug == tag_slug))
        tag = result.scalar_one_or_none()
        if not tag:
            tag = Tag(name=name, slug=tag_slug)
            db.add(tag)
            await db.flush()

        db.add(PostTag(post_id=post_id, tag_id=tag.id))

    await db.flush()


async def list_tags(db: AsyncSession) -> Sequence[Tag]:
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


# ──────────────────────────────────────────────────────────────
#  CATEGORIES
# ──────────────────────────────────────────────────────────────

async def create_category(
    db: AsyncSession,
    name: str,
    description: str | None = None,
) -> Category:
    slug = slugify(name)
    category = Category(name=name, slug=slug, description=description)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def list_categories(db: AsyncSession) -> Sequence[Category]:
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


async def get_category_by_id(db: AsyncSession, category_id: uuid.UUID) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def update_category(
    db: AsyncSession,
    category_id: uuid.UUID,
    name: str | None = None,
    description: str | None = None,
) -> Category:
    cat = await get_category_by_id(db, category_id)
    if not cat:
        from src.blog.exceptions import CategoryNotFound
        raise CategoryNotFound()
    if name is not None:
        cat.name = name
        cat.slug = slugify(name)
    if description is not None:
        cat.description = description
    await db.commit()
    await db.refresh(cat)
    return cat


async def delete_category(db: AsyncSession, category_id: uuid.UUID) -> None:
    cat = await get_category_by_id(db, category_id)
    if not cat:
        from src.blog.exceptions import CategoryNotFound
        raise CategoryNotFound()
    await db.delete(cat)
    await db.commit()


# ──────────────────────────────────────────────────────────────
#  COMMENTS
# ──────────────────────────────────────────────────────────────

async def create_comment(
    db: AsyncSession,
    *,
    post_id: uuid.UUID,
    user_id: uuid.UUID,
    body: str,
    parent_id: uuid.UUID | None = None,
) -> Comment:
    # Verify post exists
    post = await get_post_by_id(db, post_id)
    if not post:
        raise PostNotFound()

    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        body=body,
        parent_id=parent_id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def list_comments(
    db: AsyncSession,
    post_id: uuid.UUID,
    *,
    limit: int = 50,
    offset: int = 0,
) -> tuple[Sequence[Comment], int]:
    """List top-level comments for a post. Replies loaded via relationship."""
    stmt = (
        select(Comment)
        .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
        .order_by(Comment.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    count_stmt = (
        select(func.count())
        .select_from(Comment)
        .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
    )

    result = await db.execute(stmt)
    count_result = await db.execute(count_stmt)
    return result.scalars().all(), count_result.scalar_one()


async def update_comment(
    db: AsyncSession,
    comment_id: uuid.UUID,
    current_user: User,
    body: str,
) -> Comment:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise CommentNotFound()
    if comment.user_id != current_user.id:
        raise NotCommentOwner()

    comment.body = body
    comment.is_edited = True
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(
    db: AsyncSession,
    comment_id: uuid.UUID,
    current_user: User,
) -> None:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise CommentNotFound()

    user_role = getattr(current_user, "role", "reader")
    if comment.user_id != current_user.id and user_role != "admin":
        raise NotCommentOwner()

    await db.delete(comment)
    await db.commit()


# ──────────────────────────────────────────────────────────────
#  LIKES
# ──────────────────────────────────────────────────────────────

async def toggle_like(
    db: AsyncSession,
    post_id: uuid.UUID,
    user_id: uuid.UUID,
) -> tuple[bool, int]:
    """Toggle like. Returns (is_now_liked, total_likes)."""
    post = await get_post_by_id(db, post_id)
    if not post:
        raise PostNotFound()

    result = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        liked = False
    else:
        db.add(Like(post_id=post_id, user_id=user_id))
        liked = True

    await db.commit()

    # Count
    count_result = await db.execute(
        select(func.count()).select_from(Like).where(Like.post_id == post_id)
    )
    total = count_result.scalar_one()
    return liked, total


async def get_like_count(db: AsyncSession, post_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count()).select_from(Like).where(Like.post_id == post_id)
    )
    return result.scalar_one()


# ──────────────────────────────────────────────────────────────
#  SHARES
# ──────────────────────────────────────────────────────────────

async def record_share(
    db: AsyncSession,
    post_id: uuid.UUID,
    user_id: uuid.UUID,
    platform: str,
) -> None:
    post = await get_post_by_id(db, post_id)
    if not post:
        raise PostNotFound()

    share = Share(post_id=post_id, user_id=user_id, platform=platform)
    db.add(share)
    await db.commit()


async def get_share_counts(
    db: AsyncSession,
    post_id: uuid.UUID,
) -> tuple[int, dict[str, int]]:
    """Returns (total_shares, {platform: count})."""
    result = await db.execute(
        select(Share.platform, func.count())
        .where(Share.post_id == post_id)
        .group_by(Share.platform)
    )
    by_platform = {row[0]: row[1] for row in result.all()}
    total = sum(by_platform.values())
    return total, by_platform
