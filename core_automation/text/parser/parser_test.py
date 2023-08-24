import html2text
from bs4 import BeautifulSoup

from . import (
    default_extract_consumer,
    extract_title_with_class,
    first_with_class,
    html_text_config,
)


def test_first_with_class():
    soup = BeautifulSoup('<div class="test">content</div>', "html.parser")
    result = first_with_class(soup, "div", "test")
    assert result is not None
    assert result.text == "content"

    result = first_with_class(soup, "div", "not_exist")
    assert result is None


def test_default_extract_consumer():
    soup = BeautifulSoup("<title>Test Title</title>", "html.parser")
    result = default_extract_consumer(soup)
    assert result == "Test Title"

    soup = BeautifulSoup("<div>Test Content</div>", "html.parser")
    result = default_extract_consumer(soup)
    assert result == "Untitled"


def test_extract_title_with_class():
    html = "<title>Test Title</title>"
    result = extract_title_with_class(html)
    assert result == "Test Title"

    html = "<div>Test Content</div>"
    result = extract_title_with_class(html)
    assert result == "Untitled"


def test_html_text_config():
    h = html_text_config()
    assert isinstance(h, html2text.HTML2Text)
    assert h.ignore_links is False
    assert h.wrap_links is False
    assert h.body_width == 0
    assert h.ignore_images is False
    assert h.drop_white_space is True
    assert h.ignore_tables is False
