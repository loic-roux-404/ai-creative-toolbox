from __future__ import print_function

import os
from os.path import join, dirname, expanduser
from dotenv import load_dotenv
import base64
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from revChatGPT.V1 import Chatbot

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

pre_prompt = """
Extrait et place des résumés dans des catégories à partir d'une analyse des articles d'un email donné en entrée. 
Tu es aussi capable de titré, identifier l'auteur et dater les informations du mail. 
Tu es capable de créer les catégories seulement si des informations leurs appartenant sont présentes.

Voici le format du mail avec les catégories à rédiger si cela est utile. Pensons le étapes par étapes :

Auteur:
Date:

- Les Découvertes sur de nouvelles technologies en sciences, energie, ingenierie
- Les Informations, outils et analyses concernants les secteurs du cloud et du développement full-stack
- Les Outils marketing
- Les Actualités blockchain
- Les Actualités sur l'intelligence artificielle
- Les Actualités sur les crypto monnaies
- Les Résumés d'actualité financière
- Les Actualités cryptomonnaie
- Les Résumés d'analyse de cryptomonnaie
- Les Résumés d'analyse d'entreprise fintech
- Les Conseils en développement personnel soit des contenu traitant de psychologie, neurosciences, méditation et tout autres domaines liés.
- Les Tendances en gestion de projet et management
- Les Tendances en gestion de la privée et des données
- Les Tendances en green IT
- Les Tendances en réglementation et régulation des technologies

Nous sommes prêt à recevoir le contenu brut d'un mail.
"""

config = {
    "q": "from:linas@substack.com"# from:dan@tldrnewsletter.com" #is:unread" 
}

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

access_token = os.environ.get('AUTH0_ACCESS_TOKEN')
assert access_token, "AUTH0_ACCESS_TOKEN environment variable must be set"

chatbot = Chatbot(config={
    "access_token": access_token
})

class Context:

    def __init__(self):
        self.conversation_id = None
        self.restart_threshold = 0

    def __gpt3_pre_prompt(self):
        if self.restart_threshold < 2:
            return

        self.conversation_id = None
        self.restart_threshold = 0

        response = ""
        for data in chatbot.ask(pre_prompt, id=self.conversation_id):
            response = data["message"]
            self.conversation_id = data['conversation_id']
        print(response)


    def gpt3(self, prompt):
        self.__gpt3_pre_prompt()
        response = ""
        for data in chatbot.ask(prompt, id=self.conversation_id):
            response = data["message"]
        print(response)
        self.restart_threshold += 1

def get_email_content(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
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
                email_data['Date'] = header['value']

        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body']["data"]
                text = base64.urlsafe_b64decode(data).decode("utf-8")
                email_data['Body'] = text

        return email_data

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    client_secret_location = os.environ.get('CREDENTIALS_LOCATION')
    assert client_secret_location, "CREDENTIALS_LOCATION environment variable must be set"
    context = Context()
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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

    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', q=config['q']).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
            return

        for message in messages:
            message_content = get_email_content(service, 'me', message['id'])

            if not message_content:
                print('No message body found.')
                continue

            context.gpt3(json.dumps(message_content))

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()