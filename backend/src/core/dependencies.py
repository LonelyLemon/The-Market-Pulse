"""Shared authentication and authorization dependencies."""

from functools import wraps
from typing import Callable

from fastapi import Depends, HTTPException, status

from src.auth.dependencies import get_current_user
from src.auth.models import User


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the user is verified."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    return current_user


def require_role(*allowed_roles: str) -> Callable:
    """Dependency factory that restricts access to specific roles.

    Usage:
        @router.post("/", dependencies=[Depends(require_role("admin", "author"))])
    """

    async def _check_role(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        user_role = getattr(current_user, "role", "reader")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' is not allowed. Required: {', '.join(allowed_roles)}",
            )
        return current_user

    return _check_role


# Convenience aliases
require_admin = require_role("admin")
require_author = require_role("admin", "author")
