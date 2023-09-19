from __future__ import print_function

import logging

from .base_automation import BaseAutomation
from .files import file_exists, url_to_text, write_to_file
from .llms.gpt import ChatGPT
from .text import template_variable
from .text.parser import (
    extract_title_with_class,
    first_with_class,
    html_text_config,
    slugify,
)


class UrlToGpt(BaseAutomation):
    def __init__(self, config: dict):
        super().__init__(config)
        self.gpt_context = ChatGPT(self.config)

    def start(self):
        urls = list(self.config["urls"])

        title_extract_consumer = self.title_consumer(self.config)

        for url in urls:
            logging.info(f"Processing url : {url}")
            raw_html = url_to_text(url)

            if not raw_html:
                logging.warn("No message body found.")
                continue

            title = template_variable(
                slugify(extract_title_with_class(raw_html, title_extract_consumer)),
                self.config.get("title_template", "{{ title }}"),
            )
            logging.info(f"Extracting {title}")

            if not self.config.get("overwrite", False) and file_exists(
                f'{self.config["save_dir"]}/{title}.md'
            ):
                logging.info(f"Already exists, skipping : {title}")
                continue

            url_markdown = html_text_config().handle(raw_html)

            logging.info("Started LLM processing")
            content = self.gpt_context.gpt(url_markdown)

            filename = f'{self.config["save_dir"]}/{title}.md'

            logging.info(f"Finished, saving to : {filename}")

            write_to_file(filename, f"{content}\n\n---\n\n")

            if not self.config.get("wav_enable", False):
                return

            from .gpt_to_wav import start

            start(content, filename, self.config, {"title": title})

    @staticmethod
    def title_consumer(config: dict):
        assert "selector" in config, "Selector must be set"
        selector: dict = config.get("selector", {})
        assert "element" in selector, "Selector element must be set"
        assert "css_class" in selector, "Selector css_class must be set"

        def function(soup):
            res = first_with_class(soup, selector["element"], selector["css_class"])
            return res.text if res else "Untitled"

        return function
