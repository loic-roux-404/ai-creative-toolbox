from __future__ import print_function

import asyncio
import logging
import re
from os import path
from typing import Any

from openai.error import Timeout
from split_markdown4gpt import split
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from ..files import open_file
from .gpt_message import Message, MessageMapper, Role
from .gpt_token_utils import get_max_tokens
from .llm_call_parrallel_processing import LlmCallParallelProcessing


class ChatGPT:
    MODEL_MAPPING = {
        "gpt-4-mobile": "gpt-4",
        "text-davinci-002-render-sha": "gpt-3.5-turbo",
        "text-davinci-002-render-sha-mobile": "gpt-3.5-turbo",
    }

    INTERACTION_SEP = "\n\n"

    def __init__(self, config: dict[str, Any]):
        self.messages = self.open_messages(config.get("messages", []))
        self.chatgpt_base_url = config.get("chatgpt_base_url", None)
        self.model = config.get("model", "gpt-3.5-turbo")
        self.combine_prompts = config.get("combine_prompts", False)
        self.stream = config.get("stream", True)
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
        self.llm_calls_timeout = config.get("llm_calls_timeout", 6 * 60 * 60)
        # environment variables are loaded after base imoprt
        import openai

        self.openai = openai

    @staticmethod
    def open_messages(messages: list[dict[str, str]]) -> list["Message"]:
        mapped_messages = [MessageMapper.deserialize(message) for message in messages]
        return [
            prompt.model_copy(
                update={"content": open_file(path.expanduser(prompt.content))}
            )
            for prompt in mapped_messages
        ]

    def parse_model_alias(self, model: str):
        return self.MODEL_MAPPING[model] if model in self.MODEL_MAPPING else model

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

    def process_prompts(self, raw_md_prompt: str, pre_prompt: Message):
        model = self.parse_model_alias(self.model)
        prompts = split(
            raw_md_prompt,
            model=model,
            limit=pre_prompt.token_limit_with_prompt(model),
        )

        prompts_as_messages = [
            Message(role=Role.USER, content=prompt) for prompt in prompts
        ]

        splitted_prompts = [
            prompts_as_messages[i : i + self.prompt_per_conversation]
            for i in range(0, len(prompts_as_messages), self.prompt_per_conversation)
        ]

        user_prompts = [
            [
                Message(role=Role.USER, content=subprompt.content)
                for batch in splitted_prompts
                for subprompt in batch
            ]
        ]

        results = [
            self.generate_data_with_completions(prompts) for prompts in user_prompts
        ]

        return [item for sub_result_group in results for item in sub_result_group]

    def gpt(self, raw_md_prompt: str) -> str:
        res = [
            self.process_prompts(raw_md_prompt, pre_prompt)
            for pre_prompt in self.messages
        ].pop()

        return self.INTERACTION_SEP.join(res if len(res) > 0 else [raw_md_prompt])

    def sync_llm_calls(self, all_prompts_finalized: list["Message"]):
        llm_call_parrallel_processing = LlmCallParallelProcessing(
            [
                lambda: self.chat_completion_create([message], self.model, self.stream)
                for message in all_prompts_finalized
            ],
            self.rate_limit,
            self.llm_calls_timeout,
        )

        return asyncio.run(llm_call_parrallel_processing.run())

    def generate_data_with_completions(self, prompts: list["Message"]) -> list[str]:
        all_prompts_finalized = (
            [
                Message(
                    role=Role.USER,
                    content=self.INTERACTION_SEP.join(
                        [prompt.content for prompt in self.messages + [prompt]]
                    ),
                )
                for prompt in prompts
            ]
            if self.combine_prompts
            else self.messages + prompts
        )

        return [
            self.extract_code_block_if_exists(result)
            for result in self.sync_llm_calls(all_prompts_finalized)
        ]

    def extract_content_from_stream(self, token: dict[str, Any]) -> str:
        if token is None or len(token.get("choices", [])) <= 0:
            return ""

        content = token["choices"][0].get("delta", {"content": ""}).get("content")
        if content is not None and len(content) > 0:
            return content
        return ""

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=(
            retry_if_exception_type(TimeoutError) | retry_if_exception_type(Timeout)
        ),
    )
    async def chat_completion_create(
        self,
        messages: list["Message"],
        model: str = "gpt-3.5-turbo",
        stream: bool = False,
    ) -> str:
        token_in_message = sum([message.tokens_count(model) for message in messages])

        logging.debug(f"token_in_message: {token_in_message}")

        if token_in_message <= self.min_token:
            return ""

        estimated_timeout = round(token_in_message * self.response_time_per_token)

        chat_completion: Any = self.openai.ChatCompletion.create(
            model=model,
            messages=[message.model_dump() for message in messages],
            stream=stream,
            timeout=estimated_timeout,
            max_tokens=get_max_tokens(model) - token_in_message,
            **self.api_options,
        )

        if isinstance(chat_completion, dict):
            choices: list[Any] = chat_completion.get("choices", [])
            if len(choices) <= 0:
                return ""
            return str(list(chat_completion.get("choices", [])).pop().message.content)

        return "".join(
            [self.extract_content_from_stream(token) for token in chat_completion]
        )
