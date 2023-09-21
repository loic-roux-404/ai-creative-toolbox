import re

from bs4 import BeautifulSoup
from markdown import markdown


def exclude_links_ref(text):
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)

    # Remove all other links
    text = re.sub(r"http(s)?://[a-zA-Z0-9./?=_%:-]+", "", text)

    return text


def md_to_text(md):
    html = markdown(md)
    soup = BeautifulSoup(html, features="html.parser")
    return soup.get_text()
