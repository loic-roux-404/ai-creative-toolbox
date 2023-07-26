from __future__ import print_function

from core.container import Container
from engine.tesseract import get_text_from_images
from fs import url_to_image
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
    logger.info(f"Found {len(photos)} photos")

    images = [
        url_to_image(photo["baseUrl"])
        for photo in photos
        if photo and "baseUrl" in photo
    ]
    images = [image for image in images if image is not None]

    texts = get_text_from_images(images)

    [print(gpt_context.gpt(text)) for text in texts]
