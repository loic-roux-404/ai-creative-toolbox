from __future__ import print_function

import re
from os import environ, path

from split_markdown4gpt import split
from split_markdown4gpt.splitter import OPENAI_MODELS, MarkdownLLMSplitter

from ..files import open_file


class ChatGPT:
    MODEL_MAPPING = {
        "gpt-4-mobile": "gpt-4",
        "text-davinci-002-render-sha": "gpt-3.5-turbo",
        "text-davinci-002-render-sha-mobile": "gpt-3.5-turbo",
    }

    INTERACTION_SEP = "\n\n"

    def __init__(self, config):
        self.pre_prompts = self.create_pre_prompt(config.get("preprompts", ""))
        self.base_url = config.get("base_url", None)
        self.auth0_access_token = config["auth0_access_token"]
        self.rev_gpt_config = config.get("rev_gpt_config", {})
        self.combine_prompts = config.get("combine_prompts", False)
        self.captcha_url = config.get("captcha_url", None)
        self.rollback_chat = config.get("rollback_chat", 0)
        self.max_context_reuse = config.get("max_context_reuse", 0)
        self.chatbot = self.__login_chatbot()

    @staticmethod
    def create_pre_prompt(pre_prompts: str) -> list[str]:
        return list(
            map(
                lambda prompt: open_file(path.expanduser(prompt)),
                list(pre_prompts),
            )
        )

    def parse_model_alias(self, model: str):
        return self.MODEL_MAPPING[model] if model in self.MODEL_MAPPING else model

    def __login_chatbot(self):
        assert (
            self.auth0_access_token
        ), "auth0_access_token config or env variable must be set"

        if self.captcha_url:
            environ["CAPTCHA_URL"] = self.captcha_url

        # import here to enforce env variables
        from revChatGPT.V1 import Chatbot

        return Chatbot(
            config={**{"access_token": self.auth0_access_token}, **self.rev_gpt_config},
            base_url=self.base_url,
        )

    def __get_conversation_id(self, pre_prompt):
        conversation_id = [
            data["conversation_id"]
            for data in self.chatbot.ask(pre_prompt, auto_continue=True)
        ]

        if len(conversation_id) <= 0:
            raise ConnectionError("No conversation id found")

        return conversation_id.pop()

    def __reinitialise_chat(self, counter: int = 0):
        if (
            self.rollback_chat > 0
            and len(self.chatbot.conversation_id_prev_queue) >= self.rollback_chat
        ):
            self.chatbot.rollback_conversation(self.rollback_chat)
        else:
            self.chatbot.reset_chat() if counter >= self.max_context_reuse else None

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

    def token_limit_with_prompt(self, model: str, prompt: str) -> int:
        return OPENAI_MODELS[model] - MarkdownLLMSplitter(
            gptok_model=model
        ).gpttok_size(prompt)

    def gpt(self, raw_md_prompt: str) -> str:
        model = self.parse_model_alias(self.rev_gpt_config["model"])
        res = []

        for pre_prompt in self.pre_prompts:
            prompts = (
                res
                if len(res) > 0
                else split(
                    raw_md_prompt,
                    model=model,
                    limit=self.token_limit_with_prompt(model, pre_prompt),
                )
            )

            res = [
                self.__gpt(pre_prompt, prompt, count)
                for count, prompt in enumerate(prompts)
            ]

        return self.INTERACTION_SEP.join(res if len(res) > 0 else [raw_md_prompt])

    def generate_data(self, prompt: str, conv_id: int | None = None) -> str:
        return [
            self.extract_code_block_if_exists(data["message"])
            for data in self.chatbot.ask(prompt, id=conv_id, auto_continue=True)
        ].pop()

    def __gpt(self, pre_prompt, prompt, count=0) -> str:
        if self.combine_prompts:
            self.__reinitialise_chat(count)
            return self.generate_data(f"{pre_prompt}{self.INTERACTION_SEP}{prompt}")

        self.__reinitialise_chat(count)
        conv_id = self.__get_conversation_id(pre_prompt)
        return self.generate_data(prompt, conv_id)
