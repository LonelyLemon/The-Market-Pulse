"""Blog module SQLAlchemy models.

Tables: posts, categories, tags, post_tags, comments, likes, shares.
"""

import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base


# ─── Categories ──────────────────────────────────────────────
class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # relationships
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="category", lazy="selectin")


# ─── Tags ────────────────────────────────────────────────────
class Tag(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)


# ─── Post ↔ Tag association ─────────────────────────────────
class PostTag(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),
    )


# ─── Posts ───────────────────────────────────────────────────
class Post(Base):
    __tablename__ = "posts"

    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(350), unique=True, nullable=False, index=True)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft | published | archived
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    search_vector = mapped_column(TSVECTOR, nullable=True)

    # relationships
    category: Mapped["Category | None"] = relationship("Category", back_populates="posts", lazy="selectin")
    author = relationship("User", backref="posts", lazy="selectin")
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="post_tags", lazy="selectin")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", lazy="noload")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="post", lazy="noload")

    __table_args__ = (
        Index("ix_posts_search_vector", "search_vector", postgresql_using="gin"),
    )


# ─── Comments (threaded) ────────────────────────────────────
class Comment(Base):
    __tablename__ = "comments"

    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)

    # relationships
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    author = relationship("User", backref="comments", lazy="selectin")
    replies: Mapped[list["Comment"]] = relationship(
        "Comment", backref="parent", remote_side="Comment.id", lazy="selectin"
    )


# ─── Likes ───────────────────────────────────────────────────
class Like(Base):
    __tablename__ = "likes"

    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # relationships
    post: Mapped["Post"] = relationship("Post", back_populates="likes")

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_like_post_user"),
    )


# ─── Shares ──────────────────────────────────────────────────
class Share(Base):
    __tablename__ = "shares"

    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String(30), nullable=False)  # x | facebook | linkedin | threads
