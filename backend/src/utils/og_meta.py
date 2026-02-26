"""Open Graph and Twitter Card meta tag generation for social sharing previews."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OGMeta:
    """Open Graph + Twitter Card metadata for a blog post."""

    title: str
    description: str
    url: str
    image: str | None = None
    site_name: str = "The Market Pulse"
    og_type: str = "article"
    author: str | None = None
    published_time: str | None = None

    def to_dict(self) -> dict:
        """Return metadata as a flat dict for API responses."""
        meta = {
            "og:title": self.title,
            "og:description": self.description,
            "og:url": self.url,
            "og:type": self.og_type,
            "og:site_name": self.site_name,
            "twitter:card": "summary_large_image" if self.image else "summary",
            "twitter:title": self.title,
            "twitter:description": self.description,
        }
        if self.image:
            meta["og:image"] = self.image
            meta["twitter:image"] = self.image
        if self.author:
            meta["article:author"] = self.author
        if self.published_time:
            meta["article:published_time"] = self.published_time
        return meta

    def to_html_tags(self) -> str:
        """Render as HTML <meta> tags (useful for SSR or prerender)."""
        tags = []
        for key, value in self.to_dict().items():
            prop = "name" if key.startswith("twitter:") else "property"
            tags.append(f'<meta {prop}="{key}" content="{_escape(value)}" />')
        return "\n".join(tags)


def generate_og_meta(
    *,
    title: str,
    excerpt: str | None,
    slug: str,
    cover_image_url: str | None = None,
    author_name: str | None = None,
    published_time: str | None = None,
    base_url: str = "https://themarketpulse.com",
) -> OGMeta:
    """Build Open Graph metadata for a blog post."""
    description = (excerpt or "")[:200]
    url = f"{base_url}/posts/{slug}"

    return OGMeta(
        title=title,
        description=description,
        url=url,
        image=cover_image_url,
        author=author_name,
        published_time=published_time,
    )


def generate_share_urls(post_url: str, post_title: str) -> dict[str, str]:
    """Generate social platform share URLs for a post."""
    from urllib.parse import quote

    encoded_url = quote(post_url, safe="")
    encoded_title = quote(post_title, safe="")

    return {
        "x": f"https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
        "threads": f"https://www.threads.net/intent/post?text={encoded_title}%20{encoded_url}",
    }


def _escape(value: str) -> str:
    """Escape HTML special characters for meta tag content."""
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
