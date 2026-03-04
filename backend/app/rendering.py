"""Shared markdown rendering helpers."""

import markdown


MARKDOWN_EXTENSIONS = [
    "nl2br",
    "sane_lists",
    "smarty",
]


def markdown_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=MARKDOWN_EXTENSIONS)
