<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/ia-utils.svg?branch=main)](https://cirrus-ci.com/github/<USER>/ia-utils)
[![ReadTheDocs](https://readthedocs.org/projects/ia-utils/badge/?version=latest)](https://ia-utils.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/ia-utils/main.svg)](https://coveralls.io/r/<USER>/ia-utils)
[![PyPI-Server](https://img.shields.io/pypi/v/ia-utils.svg)](https://pypi.org/project/ia-utils/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/ia-utils.svg)](https://anaconda.org/conda-forge/ia-utils)
[![Monthly Downloads](https://pepy.tech/badge/ia-utils/month)](https://pepy.tech/project/ia-utils)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/ia-utils)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# ia-utils

Apply a GPT prompt on specific emails found in a config.

## Google cloud setup

```bash
terraform init
terraform apply
```

Then follow these google cloud docs :
- [Oauth Consent Screen](https://developers.google.com/gmail/api/quickstart/python#configure_the_oauth_consent_screen)
- [Credentials](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application)

## Lib setup

```bash
brew install freetype imagemagick
brew install leptonica
brew install tesseract-lang
```

> Mac os / M1 fix : `export MAGICK_HOME=$(brew --prefix imagemagick) && export PATH="$MAGICK_HOME/bin:$PATH"`

## Configuration variables

- Credential file from gcloud console
- token from https://chat.openai.com/api/auth/session

**Env file, ideal for critical variables :**

```dotenv
CREDENTIALS_LOCATION=path/to/gcp-oauth-credentials.json
AUTH0_ACCESS_TOKEN=token
```

**Json file :**

### Gmail

- save_dir : path to save the generated letter (Example show fully functionnal saving in obsidian vault)
- [rev_gpt_config](https://github.com/acheong08/ChatGPT#--optional-configuration)


```json
{
    "query": "is:unread",
    "from": [
        "news@changelog.com",
        "noreply@usepanda.com"
    ],
    "logging_level": "20",
    "preprompt_file": "./path/to/prompt",
    "gpt_context_max_prompts": "1",
    "save_dir": "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/notes/News",
    "rev_gpt_config": {
        "model": "text-davinci-002-render-sha"
    }
}
```

> Same keys are available for config and env variables

### Google Photos

# TODO

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
python python src/ia_utils/main.py --config configs/gmail.json gmail
```

## Development

- [Pyscaffold](https://github.com/pyscaffold/pyscaffold)

Build :

```bash
pip install -e .
```

Other tasks :

```bash
tox -av
```
