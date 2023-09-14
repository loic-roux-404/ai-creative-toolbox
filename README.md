# Ai Creative Toolbox

Apply a GPT prompt on specific type of content specified in a config.

## Monorepo setup

Install nix :

```bash
sh <(curl -L https://nixos.org/nix/install) --daemon
```

> You could need to run these commands but take care to back up things you need :

```bash
rm -rf /etc/bash.bashrc.backup-before-nix || true
rm -rf /etc/zsh.zshrc.backup-before-nix || true
```

Install direnv

- Mac : `brew install direnv`
- Linux : `apt install -y direnv`

Start nix shell for your preferred shell.

```bash
nix-shell --run zsh
```

Finally enable direnv to automatically set up the environment when changing to this project's directory.

```bash
direnv allow
```

## Google cloud setup

```bash
terraform init
terraform apply
```

Then follow these google cloud docs :

-   [Oauth Consent Screen](https://developers.google.com/gmail/api/quickstart/python#configure_the_oauth_consent_screen)
-   [Credentials](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application)

## Configuration variables

-   Credential file from gcloud console
-   token from https://chat.openai.com/api/auth/session

**Env file, ideal for critical variables :**

```dotenv
CREDENTIALS_LOCATION=path/to/gcp-oauth-credentials.json
AUTH0_ACCESS_TOKEN=token
```

### Start Chat gpt required services

-   `make start`

## Configurations

### Gmail

-   save_dir : path to save the generated letter (Example show fully functionnal saving in obsidian vault)
-   [rev_gpt_config](https://github.com/acheong08/ChatGPT#--optional-configuration)

```json
{
    "query": "is:unread",
    "from": ["news@changelog.com", "noreply@usepanda.com"],
    "messages": [
        {
            "role": "system",
            "content": "path/to/prompt.md"
        },
        {
            "role": "assistant",
            "content": "path/to/prompt.md"
        },
        {
            "role": "user",
            "content": "path/to/prompt.md"
        }
    ],
    "gpt_context_max_prompts": "1",
    "save_dir": "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/notes/News",
    "rev_gpt_config": {
        "model": "text-davinci-002-render-sha"
    },
    "base_url": "http://localhost:9090/api/",
    "captcha_url": "http://localhost:8080/captcha"
}
```

> Same keys are available for config and env variables

#### Command

```bash
bazelisk run //main_cli:main_cli -- --config $(pwd)/configs/gmail.json gmail
```

Or

```bash
PYTHONPATH=$(pwd) \
python main_cli/__main__.py --config configs/gmail.json gmail
```

### Url

> No requirements

```json
{
    "overwrite": false,
    "urls": [
        "https://cdn2.percipio.com/secure/aws/eot/transcripts/course-1/cloudtrain.html"
    ],
    "selector": {
        "element": "h1",
        "css_class": "report_title"
    },
    "messages": [
        {
            "role": "user",
            "content": "~/path/to/prompt.md"
        }
    ],
    "files": [
        "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/courses/ML/"
    ],
    "save_dir": "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/courses/ML",
    "rev_gpt_config": {
        "model": "text-davinci-002-render-sha"
    },
    "base_url": "http://localhost:9090/api/",
    "captcha_url": "http://localhost:8080/captcha",
    "title_template": "{{ title | replace(' ', '-') }}"
}
```

#### Command

```bash
bazelisk run //main_cli:main_cli -- --config $(pwd)/configs/urls.json url
```

### Google Photos

> Not very efficient on images with bad perspective or bad light, but it works for simple OCR

Run command :

```bash
bazelisk run //main_cli:main_cli -- --config $(pwd)/configs/gphotos.json gphotos
```

---

## Stack :

- bazel for monorepo with python rules, node js rules and golang rules
- nixpkgs for lang and library versions
- python : black formatter
- git : pre-commit hooks
