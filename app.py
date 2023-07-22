from __future__ import print_function

import logging
from os import environ, path, makedirs
from dotenv import load_dotenv
import base64
import json
from datetime import datetime
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from revChatGPT.V1 import Chatbot
from google.auth.external_account_authorized_user import Credentials as ExternalAccountCredentials
from google.oauth2.credentials import Credentials as Oauth2Credentials
import html2text
from split_markdown4gpt import split

def write_to_file(file_path, content):
    file = open(file_path, 'a')
    file.write(content)
    file.close()

def open_file(file_path):
    file = open(file_path, 'r')
    content = file.read()
    file.close()
    return content

class Container:
    DEFAULT_CONFIG = {
        "auth0_access_token": None,
        "credentials_location": None,
        "logging_level": logging.INFO,
        "rev_gpt_config": {
            "model": "text-davinci-002-render-sha",
        }
    }

    def __init__(self, configfile):
        self.config = self.load_config(configfile)
        self.logger = self.logging_init(int(self.config['logging_level']))

    def logging_init(self, level: int=logging.INFO):
        logging.basicConfig(level=level)
        return logging.getLogger(__name__)

    def load_config(self, configfile):
        config = self.DEFAULT_CONFIG
        with open(path.expanduser(configfile)) as f:
            config = {**config, **json.load(f)}

        dotenv_path = path.join(path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        env_vars = environ
        keys_to_filter = config.keys()

        filtered_env_vars = {
            key.lower(): value
            for key, value in env_vars.items()
            if key.lower() in keys_to_filter
        }

        return {**config, **filtered_env_vars}

class RevChatGpt:
    MODEL_MAPPING = {
        "gpt-4-mobile": "gpt-4",
        "text-davinci-002-render-sha": "gpt-3.5-turbo",
        "text-davinci-002-render-sha-mobile": "gpt-3.5-turbo"
    }

    def __init__(self, config):
        self.conversation_prompt_nb = int(config['gpt_context_max_prompts'] )
        self.pre_prompts = list(map(lambda prompt: open_file(path.expanduser(prompt)), list(config['preprompts'])))
        self.base_url = config['base_url']
        self.auth0_access_token = config['auth0_access_token']
        self.rev_gpt_config = config['rev_gpt_config']
        self.captcha_url = config['captcha_url']
        # Init Methods
        self.chatbot = self.__login_chatbot()

    def parse_model_alias(self, model):
        return self.MODEL_MAPPING[model] if model in self.MODEL_MAPPING else model

    def __login_chatbot(self):
        assert self.auth0_access_token, "auth0_access_token config or env variable must be set"

        if self.captcha_url:
            environ['CAPTCHA_URL'] = self.captcha_url

        return Chatbot(config={**{
            "access_token": self.auth0_access_token}, **self.rev_gpt_config}, base_url=self.base_url)

    def __get_chat_for_pre_prompt(self, pre_prompt):
        self.chatbot.reset_chat()
        return list(map(lambda data: data['conversation_id'], self.chatbot.ask(pre_prompt))).pop()

    def extract_code_block_if_exists(self, content: str):
        def replace_code_block(code_block):
            new_text = re.sub(r"```\S+\n", "", code_block, flags=re.DOTALL)
            return re.sub(r"```", "", new_text, flags=re.DOTALL)

        if "```" not in content:
            return content

        only_code = re.findall(r"```\S+\n+```", content, re.DOTALL)

        try:
            return json.dumps(list(map(replace_code_block, only_code)))
        except Exception as e:
            print(f"An error occurred: {e}")
            return content

    def gpt(self, raw_md_prompt: str) -> str:
        final_response = ""
        prompts = split(raw_md_prompt, model=self.parse_model_alias(self.rev_gpt_config['model']))

        for prompt in prompts:
            final_response = self.__gpt(prompt)

        return final_response

    def __gpt(self, prompt) -> str:
        response = f"{prompt}"

        for pre_prompt in self.pre_prompts:
            conv_id = self.__get_chat_for_pre_prompt(pre_prompt)
            for data in self.chatbot.ask(response, id=conv_id, auto_continue=True):
                response = self.extract_code_block_if_exists(data["message"])

        return response

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
        h.inline_links = False
        h.body_width = 0
        h.ignore_images = False
        h.drop_white_space = True
        h.ignore_tables = True

        return h

def auth_gcp(config, scopes)-> ExternalAccountCredentials | Oauth2Credentials:

    client_secret_location = config['credentials_location']
    assert client_secret_location, "credentials_location variable or env must be set"

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path.expanduser(client_secret_location), scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    assert creds, "Credentials must be set"

    return creds

class Gmail():
    MODIFY_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    def __init__(self, creds, mail_helper, logger):
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger = logger
        self.mail_helper = mail_helper

    def list_messages(self, mail_query_data: dict):
        messages = []
        try:
            parsed_query = self.parse_email_query(mail_query_data)
            self.logger.debug(f"Querying for: {parsed_query}")
            results = self.service.users().messages().list(userId='me', q=parsed_query, maxResults=200).execute()
            messages = results.get('messages', [])
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")

        if len(messages) <= 0:
            self.logger.warn(f"No messages found")
            return messages

        return messages

    def parse_email_query(self, config):
        watched_addresses = " OR ".join(map(lambda f: f"from:{f}", list(config['from']))) if 'from' in config else ''
        mail_query = f"{config['query']} {watched_addresses}" if 'query' in config else ''

        return mail_query

    def get_email_content(self, user_id, msg_id):
        message = {}
        h = self.mail_helper.html_text_config()

        try:
            message = self.service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        except Exception as e:
            self.logger.error(e)

        payload = message['payload']
        headers = payload['headers']
        parts = payload['parts']
        
        email_data = {}
        for header in headers:
            if header['name'] == 'Subject':
                email_data['Subject'] = header['value']
            elif header['name'] == 'From':
                email_data['From'] = header['value']
            elif header['name'] == 'Date':
                cleaned_date = header['value'][:25].strip()
                parsed_date = datetime.strptime(cleaned_date, "%a, %d %b %Y %H:%M:%S")
                email_data['Date'] = str(parsed_date)

        for part in parts:
            data = part['body']["data"]
            content = base64.urlsafe_b64decode(data).decode("utf-8")

            # 20 char is the minimum for a message to be considered
            if not content or len(content) <= 20:
                continue

            if part['mimeType'] == 'text/plain':
                email_data['Body'] = content

            if part['mimeType'] == 'text/html':
                email_data['Body'] = h.handle(content)

        return email_data

    def mark_as_read(self, user_id, msg_id):
        try:
            message = self.service.users().messages().modify(
                userId=user_id, 
                id=msg_id, 
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            return message

        except Exception as e:
            self.logger.error(e)

def human_readable_day(day_date):
    date_object = datetime.strptime(day_date, '%Y-%m-%d')
    day_of_week = date_object.strftime('%d-%A')
    return day_of_week

def human_readable_month(month_nb):
    date_object = datetime.strptime(month_nb, '%m')
    return date_object.strftime('%B')

def date_to_folders_tree(save_dir, date):
    only_day_date = date.split(" ")[0]
    save_dir = path.expanduser(save_dir)
    year, month = only_day_date.split("-")[0], only_day_date.split("-")[1]
    human_r_day = human_readable_day(only_day_date)
    human_r_month = human_readable_month(month)
    final_dir = f"{save_dir}/{year}/{human_r_month}"

    if not path.exists(final_dir):
        makedirs(final_dir)

    return f"{final_dir}/{human_r_day}.md"

def main():
    container = Container('config.json')
    config = container.config
    logger = container.logger

    gpt_context = RevChatGpt(config)

    creds = auth_gcp(config, Gmail.MODIFY_SCOPES)
    mail_helper = MailHelper(config)
    gmail = Gmail(creds, mail_helper, logger)

    messages = gmail.list_messages(config)
    logger.info(f"Found {len(messages)} messages")

    for message in messages:
        message_content = gmail.get_email_content('me', message['id'])

        if not message_content:
            logger.warn('No message body found.')
            continue

        logger.info(f"Message found: {message_content['Subject']} at {message_content['Date']}")
        logger.info("Started gpt treatment for message")

        content = mail_helper.email_infos_to_md(message_content)
        content += gpt_context.gpt(message_content['Body'])

        filename = date_to_folders_tree(config['save_dir'], message_content['Date'])

        logger.info(f"Finished, saving to : {filename}")

        write_to_file(filename, f"{content}\n\n---\n\n")

        gmail.mark_as_read('me', message['id'])

if __name__ == '__main__':
    main()