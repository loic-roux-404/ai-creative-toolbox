from __future__ import print_function

import base64
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..mail.helper import MailHelper


class Gmail:
    MODIFY_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

    def __init__(self, creds, mail_helper: MailHelper, logger):
        self.service = build("gmail", "v1", credentials=creds)
        self.logger = logger
        self.mail_helper = mail_helper

    def list_messages(self, mail_query_data: dict):
        messages = []
        try:
            parsed_query = self.parse_email_query(mail_query_data)
            self.logger.debug(f"Querying for: {parsed_query}")
            results = (
                self.service.users()
                .messages()
                .list(userId="me", q=parsed_query, maxResults=200)
                .execute()
            )
            messages = results.get("messages", [])
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")

        if len(messages) <= 0:
            self.logger.warn("No messages found")
            return messages

        return messages

    def parse_email_query(self, config):
        watched_addresses = (
            " OR ".join(map(lambda f: f"from:{f}", list(config["from"])))
            if "from" in config
            else ""
        )
        mail_query = (
            f"{config['query']} {watched_addresses}" if "query" in config else ""
        )

        return mail_query

    def get_email_content(self, user_id, msg_id):
        message = {}
        h = self.mail_helper.html_mail_config()

        try:
            message = (
                self.service.users()
                .messages()
                .get(userId=user_id, id=msg_id, format="full")
                .execute()
            )
            if "payload" not in message:
                raise Exception("No payload in message")
        except Exception as e:
            self.logger.error(e)

        payload = message["payload"]
        headers = payload["headers"]
        parts = payload["parts"] if "parts" in payload else [payload]

        email_data = {}
        for header in headers:
            if header["name"] == "Subject":
                email_data["Subject"] = header["value"]
            elif header["name"] == "From":
                email_data["From"] = header["value"]
            elif header["name"] == "Date":
                cleaned_date = header["value"][:25].strip()
                parsed_date = datetime.strptime(cleaned_date, "%a, %d %b %Y %H:%M:%S")
                email_data["Date"] = str(parsed_date)

        for part in parts:
            data = part["body"]["data"]
            content = base64.urlsafe_b64decode(data).decode("utf-8")

            # 20 char is the minimum for a message to be considered
            if not content or len(content) <= 20:
                continue

            if part["mimeType"] == "text/plain":
                email_data["Body"] = content

            if part["mimeType"] == "text/html":
                email_data["Body"] = h.handle(content)

        return email_data

    def mark_as_read(self, user_id, msg_id):
        try:
            message = (
                self.service.users()
                .messages()
                .modify(userId=user_id, id=msg_id, body={"removeLabelIds": ["UNREAD"]})
                .execute()
            )

            return message

        except Exception as e:
            self.logger.error(e)
