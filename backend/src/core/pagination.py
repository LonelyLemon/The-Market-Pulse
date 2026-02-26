"""Reusable pagination utilities for API endpoints."""

from __future__ import annotations

from typing import Any, Generic, Sequence, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    """Dependency-injectable pagination parameters."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.per_page = per_page

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: Sequence[Any],
        total: int,
        page: int,
        per_page: int,
    ) -> "PaginatedResponse[T]":
        total_pages = max(1, (total + per_page - 1) // per_page)
        return cls(
            items=list(items),
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )
