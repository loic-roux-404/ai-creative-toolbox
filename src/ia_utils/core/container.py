from __future__ import print_function

import json
import logging
from os import environ, getcwd, path

from dotenv import load_dotenv


class Container:
    DEFAULT_CONFIG = {
        "auth0_access_token": None,
        "credentials_location": None,
        "logging_level": logging.INFO,
        "rev_gpt_config": {
            "model": "text-davinci-002-render-sha",
        },
    }

    def __init__(self, configfile):
        self.config = self.load_config(configfile)
        self.logger = self.logging_init(int(self.config["logging_level"]))
        self.__validate()

    def __validate(self):
        assert self.config[
            "auth0_access_token"
        ], "auth0_access_token config or env variable must be set"
        assert self.config[
            "credentials_location"
        ], "credentials_location config or env variable must be set"
        assert self.config["save_dir"], "save_dir config or env variable must be set"

    def logging_init(self, level: int = logging.INFO):
        logging.basicConfig(level=level)
        return logging.getLogger(__name__)

    def load_config(self, configfile):
        config = self.DEFAULT_CONFIG
        with open(path.expanduser(configfile)) as f:
            config = {**config, **json.load(f)}

        dotenv_path = path.join(getcwd(), ".env")
        load_dotenv(dotenv_path)

        env_vars = environ
        keys_to_filter = config.keys()

        filtered_env_vars = {
            key.lower(): value
            for key, value in env_vars.items()
            if key.lower() in keys_to_filter
        }

        return {**config, **filtered_env_vars}
