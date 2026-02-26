"""Tests for utility modules — slug, markdown, og_meta, pagination, rbac."""

import pytest
from unittest.mock import MagicMock


# ═══════════════════════════════════════════════════════════
#  Slug tests
# ═══════════════════════════════════════════════════════════

from src.utils.slug import slugify, unique_slug


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_chars(self):
        assert slugify("Hello World!!! @#$") == "hello-world"

    def test_multiple_spaces(self):
        assert slugify("  Multiple   spaces  ") == "multiple-spaces"

    def test_already_slug(self):
        assert slugify("already-a-slug") == "already-a-slug"

    def test_unicode(self):
        result = slugify("Café & Résumé")
        assert "caf" in result  # Depends on locale, but should lowercase

    def test_underscores(self):
        assert slugify("some_thing_here") == "some-thing-here"

    def test_leading_trailing_dashes(self):
        assert slugify("--hello--") == "hello"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_numbers(self):
        assert slugify("Top 10 Tips") == "top-10-tips"


class TestUniqueSlug:
    def test_has_suffix(self):
        result = unique_slug("Hello World")
        assert result.startswith("hello-world-")
        # UUID hex suffix is 8 chars
        suffix = result.split("hello-world-")[1]
        assert len(suffix) == 8

    def test_uniqueness(self):
        results = {unique_slug("Same Title") for _ in range(10)}
        assert len(results) == 10  # All unique


# ═══════════════════════════════════════════════════════════
#  Markdown tests
# ═══════════════════════════════════════════════════════════

from src.utils.markdown import markdown_to_html


class TestMarkdownToHtml:
    def test_basic_conversion(self):
        html = markdown_to_html("**bold**")
        assert "<strong>bold</strong>" in html

    def test_heading(self):
        html = markdown_to_html("# Title")
        assert "<h1>" in html

    def test_empty(self):
        assert markdown_to_html("") == ""

    def test_none_like_empty(self):
        assert markdown_to_html("") == ""

    def test_link(self):
        html = markdown_to_html("[click](http://example.com)")
        assert "http://example.com" in html

    def test_code_block(self):
        html = markdown_to_html("```python\nprint('hi')\n```")
        assert "print" in html

    def test_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = markdown_to_html(md)
        assert "<table>" in html


# ═══════════════════════════════════════════════════════════
#  OG Meta tests
# ═══════════════════════════════════════════════════════════

from src.utils.og_meta import generate_og_meta, generate_share_urls, OGMeta


class TestOgMeta:
    def test_basic_meta(self):
        meta = generate_og_meta(
            title="Test Post",
            excerpt="A description",
            slug="test-post",
        )
        d = meta.to_dict()
        assert d["og:title"] == "Test Post"
        assert "A description" in d["og:description"]
        assert "test-post" in d["og:url"]
        assert "twitter:card" in d

    def test_with_image(self):
        meta = generate_og_meta(
            title="Test",
            excerpt="Desc",
            slug="test",
            cover_image_url="http://example.com/img.jpg",
        )
        d = meta.to_dict()
        assert d["og:image"] == "http://example.com/img.jpg"

    def test_html_tags(self):
        meta = generate_og_meta(title="Test", excerpt="Desc", slug="test")
        html = meta.to_html_tags()
        assert 'property="og:title"' in html

    def test_share_urls(self):
        urls = generate_share_urls("http://example.com/p/1", "My Post")
        assert "twitter.com" in urls["x"]
        assert "facebook.com" in urls["facebook"]
        assert "linkedin.com" in urls["linkedin"]
        assert "threads.net" in urls["threads"]

