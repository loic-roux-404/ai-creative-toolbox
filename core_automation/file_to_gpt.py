from __future__ import print_function

import logging

from .base_automation import BaseAutomation
from .files import all_files_in_dirs, file_exists, open_file, write_to_file
from .llms.gpt import ChatGPT
from .text import template_title
from .text.parser import html_text_config, slugify


class FileToGpt(BaseAutomation):
    def __init__(self, config: dict):
        super().__init__(config)
        self.gpt_context = ChatGPT(self.config)

    def start(self):
        files = all_files_in_dirs(list(self.config["files"]))

        for file in files:
            logging.info(f"Processing file : {file}")
            raw_md = open_file(file)

            if not raw_md:
                logging.warn("No message body found.")
                continue

            title = template_title(
                slugify(file),
                self.config.get("title_template", "{{ title }}"),
            )
            logging.info(f"Extracting {title}")

            if not self.config.get("overwrite", False) and file_exists(
                f'{self.config["save_dir"]}/{title}.md'
            ):
                logging.info(f"Already exists, skipping : {title}")
                continue

            url_markdown = html_text_config().handle(raw_md)

            logging.info("Started LLM processing")
            content = self.gpt_context.gpt(url_markdown)

            filename = f'{self.config["save_dir"]}/{title}.md'

            logging.info(f"Finished, saving to : {filename}")

            write_to_file(filename, f"{content}\n\n---\n\n")
