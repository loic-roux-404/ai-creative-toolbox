from __future__ import print_function

import logging
from os import path
from typing import Any
from unicodedata import normalize

from joblib import Parallel, delayed
from langchain.text_splitter import TokenTextSplitter
from litellm import get_max_tokens
from tiktoken.model import encoding_name_for_model

from ..files import open_file
from .gpt_message import Message, MessageMapper, Role
from .gpt_process import process_message

MODEL_MAPPING = {
    "gpt-4-mobile": "gpt-4",
    "text-davinci-002-render-sha": "gpt-3.5-turbo",
    "text-davinci-002-render-sha-mobile": "gpt-3.5-turbo",
}


class ChatGPT:
    def __init__(self, config: dict[str, Any]):
        self.messages = self.open_messages(config.get("messages", []))
        self.chatgpt_base_url = config.get("chatgpt_base_url", None)
        self.model = self.parse_model_alias(config.get("model", "gpt-3.5-turbo"))
        self.combine_prompts = config.get("combine_prompts", False)
        self.stream = config.get("stream", False)
        self.response_time_per_token = config.get("response_time_per_token", 12)
        self.min_token = config.get("min_token", 5)
        self.captcha_url = config.get("captcha_url", None)
        self.prompt_per_conversation = config.get("prompt_per_conversation", 1)
        self.max_context_reuse = config.get("max_context_reuse", 0)
        self.token_in_out_ratio = config.get("token_divider", 1)
        self.api_options = config.get(
            "api_options",
            {
                "temperature": 0.7,
            },
        )
        self.rate_limit = config.get("rate_limit", 60)
        self.rate_limit_per = config.get("rate_limit_per", 12)
        self.remove_footer = config.get("remove_footer", True)
        self.text_splitter = TokenTextSplitter.from_tiktoken_encoder(
            encoding_name=encoding_name_for_model(self.model),
            chunk_size=self.get_chunk_size(self.model, self.messages),
            chunk_overlap=0,
        )

    @staticmethod
    def parse_model_alias(model: str):
        return MODEL_MAPPING[model] if model in MODEL_MAPPING else model

    @staticmethod
    def get_chunk_size(
        model: str, pre_prompts: list[Message], token_in_out_ratio: int = 0.5
    ) -> int:
        if token_in_out_ratio > 1:
            logging.warning(
                "token_in_out_ratio should be less than 1, setting it to default (0.5)"
            )
            token_in_out_ratio = 0.5

        return int(
            (
                get_max_tokens(model)
                - sum([pre_prompt.tokens_count(model) for pre_prompt in pre_prompts])
            )
            * token_in_out_ratio
        )

    @staticmethod
    def open_messages(messages: list[dict[str, str]]) -> list["Message"]:
        mapped_messages = [MessageMapper.deserialize(message) for message in messages]
        return [
            prompt.copy(update={"content": open_file(path.expanduser(prompt.content))})
            for prompt in mapped_messages
        ]

    def clean_text(self, text: str) -> str:
        return normalize(
            "NFC", text.casefold().encode("ascii", "ignore").decode("utf-8")
        )

    def process_prompts(self, raw_md_prompt: str):
        prompts_parts = self.text_splitter.split_text(raw_md_prompt)

        user_prompts = [
            Message(role=Role.USER, content=prompt) for prompt in prompts_parts
        ]

        all_prompts_finalized = (
            user_prompts[:-1] if self.remove_footer else user_prompts
        )

        with Parallel(n_jobs=4, prefer="threads") as parallel:
            return list(
                parallel(
                    delayed(process_message)(
                        self.messages + [prompt],
                        self.model,
                        self.min_token,
                        self.stream,
                        self.response_time_per_token,
                        self.api_options,
                    )
                    for prompt in all_prompts_finalized
                )
            )

    def gpt(self, raw_md_prompt: str) -> str:
        return "\n\n".join(self.process_prompts(self.clean_text(raw_md_prompt)))
