import logging
from typing import Any

from .text import template_context
from .text.md import exclude_links_ref, md_to_text


def start(
    function: callable,
    content: str,
    destination_md: str,
    config: dict[str, Any],
    additional_context: dict[str, Any] = {},
):
    destination = template_context(
        config.get("wav_dest_template", "{{ filename }}.wav"),
        {
            **{"filename": destination_md, "save_dir": config["save_dir"]},
            **additional_context,
        },
    )
    logging.info(f"Generating audio at {destination}")
    function(exclude_links_ref(md_to_text(content)), destination, config)
    logging.info("Finished generating audio")
