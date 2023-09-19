from __future__ import print_function

import logging

from .base_automation import BaseAutomation
from .date.date import date_to_folders_tree
from .files import write_to_file
from .llms.gpt import ChatGPT
from .mail.helper import MailHelper
from .platforms.gcp import auth_gcp
from .platforms.gmail import Gmail
from .text.parser import slugify


class GmailToGPT(BaseAutomation):
    def __init__(self, config: dict):
        super().__init__(config)
        self.gpt_context = ChatGPT(self.config)

    def start(self):
        creds = auth_gcp(self.config, Gmail.MODIFY_SCOPES, "gmail_token.json")
        mail_helper = MailHelper(self.config)
        gmail = Gmail(creds, mail_helper, logging)

        messages = gmail.list_messages(self.config)
        logging.info(f"Found {len(messages)} messages")

        for message in messages:
            message_content = gmail.get_email_content("me", message["id"])

            if not message_content:
                logging.warn("No message body found.")
                continue

            logging.info(
                f'Started LLM processing of : {message_content["Subject"]} at '
                + f'{message_content["Date"]}'
            )

            content = mail_helper.email_infos_to_md(message_content)
            content += self.gpt_context.gpt(message_content["Body"])

            filename = date_to_folders_tree(
                self.config["save_dir"], message_content["Date"]
            )

            logging.info(f"Finished, saving to : {filename}")

            write_to_file(filename, f"{content}\n\n---\n\n")

            if self.config.get("mark_as_read", True):
                gmail.mark_as_read("me", message["id"])

            logging.info(f"Readed email {message['id']}")

            if not self.config.get("wav_enable", False):
                return

            from .gpt_to_wav import start

            start(
                content,
                filename,
                self.config,
                {
                    "slugified_subject": slugify(message_content["Subject"]),
                    "message_id": message["id"],
                },
            )
