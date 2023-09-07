import re
import unicodedata
from collections.abc import Callable

import html2text
from bs4 import BeautifulSoup, NavigableString, Tag


def first_with_class(
    soup: BeautifulSoup, el: str, class_name: str
) -> Tag | NavigableString | None:
    return soup.find(el, class_=class_name)


def default_extract_consumer(soup: BeautifulSoup) -> str:
    res = soup.find("title")

    return res.text if res else "Untitled"


def extract_title_with_class(
    html: str, consumer: Callable[[BeautifulSoup], str] = default_extract_consumer
) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title = consumer(soup)
    return title


def slugify(text: str) -> str:
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    """

    value = str(text)
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^\w\s-]", "", value.lower())


def html_text_config() -> html2text.HTML2Text:
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.wrap_links = False
    h.body_width = 0
    h.ignore_images = False
    h.drop_white_space = True
    h.ignore_tables = False

    return h
