"""Slug generation utility for blog posts."""

import re
import uuid


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug.

    Examples:
        >>> slugify("Hello World!")
        'hello-world'
        >>> slugify("  Multiple   spaces  ")
        'multiple-spaces'
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text


def unique_slug(text: str) -> str:
    """Generate a slug with a short UUID suffix for guaranteed uniqueness."""
    base = slugify(text)
    suffix = uuid.uuid4().hex[:8]
    return f"{base}-{suffix}"
