"""
Main file

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.
"""

import argparse
import logging
import sys

import debugpy

from core_automation import __version__

from .config import load_config

__author__ = "loic-roux-404"
__copyright__ = "loic-roux-404"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from core_automation.skeleton import fib`,
# when using this Python module as a library.

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def setup_debugger(port):
    if not port:
        return

    logging.info(f"Starting debugger on port {port}, waiting to attach...")
    debugpy.listen(port)
    debugpy.wait_for_client()


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Automate IA tasks")
    parser.add_argument(
        "--version",
        action="version",
        version=f"core_automation {__version__}",
    )
    parser.add_argument(
        dest="automation", help="Automation choice", type=str, metavar="STR"
    )
    parser.add_argument("--config", type=str, help="Path to the configuration file")
    parser.add_argument(
        "--env-file", type=str, help="Path to the env file", default=".env"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    parser.add_argument(
        "--debugger",
        help="Enable debugger setting his port",
        type=int,
        required=False,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def get_file_to_gpt():
    from core_automation import file_to_gpt

    return file_to_gpt.FileToGpt


def get_gmail_to_gpt():
    from core_automation import gmail_to_gpt

    return gmail_to_gpt.GmailToGPT


def get_url_to_gpt():
    from core_automation import url_to_gpt

    return url_to_gpt.UrlToGpt


def get_gphotos_to_gpt():
    from core_automation import gphotos_to_gpt

    return gphotos_to_gpt.GphotosToGPT


def get_automation(automation: str, config: dict):
    automations = {
        "gmail": get_gmail_to_gpt,
        "gphotos": get_gphotos_to_gpt,
        "url": get_url_to_gpt,
        "file": get_file_to_gpt,
    }

    if automation not in automations:
        raise ValueError(f"Automation {automation} is not supported")

    return automations[automation]()(config)


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "./config.json"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    setup_debugger(args.debugger)

    config = load_config(args)

    automation = get_automation(args.automation, config)

    automation.start()

    _logger.info("Script ends here")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m core_automation.main
    #
    run()
