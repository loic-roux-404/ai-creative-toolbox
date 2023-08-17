from __future__ import print_function

import json
import logging
import re
from os import environ, path

from revChatGPT.V1 import Chatbot
from split_markdown4gpt import split
from split_markdown4gpt.splitter import OPENAI_MODELS, MarkdownLLMSplitter

from ..files import open_file


class RevChatGpt:
    MODEL_MAPPING = {
        "gpt-4-mobile": "gpt-4",
        "text-davinci-002-render-sha": "gpt-3.5-turbo",
        "text-davinci-002-render-sha-mobile": "gpt-3.5-turbo",
    }

    def __init__(self, config):
        self.pre_prompts = list(
            map(
                lambda prompt: open_file(path.expanduser(prompt)),
                list(config["preprompts"]),
            )
        )
        self.base_url = config.get("base_url", None)
        self.auth0_access_token = config["auth0_access_token"]
        self.rev_gpt_config = config.get("rev_gpt_config", {})
        self.combine_prompts = config.get("combine_prompts", False)
        self.captcha_url = config.get("captcha_url", None)
        # Init Methods
        self.chatbot = self.__login_chatbot()

    def parse_model_alias(self, model):
        return self.MODEL_MAPPING[model] if model in self.MODEL_MAPPING else model

    def __login_chatbot(self):
        assert (
            self.auth0_access_token
        ), "auth0_access_token config or env variable must be set"

        if self.captcha_url:
            environ["CAPTCHA_URL"] = self.captcha_url

        return Chatbot(
            config={**{"access_token": self.auth0_access_token}, **self.rev_gpt_config},
            base_url=self.base_url,
        )

    def __get_chat_for_pre_prompt(self, pre_prompt):
        self.chatbot.reset_chat()
        return [
            data["conversation_id"]
            for data in self.chatbot.ask(pre_prompt, auto_continue=True)
        ].pop()

    def extract_code_block_if_exists(self, content: str) -> str:
        def replace_code_block(code_block):
            new_text = re.sub(r"```[\s\S]*?\n", "", code_block, flags=re.DOTALL)
            return re.sub(r"```", "", new_text, flags=re.DOTALL)

        if "```" not in content:
            return content

        code_blocks = re.findall(r"```[\s\S]*?```", content, re.DOTALL)

        try:
            print(list(map(replace_code_block, code_blocks)))
            return json.dumps(list(map(replace_code_block, code_blocks)))
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return content

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
            # TODO flatten a newly splitted list of prompts
            # if previous iteration returned prompts overlapps model token limit
            res = [self.__gpt(pre_prompt, prompt) for prompt in prompts]

        return "\n".join(res)

    def generate_data(self, prompt: str, conv_id: int | None = None) -> str:
        return [
            self.extract_code_block_if_exists(data["message"])
            for data in self.chatbot.ask(prompt, id=conv_id, auto_continue=True)
        ].pop()

    def __gpt(self, pre_prompt, prompt) -> str:
        if self.combine_prompts:
            return self.generate_data(f"{pre_prompt} :\n{prompt}")

        conv_id = self.__get_chat_for_pre_prompt(pre_prompt)
        return self.generate_data(prompt, conv_id)
