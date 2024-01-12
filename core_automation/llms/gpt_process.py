import logging
import re
from typing import Any

import litellm
from litellm import RateLimitError, completion
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from .gpt_message import Message


def extract_code_block_if_exists(content: str) -> str:
    def replace_code_block(code_block: str):
        replaced_code_block_and_lang = re.sub(
            r"```[\s\S]*?\n", "", code_block, flags=re.DOTALL
        )
        return re.sub(r"```", "", replaced_code_block_and_lang, flags=re.DOTALL)

    if "```" not in content:
        return content

    code_blocks = re.findall(r"```[\s\S]*?```", content, re.DOTALL)

    return "\n\n".join(list(map(replace_code_block, code_blocks)))


def process_message(
    messages: list[Message],
    model: str = "gpt-3.5-turbo",
    min_token: int = 200,
    stream=False,
    response_time_per_token: int = 60,
    api_options={},
) -> str:
    logging.info(f"Processing {len(messages)} messages")

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        litellm.set_verbose = True

    return extract_code_block_if_exists(
        chat_completion_create(
            messages,
            model,
            min_token,
            stream,
            response_time_per_token,
            api_options,
        )
    )


def get_content(response) -> str:
    try:
        return response.choices[0].message.content or ""
    except (KeyError, AttributeError):
        try:
            return response.choices[0].delta.content or ""
        except KeyError:
            return ""


@retry(
    wait=wait_fixed(3600),
    stop=stop_after_attempt(3),
    retry=(
        retry_if_exception_type(TimeoutError) | retry_if_exception_type(RateLimitError)
    ),
)
def chat_completion_create(
    messages: list[Message],
    model: str = "gpt-3.5-turbo",
    min_token: int = 100,
    stream: bool = False,
    response_time_per_token: int = 12,
    api_options={},
) -> str:
    token_in_message = sum([message.tokens_count(model) for message in messages])

    logging.debug(f"token_in_message: {token_in_message}")
    logging.debug(f"messages : {messages}")

    if token_in_message <= min_token:
        return ""

    estimated_timeout = round(token_in_message * response_time_per_token)

    chat_completion: Any = completion(
        model=model,
        messages=[message.dict() for message in messages],
        stream=stream,
        timeout=estimated_timeout,
        **api_options,
    )

    logging.debug(f"chat_completion: {chat_completion}")

    if stream:
        return "".join([get_content(chunk) for chunk in chat_completion])

    return get_content(chat_completion)
