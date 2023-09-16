from __future__ import print_function

from os import path

from google.auth.external_account_authorized_user import (
    Credentials as ExternalAccountCredentials,
)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.credentials import Credentials as Oauth2Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def auth_gcp(
    config, scopes: list[str], token_file="token.json"
) -> ExternalAccountCredentials | Oauth2Credentials:
    assert "credentials_location" in config.keys(), "credentials_location must be set"
    client_secret_location = config["credentials_location"]

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token and creds.has_scopes(scopes):
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                path.expanduser(client_secret_location),
                scopes=scopes + ((creds.scopes or []) if creds else []),
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    assert creds, "Credentials must be set"

    return creds
