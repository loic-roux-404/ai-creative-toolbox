# Ai Creative Toolbox

Apply a GPT prompt on specific type of content specified in a config.

## Monorepo setup

Base tool install

```bash
make install
```

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

#### Command

```bash
bazelisk run //main_cli:main_cli -- --config configs/gmail.json gmail
```

### Url

> No requirements

```json
{
    "urls": [
        "https://www.python.org/doc/versions/"
    ],
    "preprompts": [
        "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/notes/python-extract-version.md"
    ],
    "save_dir": "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/courses/python",
    "rev_gpt_config": {
        "model": "text-davinci-002-render-sha"
    }
}

```

#### Command

```bash
bazelisk run //main_cli:main_cli -- --config configs/urls.json url
```

### Google Photos

> Not very efficient on images with bad perspective or bad light, but it works for simple OCR

#### Required libraries

```bash
brew install freetype imagemagick
brew install leptonica
brew install tesseract-lang
```

> Mac os / M1 fix : add to your shell start file (.bashrc, .zshrc, /etc/profile) :

```bash
export MAGICK_HOME=$(brew --prefix imagemagick)
export PATH="$MAGICK_HOME/bin:$PATH"
cp /opt/homebrew/Cellar/leptonica/1.83.1/lib/libleptonica.6.dylib /opt/homebrew/Cellar/leptonica/1.83.1/lib/liblept.5.dylib

```

And then run command :

```bash
source .env # Open api and google credentials are needed
bazelisk run //main_cli:main_cli -- --config configs/gphotos.json gphotos
```

---

## Sources :

- https://github.com/bazelbuild/rules_python/blob/main/examples/bzlmod/MODULE.bazel
- Doc gen : https://github.com/loic-roux-404/ai-creative-toolbox/blob/4bbc80b45418c36947cb415fa4a9a097ad708207/tox.ini
