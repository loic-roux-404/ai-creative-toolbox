import html2text


class MailHelper:
    def __init__(self, config):
        self.config = config

    def email_infos_to_md(self, email_content):
        return f"""
# {email_content['Subject']}
***{email_content['From'].split(" ")[0]}, {email_content['Date']}***

"""

    def html_text_config(self):
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.wrap_links = False
        h.body_width = 0
        h.ignore_images = False
        h.drop_white_space = True
        h.ignore_tables = True

        return h
