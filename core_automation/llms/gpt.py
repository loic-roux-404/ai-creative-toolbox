from __future__ import print_function

import logging
import re
from os import path
from typing import Any

import openai
from joblib import Parallel, delayed
from langchain.text_splitter import CharacterTextSplitter
from openai import RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from ..files import open_file
from .gpt_message import Message, MessageMapper, Role
from .gpt_token_utils import OPENAI_MODELS

# from openai.types.chat.chat_completion import Choice

MODEL_MAPPING = {
    "gpt-4-mobile": "gpt-4",
    "text-davinci-002-render-sha": "gpt-3.5-turbo",
    "text-davinci-002-render-sha-mobile": "gpt-3.5-turbo",
}


class ChatGPT:
    INTERACTION_SEP = "\n\n"

    def __init__(self, config: dict[str, Any]):
        self.messages = self.open_messages(config.get("messages", []))
        self.chatgpt_base_url = config.get("chatgpt_base_url", None)
        self.model = self.parse_model_alias(config.get("model", "gpt-3.5-turbo"))
        self.combine_prompts = config.get("combine_prompts", False)
        self.stream = False  # Not supported yet
        self.response_time_per_token = config.get("response_time_per_token", 12)
        self.min_token = config.get("min_token", 5)
        self.captcha_url = config.get("captcha_url", None)
        self.prompt_per_conversation = config.get("prompt_per_conversation", 1)
        self.max_context_reuse = config.get("max_context_reuse", 0)
        self.token_divider = config.get("token_divider", 1)
        self.api_options = config.get(
            "api_options",
            {
                "temperature": 0.25,
                "presence_penalty": -1.0,
            },
        )
        self.rate_limit = config.get("rate_limit", 60)
        self.rate_limit_per = config.get("rate_limit_per", 60)
        self.remove_footer = config.get("remove_footer", True)
        self.openai = openai.OpenAI()
        self.text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=self.get_chunk_size(self.model, self.messages), chunk_overlap=0
        )

    @staticmethod
    def parse_model_alias(model: str):
        return MODEL_MAPPING[model] if model in MODEL_MAPPING else model

    @staticmethod
    def get_chunk_size(model: str, pre_prompts: list[Message]) -> int:
        return OPENAI_MODELS.get(model, 4096) - sum(
            [pre_prompt.tokens_count(model) for pre_prompt in pre_prompts]
        )

    @staticmethod
    def open_messages(messages: list[dict[str, str]]) -> list["Message"]:
        mapped_messages = [MessageMapper.deserialize(message) for message in messages]
        return [
            prompt.model_copy(
                update={"content": open_file(path.expanduser(prompt.content))}
            )
            for prompt in mapped_messages
        ]

    def extract_code_block_if_exists(self, content: str) -> str:
        def replace_code_block(code_block: str):
            replaced_code_block_and_lang = re.sub(
                r"```[\s\S]*?\n", "", code_block, flags=re.DOTALL
            )
            return re.sub(r"```", "", replaced_code_block_and_lang, flags=re.DOTALL)

        if "```" not in content:
            return content

        code_blocks = re.findall(r"```[\s\S]*?```", content, re.DOTALL)

        return self.INTERACTION_SEP.join(list(map(replace_code_block, code_blocks)))

    def get_content(self, response) -> str:
        try:
            return response.choices[0].message.content
        except KeyError:
            return ""

    def process_prompts(self, raw_md_prompt: str):
        prompts_parts = self.text_splitter.split_text(raw_md_prompt)

        logging.debug(f"prompts_parts: {prompts_parts}")

        user_prompts = [
            Message(role=Role.USER, content=prompt) for prompt in prompts_parts
        ]

        all_prompts_finalized = (
            user_prompts[:-1] if self.remove_footer else user_prompts
        )

        with Parallel(n_jobs=1) as parallel:
            results = list(
                parallel(
                    delayed(self.process_message)(prompt)
                    for prompt in all_prompts_finalized
                )
            )

            logging.debug(f"Results {results}")

            return results

    def gpt(self, raw_md_prompt: str) -> str:
        return self.INTERACTION_SEP.join(self.process_prompts(raw_md_prompt))

    def process_message(self, data: Message) -> str:
        result = self.chat_completion_create(
            self.messages + [data], self.model, self.stream
        )

        return self.extract_code_block_if_exists(result)

    @retry(
        wait=wait_fixed(3600),
        stop=stop_after_attempt(3),
        retry=(
            retry_if_exception_type(TimeoutError)
            | retry_if_exception_type(RateLimitError)
        ),
    )
    def chat_completion_create(
        self,
        messages: list[Message],
        model: str = "gpt-3.5-turbo",
        stream: bool = False,
    ) -> str:
        token_in_message = sum([message.tokens_count(model) for message in messages])

        logging.debug(f"token_in_message: {token_in_message}")

        if token_in_message <= self.min_token:
            return ""

        estimated_timeout = round(token_in_message * self.response_time_per_token)

        chat_completion: Any = self.openai.chat.completions.create(
            model=model,
            messages=[message.model_dump() for message in messages],
            stream=stream,
            timeout=estimated_timeout,
            **self.api_options,
        )

        logging.debug(f"chat_completion: {chat_completion}")

        return self.get_content(chat_completion)
