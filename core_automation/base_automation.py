from __future__ import print_function


class BaseAutomation:
    def __init__(self, config: dict):
        self.config = config
        self.__validate()

    def __validate(self):
        assert self.config["save_dir"], "save_dir config or env variable must be set"

    def start(self):
        raise NotImplementedError
