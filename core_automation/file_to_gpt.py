from .core.container import Container
from .files import all_files_in_dirs, file_exists, open_file, write_to_file
from .llms.gpt import RevChatGpt
from .text import template_title
from .text.parser import html_text_config, slugify


def start(configfile):
    container = Container(configfile)
    config = container.config
    logger = container.logger

    gpt_context = RevChatGpt(config)

    files = all_files_in_dirs(list(config["files"]))

    for file in files:
        logger.info(f"Processing file : {file}")
        raw_md = open_file(file)

        if not raw_md:
            logger.warn("No message body found.")
            continue

        title = template_title(
            slugify(file),
            config.get("title_template", "{{ title }}"),
        )
        logger.info(f"Extracting {title}")

        if not config.get("overwrite", False) and file_exists(
            f'{config["save_dir"]}/{title}.md'
        ):
            logger.info(f"Already exists, skipping : {title}")
            continue

        url_markdown = html_text_config().handle(raw_md)

        logger.info("Started LLM processing")
        content = gpt_context.gpt(url_markdown)

        filename = f'{config["save_dir"]}/{title}.md'

        logger.info(f"Finished, saving to : {filename}")

        write_to_file(filename, f"{content}\n\n---\n\n")
