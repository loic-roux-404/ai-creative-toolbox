from __future__ import print_function

from core.container import Container
from llms.gpt import RevChatGpt
from platforms.gcp import auth_gcp
from platforms.gphotos import GooglePhotos


def gphotos_to_gpt(configfile):
    container = Container(configfile)
    config = container.config
    logger = container.logger

    gpt_context = RevChatGpt(config)

    creds = auth_gcp(config, GooglePhotos.READ_SCOPES, "gphotos_token.json")
    gphotos = GooglePhotos(creds, logger)

    photos = gphotos.list_photos(config["album_id"])
    logger.info(f"Found {len(photos)} messages")

    for photo in photos:
        print(photo)
        if not photo:
            logger.warn("No message body found.")
            continue

        gpt_context.gpt(photo["id"])
