"""Blog API router — posts, comments, likes, shares, categories, tags."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.blog import service
from src.blog.exceptions import PostNotFound
from src.blog.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    LikeResponse,
    PostCreate,
    PostDetailResponse,
    PostResponse,
    PostUpdate,
    ShareCountResponse,
    ShareCreate,
    TagResponse,
)
from src.blog.search import search_posts
from src.core.database import SessionDep
from src.core.dependencies import require_admin, require_author
from src.core.pagination import PaginatedResponse, PaginationParams
from src.utils.og_meta import generate_og_meta, generate_share_urls

blog_route = APIRouter(prefix="/posts", tags=["Blog Posts"])
category_route = APIRouter(prefix="/categories", tags=["Categories"])
tag_route = APIRouter(prefix="/tags", tags=["Tags"])


# ══════════════════════════════════════════════════════════════
#  POSTS
# ══════════════════════════════════════════════════════════════

@blog_route.get("/", response_model=PaginatedResponse[PostResponse])
async def list_posts(
    db: SessionDep,
    pagination: PaginationParams = Depends(),
    category: str | None = Query(None, description="Filter by category slug"),
    tag: str | None = Query(None, description="Filter by tag slug"),
    status: str = Query("published", description="Post status filter"),
):
    """List published posts with optional category/tag filters."""
    posts, total = await service.list_posts(
        db,
        status_filter=status,
        category_slug=category,
        tag_slug=tag,
        limit=pagination.per_page,
        offset=pagination.offset,
    )
    return PaginatedResponse.create(
        items=posts, total=total,
        page=pagination.page, per_page=pagination.per_page,
    )


@blog_route.get("/search", response_model=PaginatedResponse[PostResponse])
async def search(
    db: SessionDep,
    q: str = Query(..., min_length=1, description="Search query"),
    pagination: PaginationParams = Depends(),
):
    """Full-text search across blog posts."""
    posts, total = await search_posts(
        db, q, limit=pagination.per_page, offset=pagination.offset,
    )
    return PaginatedResponse.create(
        items=posts, total=total,
        page=pagination.page, per_page=pagination.per_page,
    )


@blog_route.get("/{slug}", response_model=PostDetailResponse)
async def get_post(slug: str, db: SessionDep):
    """Get a single post by slug. Increments view count."""
    post = await service.get_post_by_slug(db, slug)
    if not post:
        raise PostNotFound()
    await service.increment_view_count(db, post.id)

    # Build OG meta and share URLs
    author_name = getattr(post.author, "display_name", None) or getattr(post.author, "username", None)
    og = generate_og_meta(
        title=post.title,
        excerpt=post.excerpt,
        slug=post.slug,
        cover_image_url=post.cover_image_url,
        author_name=author_name,
        published_time=post.created_at.isoformat() if post.created_at else None,
    )
    post_url = og.url
    share_urls = generate_share_urls(post_url, post.title)

    # Build response with OG enrichment
    response = PostDetailResponse.model_validate(post, from_attributes=True)
    response.og_meta = og.to_dict()
    response.share_urls = share_urls
    return response


@blog_route.post(
    "/",
    response_model=PostDetailResponse,
    status_code=201,
    dependencies=[Depends(require_author)],
)
async def create_post(
    payload: PostCreate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Create a new blog post. Requires author or admin role."""
    post = await service.create_post(
        db,
        author_id=current_user.id,
        title=payload.title,
        content_markdown=payload.content_markdown,
        excerpt=payload.excerpt,
        cover_image_url=payload.cover_image_url,
        status=payload.status,
        category_id=payload.category_id,
        tag_names=payload.tag_names,
    )
    return post


