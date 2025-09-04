import hashlib
from django.core.cache import cache
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def highlight_code(code: str, language: str) -> str:
    """
    Highlights the given code using Pygments and caches the result.

    Args:
        code: The source code to highlight.
        language: The programming language of the code.

    Returns:
        The HTML-formatted highlighted code.
    """
    cache_key = f"code_highlight:{hashlib.md5(code.encode('utf-8')).hexdigest()}:{language}"
    cached_html = cache.get(cache_key)

    if cached_html:
        return cached_html

    try:
        lexer = get_lexer_by_name(language, stripall=True)
    except ValueError:
        # Fallback to a generic lexer if the language is not found
        lexer = get_lexer_by_name('text', stripall=True)

    formatter = HtmlFormatter(style='monokai', full=True, cssclass="source")
    highlighted_html = highlight(code, lexer, formatter)

    # Cache the result for 24 hours
    cache.set(cache_key, highlighted_html, timeout=86400)

    return highlighted_html
