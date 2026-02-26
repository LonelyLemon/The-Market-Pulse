"""Markdown to HTML conversion utility."""

import mistune


_renderer = mistune.create_markdown(
    escape=True,
    plugins=["strikethrough", "table", "url"],
)


def markdown_to_html(md_text: str) -> str:
    """Convert Markdown text to sanitised HTML."""
    if not md_text:
        return ""
    return _renderer(md_text)
