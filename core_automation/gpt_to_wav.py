import logging
from typing import Any

from text import template_context

from .engine.tts_bark import text_to_speech_wav
from .text.md import exclude_links_ref, md_to_text


def start(
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
    text_to_speech_wav(
        exclude_links_ref(md_to_text(content)),
        destination,
        config.get("wav_speaker"),
    )
    logging.info("Finished generating audio")
