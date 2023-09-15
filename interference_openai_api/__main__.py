from __future__ import annotations

import argparse
import json
import logging
import random
import string
import sys
import time
import uuid
from os import environ
from typing import Any

import g4f
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from g4f.Provider.base_provider import BaseProvider, format_prompt
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app)


@app.errorhandler(Exception)
def page_not_found(e: Exception):
    code = 400
    if isinstance(e, HTTPException):
        return (
            jsonify(error=e.code, text={"error": e.description, "name": e.name}),
            e.code or code,
        )

    return jsonify(error=code, text={"error": str(e)}), code


class ChatGpt:
    def __init__(self):
        load_dotenv(".env")
        self.auth0_access_token = environ.get("AUTH0_ACCESS_TOKEN", None)
        self.captcha_url = environ.get("CAPTCHA_URL", None)
        self.base_url = environ.get("BASE_URL", None)
        self.chatbot = self.__login_chatbot()

    def __login_chatbot(self):
        assert (
            self.auth0_access_token
        ), "auth0_access_token config or env variable must be set"

        if self.captcha_url:
            environ["CAPTCHA_URL"] = self.captcha_url

        # import here to enforce env variables
        from revChatGPT.V1 import Chatbot

        return Chatbot(
            config={**{"access_token": self.auth0_access_token}},
            base_url=self.base_url,
        )


class OpenaiChat(BaseProvider):
    url = "https://chat.openai.com"
    needs_auth = False
    working = True
    supports_gpt_35_turbo = True
    _access_token = None

    @classmethod
    def create_completion(
        cls,
        model: str,
        messages: list[dict[str, str]],
        stream: bool = False,
        **kwargs: dict,
    ) -> Any:
        chat_gpt = ChatGpt().chatbot

        print(messages)

        formatted = "\n".join(
            [
                "%s: %s" % ((message["role"]).capitalize(), message["content"])
                for message in messages
            ]
        )

        print(formatted)

        final_messages = [
            {
                "id": str(uuid.uuid4()),
                "author": {"role": "user"},
                "content": {
                    "content_type": "text",
                    "parts": [format_prompt(messages)],
                },
            },
        ]

        response = chat_gpt.post_messages(
            final_messages,
            model=model,
            conversation_id=None,
            parent_id=None,
            auto_continue=True,
        )

        return [line for line in response].pop()

    @classmethod
    @property
    def params(cls):
        params = [
            ("model", "str"),
            ("messages", "list[dict[str, str]]"),
            ("stream", "bool"),
            ("proxy", "str"),
            ("access_token", "str"),
            ("cookies", "dict[str, str]"),
        ]
        param = ", ".join([": ".join(p) for p in params])
        return f"g4f.provider.{cls.__name__} supports: ({param})"


@app.route("/chat/completions", methods=["POST"])
def chat_completions():
    model = request.get_json().get("model", "text-davinci-002-render-sha")
    stream = request.get_json().get("stream", False)
    messages = request.get_json().get("messages")

    print(len(messages))

    response = g4f.ChatCompletion.create(
        model=model, messages=messages, stream=stream, provider=OpenaiChat
    )

    completion_id = "".join(random.choices(string.ascii_letters + string.digits, k=28))
    completion_timestamp = int(time.time())

    if not stream:
        return {
            "id": f"chatcmpl-{completion_id}",
            "object": "chat.completion",
            "created": completion_timestamp,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None,
            },
        }

    def streaming():
        for chunk in response:
            completion_data = {
                "id": f"chatcmpl-{completion_id}",
                "object": "chat.completion.chunk",
                "created": completion_timestamp,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": chunk,
                        },
                        "finish_reason": None,
                    }
                ],
            }

            content = json.dumps(completion_data, separators=(",", ":"))
            yield f"data: {content}\n\n"
            time.sleep(0.1)

        end_completion_data: dict[str, Any] = {
            "id": f"chatcmpl-{completion_id}",
            "object": "chat.completion.chunk",
            "created": completion_timestamp,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }
            ],
        }
        content = json.dumps(end_completion_data, separators=(",", ":"))
        yield f"data: {content}\n\n"

    return app.response_class(streaming(), mimetype="text/event-stream")


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Open api interference server")

    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "./config.json"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)

    app.run(host="0.0.0.0", port=1337, debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
