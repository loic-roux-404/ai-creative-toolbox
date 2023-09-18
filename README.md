# Ai Creative Toolbox

Apply a GPT prompt on specific type of content specified in a config.

## Monorepo setup

Install nix :

```bash
sh <(curl -L https://nixos.org/nix/install) --daemon
```

> use `zsh` to run this command on mac os

Install direnv

-   Mac : `brew install direnv`
-   Linux : `apt install -y direnv`

Start nix shell for your preferred shell.

```bash
nix-shell --run zsh
```

Finally enable direnv to automatically set up the environment when changing to this project's directory.

```bash
direnv allow
```

All tools needed for this project are now installed.

## Vscode

- Run `code .` to open all vscode project using nix correctly.
- Run `code ai-creative-toolbox.code-workspace` to open workspaces for better development experience.

## Google cloud setup

In folder `terrraform/` :

-   Setup vars in `prod.tfvars`

```bash
project_name = "Ai creative toolbox"
project_id = "ai-creative-toolbox"
user = "email@example.com"
billing_account = "org-1" # only for production

```

-   Run terraform :

```bash
terraform init
terraform apply -var-file=prod.tfvars
```

Then follow these google cloud docs :

-   [Oauth Consent Screen](https://developers.google.com/gmail/api/quickstart/python#configure_the_oauth_consent_screen)
-   [Credentials](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application)

## Configuration variables

-   Credential file from gcloud console
-   Access token (Optional) [here](https://chat.openai.com/api/auth/session)

#### Environment variables for interference openai server :

```dotenv
CREDENTIALS_LOCATION=path/to/gcp-oauth-credentials.json
AUTH0_ACCESS_TOKEN=token
CHATGPT_BASE_URL=http://localhost:9090/api/
CAPTCHA_URL=http://localhost:9090/captcha
OPENAI_API_BASE="http://0.0.0.0:1337"
OPENAI_ORGANIZATION="org-1"
OPENAI_API_KEY="test-key"
```

> Inside we are using [revChatGPT](https://github.com/acheong08/ChatGPT) and [g4f](https://github.com/xtekky/gpt4free)

##### Also, you can set up official API using SDK default variables :

```dotenv
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_ORGANIZATION=org-1
OPENAI_API_KEY_PATH=/Users/toto/.openai/api_key
```

### Start interference openai required servers

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
    "model": "text-davinci-002-render-sha",
    "chatgpt_base_url": "http://localhost:9090/api/",
    "captcha_url": "http://localhost:8080/captcha"
}
```

> Same keys are available for config and env variables

#### Command

```bash
bazel run //main_cli:main_cli -- --config $(pwd)/configs/gmail.json gmail
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
    "model": "text-davinci-002-render-sha",
    "chatgpt_base_url": "http://localhost:9090/api/",
    "captcha_url": "http://localhost:8080/captcha",
    "title_template": "{{ title | replace(' ', '-') }}"
}
```

#### Command

```bash
bazel run //main_cli:main_cli -- --config $(pwd)/configs/urls.json url
```

### Google Photos

> Not very efficient on images with bad perspective or bad light, but it works for simple OCR

Run command :

```bash
bazel run //main_cli:main_cli -- --config $(pwd)/configs/gphotos.json gphotos
```

---

## Development

### Tests

```bash
bazel test --test_output=all //core_automation:core_automation_test
```

## Stack :

-   bazel for monorepo with python rules, node js rules and golang rules
-   nixpkgs for lang and library versions
-   python : black formatter
-   git : pre-commit hooks
