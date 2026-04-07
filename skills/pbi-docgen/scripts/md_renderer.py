"""Unified Markdown parser entry point for the docgen pipeline.

Provides two public functions that wrap markdown-it-py:
- parse_prose(): returns a token list for docx_builder's token-walker
- render_prose_html(): returns an HTML string for pdf_builder

Module-level _MD instance is initialized once at import time with
'commonmark' preset and 'table' plugin enabled.
"""

from markdown_it import MarkdownIt

_MD = MarkdownIt('commonmark').enable('table')


def parse_prose(text: str) -> list:
    """Parse Markdown prose into a markdown-it-py token list.
    Returns flat list of block-level tokens; inline tokens nested
    as .children on 'inline' tokens. Do NOT cache or mutate returned tokens."""
    return _MD.parse(text)


def render_prose_html(text: str) -> str:
    """Render Markdown prose directly to an HTML string.
    Pass RAW prose -- do NOT pre-escape. markdown-it-py handles escaping internally.
    Used by pdf_builder to replace _prose_to_html()."""
    return _MD.render(text)
