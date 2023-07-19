from __future__ import print_function

import logging
from os import environ, path, makedirs
from dotenv import load_dotenv
import base64
import json
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from revChatGPT.V1 import Chatbot
from google.auth.external_account_authorized_user import Credentials as ExternalAccountCredentials
from google.oauth2.credentials import Credentials as Oauth2Credentials
import html2text

def logging_init(level: int=logging.INFO):
    logging.basicConfig(level=level)
    return logging.getLogger(__name__)

def write_to_file(file_path, content):
    file = open(file_path, 'a')
    file.write(content)
    file.close()

def open_file(file_path):
    file = open(file_path, 'r')
    content = file.read()
    file.close()
    return content

def load_config():
    config = {}
    with open('config.json') as f:
        config = json.load(f)

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

class Context:
    def __init__(self, config):
        self.conversation_id = None
        self.restart_threshold = int(config['gpt_context_max_prompts'] )
        self.pre_prompt = open_file(path.expanduser(config['preprompt_file']))
        self.auth0_access_token = config['auth0_access_token']
        self.rev_gpt_config = config['rev_gpt_config']
        # Init Methods
        self.chatbot = self.__login_chatbot()
        self.__gpt3_pre_prompt(force=True)

    def __login_chatbot(self):
        assert self.auth0_access_token, "auth0_access_token config or env variable must be set"

        environ['CAPTCHA_URL'] = "http://localhost:9090/captcha/"

        return Chatbot(config={**{
            "access_token": self.auth0_access_token}, **self.rev_gpt_config},)
            #base_url="http://localhost:9090/")

    def __gpt3_pre_prompt(self, force=False):
        if self.restart_threshold < 1 and not force:
            return

        self.restart_threshold = 0
        self.chatbot.reset_chat()
        for data in self.chatbot.ask(self.pre_prompt):
            self.conversation_id = data['conversation_id']

    def __split_prompt(self, prompt):
        if (len(prompt) < 10000):
            return [prompt]
        
        print(prompt)
        
        return [prompt[:10000]] + self.__split_prompt(prompt[10000:])


    def gpt3(self, prompt) -> str:
        self.__gpt3_pre_prompt()
        response = ""

        for prompt in self.__split_prompt(prompt):
            for data in self.chatbot.ask(prompt, id=self.conversation_id):
                response = data["message"]
        self.restart_threshold += 1

        return response

def parse_email_query(config):
    watched_addresses = " OR ".join(map(lambda f: f"from:{f}", list(config['from'])))
    mail_query = f"{config['query']} {watched_addresses}"

    return mail_query

def get_email_content(service, user_id, msg_id):
    h = html2text.HTML2Text()
    message = {}

    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
    except Exception as e:
        print(f"An error occurred: {e}")

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
            h.ignore_links = False
            h.drop_white_space = True
            h.ignore_tables = True
            email_data['Body'] = h.handle(content)

    return email_data

def unpack_email_content(email_content):
    return f"""
From: {email_content['From']}
Date: {email_content['Date']}
Subject: {email_content['Subject']}
Body: 
{email_content['Body']}
"""

def mark_as_read(service, user_id, msg_id):
    try:
        message = service.users().messages().modify(
            userId=user_id, 
            id=msg_id, 
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

        return message

    except Exception as e:
        print(f"An error occurred: {e}")

def auth_gcp(config)-> ExternalAccountCredentials | Oauth2Credentials:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    client_secret_location = config['credentials_location']
    assert client_secret_location, "credentials_location variable or env must be set"

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path.expanduser(client_secret_location), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    assert creds, "Credentials must be set"

    return creds

def human_readable_day(day_date):
    date_object = datetime.strptime(day_date, '%Y-%m-%d')
    day_of_week = date_object.strftime('%A-%d')
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
    config = load_config()

    logger = logging_init(int(config['logging_level']))
    mail_query = parse_email_query(config)
    logger.debug(f"Querying for: {mail_query}")

    gpt_context = Context(config)

    creds = auth_gcp(config)

    service = build('gmail', 'v1', credentials=creds)

    messages = []
    try:
        results = service.users().messages().list(userId='me', q=mail_query, maxResults=200).execute()
        messages = results.get('messages', [])
    except HttpError as error:
        print(f'An error occurred: {error}')

    if len(messages) <= 0:
        print('No messages found.')
        return

    for message in messages:
        message_content = get_email_content(service, 'me', message['id'])

        if not message_content:
            print('No message body found.')
            continue

        logger.info(f"Message found: {message_content['Subject']} at {message_content['Date']}")
        logger.info("Started gpt treatment for message")

        content = gpt_context.gpt3(unpack_email_content(message_content))

        filename = date_to_folders_tree(config['save_dir'], message_content['Date'])

        logger.info(f"Finished, saving to : {filename}")
        write_to_file(filename, f"\n---\n{content}")

        mark_as_read(service, 'me', message['id'])

if __name__ == '__main__':
    main()