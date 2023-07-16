from __future__ import print_function

import os
from os.path import join, dirname, expanduser
from dotenv import load_dotenv
import base64
import json
from datetime import datetime
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from revChatGPT.V1 import Chatbot
from google.auth.external_account_authorized_user import Credentials as ExternalAccountCredentials
from google.oauth2.credentials import Credentials as Oauth2Credentials

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

class Context:
    def __init__(self, pre_prompt_location, gp3_context_max_prompts):
        self.conversation_id = None
        self.restart_threshold = int(gp3_context_max_prompts)
        self.pre_prompt = open_file(pre_prompt_location)
        self.chatbot = self.__login_chatbot()
        self.__gpt3_pre_prompt()

    def __login_chatbot(self):
        access_token = os.environ.get('AUTH0_ACCESS_TOKEN')
        assert access_token, "AUTH0_ACCESS_TOKEN environment variable must be set"

        return Chatbot(config={
            "access_token": access_token
        })

    def __gpt3_pre_prompt(self):
        if self.restart_threshold < 1:
            return

        self.restart_threshold = 0

        for data in self.chatbot.ask(self.pre_prompt):
            self.conversation_id = data['conversation_id']

    def gpt3(self, prompt) -> str:
        self.__gpt3_pre_prompt()
        response = ""
        for data in self.chatbot.ask(prompt, id=self.conversation_id):
            response = data["message"]
        self.restart_threshold += 1

        return response

def get_email_content(service, user_id, msg_id):
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
        if part['mimeType'] == 'text/plain':
            data = part['body']["data"]
            text = base64.urlsafe_b64decode(data).decode("utf-8")
            email_data['Body'] = text

    return email_data

def mark_as_read(service, user_id, msg_id):
    try:
        message = service.users().messages().modify(userId=user_id, id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
        return message
    except Exception as e:
        print(f"An error occurred: {e}")

def auth_gcp()-> ExternalAccountCredentials | Oauth2Credentials:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

    client_secret_location = os.environ.get('CREDENTIALS_LOCATION')
    assert client_secret_location, "CREDENTIALS_LOCATION environment variable must be set"

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                expanduser(client_secret_location), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    assert creds, "Credentials must be set"

    return creds

def load_config():
    config = {}
    with open('config.json') as f:
        config = json.load(f)

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    env_vars = os.environ
    keys_to_filter = config.keys()

    filtered_env_vars = {
        key.lower(): value
        for key, value in env_vars.items()
        if key in keys_to_filter
    }

    full_config = config.copy()
    full_config.update(filtered_env_vars)

    return config

def main():
    config = load_config()
    logger = logging_init(int(config['logging_level']))
    watched_address = " OR ".join(map(lambda f: f"from:{f}", list(config['from'])))
    mail_query = f"{config['query']} {watched_address}"
    logger.info(f"Querying for: {mail_query}")

    gpt_context = Context(config['preprompt_file'], config['gpt_context_max_prompts'])

    creds = auth_gcp()

    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', q=mail_query, maxResults=200).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
            return

        for message in messages:
            message_content = get_email_content(service, 'me', message['id'])

            if not message_content:
                print('No message body found.')
                continue

            logger.info(f"Message found: {message_content['Subject']} at {message_content['Date']}")
            logger.info("Started gpt treatment for message")

            content = gpt_context.gpt3(json.dumps(message_content))

            only_day_date = message_content['Date'].split(" ")[0]
            save_dir = expanduser(config['save_dir'])
            filename = f"{save_dir}/{only_day_date}.md"

            logger.info(f"Finished, saving to : {filename}")
            write_to_file(filename, f"{content}\n---\n")

            mark_as_read(service, 'me', message['id'])

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()