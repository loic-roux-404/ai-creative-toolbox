from __future__ import print_function

from os import path

from google.auth.external_account_authorized_user import (
    Credentials as ExternalAccountCredentials,
)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.credentials import Credentials as Oauth2Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def auth_gcp(config, scopes) -> ExternalAccountCredentials | Oauth2Credentials:
    client_secret_location = config["credentials_location"]
    assert client_secret_location, "credentials_location variable or env must be set"

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path.expanduser(client_secret_location), scopes
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    assert creds, "Credentials must be set"

    return creds
