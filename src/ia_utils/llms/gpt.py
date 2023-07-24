from __future__ import print_function

import json
import re
from os import environ, path

from revChatGPT.V1 import Chatbot
from split_markdown4gpt import split

from ia_utils.fs import open_file


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
        self.base_url = config["base_url"]
        self.auth0_access_token = config["auth0_access_token"]
        self.rev_gpt_config = config["rev_gpt_config"]
        self.captcha_url = config["captcha_url"]
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
        return list(
            map(lambda data: data["conversation_id"], self.chatbot.ask(pre_prompt))
        ).pop()

    def extract_code_block_if_exists(self, content: str):
        def replace_code_block(code_block):
            new_text = re.sub(r"```\S+\n", "", code_block, flags=re.DOTALL)
            return re.sub(r"```", "", new_text, flags=re.DOTALL)

        if "```" not in content:
            return content

        only_code = re.findall(r"```\S+\n+```", content, re.DOTALL)

        try:
            return json.dumps(list(map(replace_code_block, only_code)))
        except Exception as e:
            print(f"An error occurred: {e}")
            return content

    def gpt(self, raw_md_prompt: str) -> str:
        prompts = split(
            raw_md_prompt, model=self.parse_model_alias(self.rev_gpt_config["model"])
        )
        res = [self.__gpt(prompt) for prompt in prompts]

        return "\n---\n".join(res)

    def __gpt(self, prompt) -> str:
        response = ""
        pre_prompts_conv_ids = [
            self.__get_chat_for_pre_prompt(pre_prompt)
            for pre_prompt in self.pre_prompts
        ]

        for conv_id in pre_prompts_conv_ids:
            for data in self.chatbot.ask(prompt, id=conv_id, auto_continue=True):
                response = self.extract_code_block_if_exists(data["message"])
                prompt = response

        return response
