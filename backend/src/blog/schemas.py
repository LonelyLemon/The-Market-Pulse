"""Pydantic schemas for the blog module."""

from __future__ import annotations

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── Category ────────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    created_at: datetime


# ─── Tag ─────────────────────────────────────────────────────
class TagCreate(BaseModel):
    name: str = Field(..., max_length=80)


class TagResponse(BaseModel):
    id: UUID
    name: str
    slug: str


# ─── Post ────────────────────────────────────────────────────
class PostCreate(BaseModel):
    title: str = Field(..., max_length=300)
    content_markdown: str
    excerpt: str | None = None
    cover_image_url: str | None = None
    status: str = Field("draft", pattern=r"^(draft|published|archived)$")
    category_id: UUID | None = None
    tag_names: list[str] = Field(default_factory=list, description="Tag names to attach")


class PostUpdate(BaseModel):
    title: str | None = None
    content_markdown: str | None = None
    excerpt: str | None = None
    cover_image_url: str | None = None
    status: str | None = Field(None, pattern=r"^(draft|published|archived)$")
    category_id: UUID | None = None
    tag_names: list[str] | None = None


class PostAuthorResponse(BaseModel):
    id: UUID
    username: str
    display_name: str | None = None
    avatar_url: str | None = None


class PostResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    excerpt: str | None
    cover_image_url: str | None
    status: str
    view_count: int
    author: PostAuthorResponse | None = None
    category: CategoryResponse | None = None
    tags: list[TagResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class PostDetailResponse(PostResponse):
    content_html: str
    content_markdown: str
    og_meta: dict[str, str] = {}
    share_urls: dict[str, str] = {}


# ─── Comment ─────────────────────────────────────────────────
class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)
    parent_id: UUID | None = None


class CommentUpdate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)


class CommentAuthorResponse(BaseModel):
    id: UUID
    username: str
    display_name: str | None = None
    avatar_url: str | None = None


class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    user_id: UUID
    parent_id: UUID | None
    body: str
    is_edited: bool
    author: CommentAuthorResponse | None = None
    created_at: datetime
    updated_at: datetime


# ─── Like ────────────────────────────────────────────────────
class LikeResponse(BaseModel):
    liked: bool
    total_likes: int


# ─── Share ───────────────────────────────────────────────────
class ShareCreate(BaseModel):
    platform: str = Field(..., pattern=r"^(x|facebook|linkedin|threads|copy)$")


class ShareCountResponse(BaseModel):
    total: int
    by_platform: dict[str, int] = Field(default_factory=dict)
