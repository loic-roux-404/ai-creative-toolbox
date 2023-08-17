from ..text.parser import html_text_config


class MailHelper:
    def __init__(self, config):
        self.config = config

    def email_infos_to_md(self, email_content):
        return f"""
# {email_content['Subject']}
***{email_content['From'].split(" ")[0]}, {email_content['Date']}***
"""

    def html_mail_config(self):
        h = html_text_config()
        h.ignore_tables = True

        return h
