from __future__ import print_function

from .core.container import Container
from .date.date import date_to_folders_tree
from .files import write_to_file
from .llms.gpt import RevChatGpt
from .mail.helper import MailHelper
from .platforms.gcp import auth_gcp
from .platforms.gmail import Gmail


def start(configfile):
    container = Container(configfile)
    config = container.config
    logger = container.logger

    gpt_context = RevChatGpt(config)

    creds = auth_gcp(config, Gmail.MODIFY_SCOPES, "gmail_token.json")
    mail_helper = MailHelper(config)
    gmail = Gmail(creds, mail_helper, logger)

    messages = gmail.list_messages(config)
    logger.info(f"Found {len(messages)} messages")

    for message in messages:
        message_content = gmail.get_email_content("me", message["id"])

        if not message_content:
            logger.warn("No message body found.")
            continue

        logger.info(
            f'Started LLM processing of : {message_content["Subject"]} at '
            + f'{message_content["Date"]}'
        )

        content = mail_helper.email_infos_to_md(message_content)
        content += gpt_context.gpt(message_content["Body"])

        filename = date_to_folders_tree(config["save_dir"], message_content["Date"])

        logger.info(f"Finished, saving to : {filename}")

        write_to_file(filename, f"{content}\n\n---\n\n")

        gmail.mark_as_read("me", message["id"])

        logger.info(f"Readed email {message['id']}")
