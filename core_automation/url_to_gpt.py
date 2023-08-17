from .core.container import Container
from .files import url_to_text, write_to_file
from .llms.gpt import RevChatGpt
from .text.parser import extract_title_with_class, first_with_class, html_text_config


def title_consumer(config):
    assert config.selector.element, "Selector element must be set"
    assert config.selector.css_class, "Selector css_class must be set"

    def function(soup):
        res = first_with_class(soup, config.selector.element, config.selector.css_class)
        return res.text if res else "Untitled"

    return function


def start(configfile):
    container = Container(configfile)
    config = container.config
    logger = container.logger

    gpt_context = RevChatGpt(config)

    urls = list(config["urls"])

    for url in urls:
        logger.info(f"Processing url : {url}")
        raw_html = url_to_text(url)

        if not raw_html:
            logger.warn("No message body found.")
            continue

        logger.info("Started LLM processing")

        url_markdown = html_text_config().handle(raw_html)
        content = gpt_context.gpt(url_markdown)

        title = extract_title_with_class(raw_html, title_consumer(config))
        filename = f'{config["save_dir"]}/{title}.md'

        logger.info(f"Finished, saving to : {filename}")

        write_to_file(filename, f"{content}\n\n---\n\n")
