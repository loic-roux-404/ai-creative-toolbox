import json
import logging
from argparse import Namespace
from os import environ, getcwd, path

from dotenv import load_dotenv

core_env_model = list(
    [
        "CREDENTIALS_LOCATION",
    ]
)

prefix_list = ["OPENAI_", "SUNO_"]


def __load_config__(configfile, envfile, args={}):
    config = {**args}
    with open(path.expanduser(configfile)) as f:
        config = {**json.load(f), **config}

    dotenv_path = (
        path.join(getcwd(), envfile)
        if not envfile.startswith(
            ",/",
        )
        else envfile
    )
    if not path.exists(path.expanduser(dotenv_path)):
        return config

    load_dotenv(dotenv_path)

    # PATH could be a big env var not useful to keep in config
    env_vars = {
        key.lower(): value
        for key, value in environ.items()
        if key in (list(config.keys()) + core_env_model)
        or not all(not key.startswith(prefix) for prefix in prefix_list)
    }

    logging.debug(f"Found in .env : {env_vars}")

    return {**config, **env_vars}


def load_config(args: Namespace):
    config = __load_config__(args.config, args.env_file, vars(args))
    logging.debug(
        f",Loaded config : {config}",
    )
    return config
