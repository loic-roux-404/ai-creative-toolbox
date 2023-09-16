from __future__ import print_function

import re
from os import path

from split_markdown4gpt import split
from split_markdown4gpt.splitter import OPENAI_MODELS, MarkdownLLMSplitter

from ..files import open_file
from .gpt_message import Message, MessageMapper, Role


class ChatGPT:
    MODEL_MAPPING = {
        "gpt-4-mobile": "gpt-4",
        "text-davinci-002-render-sha": "gpt-3.5-turbo",
        "text-davinci-002-render-sha-mobile": "gpt-3.5-turbo",
    }

    INTERACTION_SEP = "\n\n"

    def __init__(self, config):
        self.messages = self.open_messages(config.get("messages", []))
        self.chatgpt_base_url = config.get("chatgpt_base_url", None)
        self.model = config.get("model", "text-davinci-002-render-sha")
        self.combine_prompts = config.get("combine_prompts", False)
        self.captcha_url = config.get("captcha_url", None)
        self.prompt_per_conversation = config.get("prompt_per_conversation", 1)
        self.max_context_reuse = config.get("max_context_reuse", 0)
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
        def replace_code_block(code_block):
            replaced_code_block_and_lang = re.sub(
                r"```[\s\S]*?\n", "", code_block, flags=re.DOTALL
            )
            return re.sub(r"```", "", replaced_code_block_and_lang, flags=re.DOTALL)

        if "```" not in content:
            return content

        code_blocks = re.findall(r"```[\s\S]*?```", content, re.DOTALL)

        return self.INTERACTION_SEP.join(list(map(replace_code_block, code_blocks)))

    def token_limit_with_prompt(self, model: str, prompt: "Message") -> int:
        return (
            OPENAI_MODELS[model]
            - MarkdownLLMSplitter(gptok_model=model).gpttok_size(
                f"{str(prompt.role)}: {prompt.content}"
            )
            - 1
        )

    def process_prompts(self, raw_md_prompt: str, pre_prompt: Message, res=[]):
        model = self.parse_model_alias(self.model)
        prompts = (
            res
            if len(res) > 0
            else split(
                raw_md_prompt,
                model=model,
                limit=self.token_limit_with_prompt(model, pre_prompt),
            )
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
        res = []
        res = [
            self.process_prompts(raw_md_prompt, pre_prompt, res)
            for pre_prompt in self.messages
        ].pop()

        return self.INTERACTION_SEP.join(res if len(res) > 0 else [raw_md_prompt])

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
            self.extract_code_block_if_exists(self.chat_completion_create([message]))
            for message in all_prompts_finalized
        ]

    def chat_completion_create(
        self,
        messages: list["Message"],
        model: str = "gpt-3.5-turbo",
        stream: bool = False,
    ):
        chat_completion = self.openai.ChatCompletion.create(
            model=model,
            messages=[message.model_dump() for message in messages],
            stream=stream,
        )

        if isinstance(chat_completion, dict):
            return str(list(chat_completion.get("choices", [""])).pop().message.content)

        def extract_content_from_stream(token) -> str:
            content = token["choices"][0]["delta"].get("content")
            if content is not None:
                return content
            return ""

        return "".join(
            [extract_content_from_stream(token) for token in chat_completion]
        )
