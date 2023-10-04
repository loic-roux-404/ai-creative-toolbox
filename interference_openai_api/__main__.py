from __future__ import annotations

import argparse
import json
import logging
import random
import string
import sys
import time
from typing import Any

import g4f
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app)


@app.errorhandler(Exception)
def openai_error_handler(e: Exception):
    code = 400
    name = "Bad Request"
    description = "Invalid request"
    logging.debug(e)
    logging.error(e)

    if isinstance(e, HTTPException):
        code = e.code or code
        name = e.name or name
        description = e.description or description

    return (
        jsonify(
            code=code,
            error={
                "error": {
                    "type": name,
                    "internal_message": description,
                    "param": e.args,
                    "code": code,
                }
            },
            message=description,
        ),
        code,
    )


@app.route("/chat/completions", methods=["POST"])
def chat_completions():
    model = request.get_json().get("model", "text-davinci-002-render-sha")
    stream = request.get_json().get("stream", False)
    messages = request.get_json().get("messages")

    auth0_access_token = app.config.get("AUTH0_ACCESS_TOKEN")

    logging.debug(messages)

    response = g4f.ChatCompletion.create(
        model=model,
        stream=stream,
        messages=messages,
        provider=g4f.Provider.OpenaiChat,
        access_token=auth0_access_token,
        auth="token",
        proxy_url=app.config.get("CHATGPT_BASE_URL"),
    )

    logging.debug(response)

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


def init_env(app, env_file):
    load_dotenv(env_file)
    from os import environ

    app.config["AUTH0_ACCESS_TOKEN"] = environ.get("AUTH0_ACCESS_TOKEN")
    app.config["CHATGPT_BASE_URL"] = environ.get("CHATGPT_BASE_URL")


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
    parser.add_argument(
        "--env-file", type=str, help="Path to the env file", default=".env"
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

    init_env(app, args.env_file)

    app.run(host="0.0.0.0", port=1337, debug=True)


if __name__ == "__main__":
    main(sys.argv[1:])
