from .core.container import Container
from .files import file_exists, url_to_text, write_to_file
from .llms.gpt import RevChatGpt
from .text import template_title
from .text.parser import (
    extract_title_with_class,
    first_with_class,
    html_text_config,
    slugify,
)


def title_consumer(config: dict):
    assert "selector" in config, "Selector must be set"
    selector: dict = config.get("selector", {})
    assert "element" in selector, "Selector element must be set"
    assert "css_class" in selector, "Selector css_class must be set"

    def function(soup):
        res = first_with_class(soup, selector["element"], selector["css_class"])
        return res.text if res else "Untitled"

    return function


def start(configfile):
    container = Container(configfile)
    config = container.config
    logger = container.logger

    gpt_context = RevChatGpt(config)

    urls = list(config["urls"])

    title_extract_consumer = title_consumer(config)

    for url in urls:
        logger.info(f"Processing url : {url}")
        raw_html = url_to_text(url)

        if not raw_html:
            logger.warn("No message body found.")
            continue

        title = template_title(
            slugify(extract_title_with_class(raw_html, title_extract_consumer)),
            config.get("title_template", "{{ title }}"),
        )
        logger.info(f"Extracting {title}")

        if not config.get("overwrite", False) and file_exists(
            f'{config["save_dir"]}/{title}.md'
        ):
            logger.info(f"Already exists, skipping : {title}")
            continue

        url_markdown = html_text_config().handle(raw_html)

        logger.info("Started LLM processing")
        content = gpt_context.gpt(url_markdown)

        filename = f'{config["save_dir"]}/{title}.md'

        logger.info(f"Finished, saving to : {filename}")

        write_to_file(filename, f"{content}\n\n---\n\n")
