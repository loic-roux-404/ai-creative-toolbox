# Ai Creative Toolbox

Apply a GPT prompt on specific type of content specified in a config.

## Table of contents
  * [Installation](#installation)
  * [Google cloud setup](#google-cloud-setup)
  * [Environment variables](#environment-variables)
    - [Environment variables for official API](#environment-variables-for-official-api)
  * [Configurations](#configurations)
    + [Gmail](#gmail)
    + [Url](#url)
    + [Google Photos](#google-photos)
  * [Development](#development)
    * [Monorepo setup](#monorepo-setup)
    + [Vscode](#vscode)
    + [Tests](#tests)
  * [Known issues](#known-issues)

## Installation

We're using pre-packaged wheel for python dependencies. So you don't need to install bazel or python dependencies.

```bash
pip install 'https://github.com/loic-roux-404/ai-creative-toolbox/releases/download/main_cli@v0.1.0/ai_creative_toolbox-0.1.0-py3-none-any.whl'
```

Then `ai-creative-toolbox` command is available.

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

## Environment variables

-   Credential file from gcloud console
-   Access token (Optional) [here](https://chat.openai.com/api/auth/session)

#### Environment variables for official API

Also, you can set up official API using SDK default variables :

```dotenv
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_ORGANIZATION=org-1
OPENAI_API_KEY_PATH=/Users/toto/.openai/api_key
```

## Configurations

### Gmail

-   save_dir : path to save the generated letter (Example show fully functionnal saving in obsidian vault)

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
    "model": "text-davinci-002-render-sha"
}
```

> Same keys are available for config and env variables

Run command :

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
    "title_template": "{{ title | replace(' ', '-') }}"
}
```

Run command :

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

### Monorepo setup

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


### Vscode

- Run `code .` to open all vscode project using nix correctly.
- Run `code ai-creative-toolbox.code-workspace` to open workspaces for better development experience.


### Tests

```bash
bazel test --test_output=all //core_automation:core_automation_test
```

After updating nix dependencies :

```bash
bazel clean --expunge && bazel sync
```

## Known issues

Bazel commands on mac os are giving : `xcodebuild: error: SDK "" cannot be located.`

Track this issue [here](https://github.com/bazelbuild/bazel/issues/12049) to get the date of bazel 7. The issue comes from the fact that bazel is using the default shell (/usr/bin, /bin ...) to get the default c++ toolchain.

Also you can consider trying to force nix xcode with `    export SDKROOT=$(xcrun --show-sdk-path)` or `DEVELOPER_DIR=$(xcode-select -print-path)`. But it's not working for me.

So for now we keep a non hermetic build on mac os using machine xcode (check [.bazelrc](.bazelrc), `--macos_sdk_version=14.0`).