@blog_route.patch("/{post_id}", response_model=PostDetailResponse)
async def update_post(
    post_id: UUID,
    payload: PostUpdate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Update a post. Only the author or admin can update."""
    post = await service.update_post(
        db,
        post_id=post_id,
        current_user=current_user,
        **payload.model_dump(exclude_unset=True),
    )
    return post


@blog_route.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: UUID,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Delete a post. Only the author or admin can delete."""
    await service.delete_post(db, post_id, current_user)


# ══════════════════════════════════════════════════════════════
#  COMMENTS
# ══════════════════════════════════════════════════════════════

@blog_route.get("/{post_id}/comments", response_model=PaginatedResponse[CommentResponse])
async def list_comments(
    post_id: UUID,
    db: SessionDep,
    pagination: PaginationParams = Depends(),
):
    """List threaded comments for a post."""
    comments, total = await service.list_comments(
        db, post_id, limit=pagination.per_page, offset=pagination.offset,
    )
    return PaginatedResponse.create(
        items=comments, total=total,
        page=pagination.page, per_page=pagination.per_page,
    )


@blog_route.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    post_id: UUID,
    payload: CommentCreate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Create a comment on a post."""
    comment = await service.create_comment(
        db,
        post_id=post_id,
        user_id=current_user.id,
        body=payload.body,
        parent_id=payload.parent_id,
    )
    return comment


@blog_route.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    payload: CommentUpdate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Edit a comment. Only the author can edit."""
    comment = await service.update_comment(db, comment_id, current_user, payload.body)
    return comment


@blog_route.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: UUID,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Delete a comment. Author or admin only."""
    await service.delete_comment(db, comment_id, current_user)


# ══════════════════════════════════════════════════════════════
#  LIKES
# ══════════════════════════════════════════════════════════════

@blog_route.post("/{post_id}/likes", response_model=LikeResponse)
async def toggle_like(
    post_id: UUID,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Toggle like on a post."""
    liked, total = await service.toggle_like(db, post_id, current_user.id)
    return LikeResponse(liked=liked, total_likes=total)


@blog_route.get("/{post_id}/likes", response_model=LikeResponse)
async def get_likes(post_id: UUID, db: SessionDep):
    """Get like count for a post."""
    total = await service.get_like_count(db, post_id)
    return LikeResponse(liked=False, total_likes=total)


# ══════════════════════════════════════════════════════════════
#  SHARES
# ══════════════════════════════════════════════════════════════

@blog_route.post("/{post_id}/shares", status_code=201)
async def record_share(
    post_id: UUID,
    payload: ShareCreate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    """Record a share event for analytics."""
    await service.record_share(db, post_id, current_user.id, payload.platform)
    return {"msg": "Share recorded"}


@blog_route.get("/{post_id}/shares", response_model=ShareCountResponse)
async def get_shares(post_id: UUID, db: SessionDep):
    """Get share counts by platform."""
    total, by_platform = await service.get_share_counts(db, post_id)
    return ShareCountResponse(total=total, by_platform=by_platform)


# ══════════════════════════════════════════════════════════════
#  CATEGORIES
# ══════════════════════════════════════════════════════════════

@category_route.get("/", response_model=list[CategoryResponse])
async def list_categories(db: SessionDep):
    """List all categories."""
    return await service.list_categories(db)


@category_route.post(
    "/",
    response_model=CategoryResponse,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
async def create_category(payload: CategoryCreate, db: SessionDep):
    """Create a new category. Admin only."""
    return await service.create_category(db, payload.name, payload.description)


@category_route.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(require_admin)],
)
async def update_category(category_id: UUID, payload: CategoryUpdate, db: SessionDep):
    """Update a category. Admin only."""
    return await service.update_category(
        db, category_id,
        name=payload.name,
        description=payload.description,
    )


@category_route.delete(
    "/{category_id}",
    status_code=204,
    dependencies=[Depends(require_admin)],
)
async def delete_category(category_id: UUID, db: SessionDep):
    """Delete a category. Admin only."""
    await service.delete_category(db, category_id)


# ══════════════════════════════════════════════════════════════
#  TAGS
# ══════════════════════════════════════════════════════════════

@tag_route.get("/", response_model=list[TagResponse])
async def list_tags(db: SessionDep):
    """List all tags."""
    return await service.list_tags(db)
