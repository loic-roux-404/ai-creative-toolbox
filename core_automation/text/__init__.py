from jinja2 import Template

from ..text.parser import html_text_config


def exclude_specials(content: str):
    return "".join(e for e in content if e.isalnum() or e == " ")


def limit_title(content: str, max_length: int = 45):
    if len(content) <= max_length:
        return content

    return content[:max_length] + "..."


def extract_title(content: str, max_length: int = 45):
    if len(content.split("\n")) <= 1:
        return limit_title(exclude_specials(content), max_length)

    return limit_title(exclude_specials(content.split("\n")[0]), max_length)


def html_to_md(content: str):
    h = html_text_config()

    return h.handle(content)


def template_title(title: str, title_template: str):
    return Template(title_template).render(dict(title=title))
