# Letter Synthesis

## Google cloud setup

```bash
terraform init
terraform apply
```

Then follow these google cloud docs :
- [Oauth Consent Screen](https://developers.google.com/gmail/api/quickstart/python#configure_the_oauth_consent_screen)
- [Credentials](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application)

## Configuration variables

- Credential file from gcloud console
- token from https://chat.openai.com/api/auth/session

**Env file, ideal for critical variables :**

```dotenv
CREDENTIALS_LOCATION=path/to/gcp-oauth-credentials.json
AUTH0_ACCESS_TOKEN=token
```

**Json file :**

- save_dir : path to save the generated letter (Example show fully functionnal saving in obsidian vault)

```json
{
    "query": "is:unread",
    "from": [
        "news@changelog.com",
        "noreply@usepanda.com"
    ],
    "logging_level": "20",
    "preprompt_file": "./prompts/letter-synthesis.txt",
    "gpt_context_max_prompts": "1",
    "save_dir": "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/notes/News"
}
```

> Same keys are available for config and env variables

## Recommended virtual environment setup

```bash
conda create -n letter-synthesis python==3.10
```

Then : 

```bash
conda activate letter-synthesis
```

```bash
pip install -r requirements.txt
```

## Start

```bash
python app.py
```
