from __future__ import print_function

from core.container import Container
from engine.image_magick import convert_image
from engine.opencv import get_img_ocr_optimized
from engine.tesseract import get_text_from_images_bin
from files import url_to_file, write_to_file
from llms.gpt import RevChatGpt
from platforms.gcp import auth_gcp
from platforms.gphotos import GooglePhotos
from text import extract_title


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
        url_to_file(photo["baseUrl"])
        for photo in photos
        if photo and "baseUrl" in photo
    ]
    image_paths = [image.name for image in images if image is not None]
    joined_image_paths = "\n".join(image_paths)
    logger.info("Finished downloading photos")
    logger.debug(f"Image paths: {joined_image_paths}")

    logger.info(f"Started OCR processing of {len(image_paths)} images")
    images = [get_img_ocr_optimized(convert_image(img)[0]) for img in image_paths]
    texts = get_text_from_images_bin(images)

    for text in texts:
        raw_title = extract_title(text)
        logger.info(f"Started LLM processing of {raw_title}")
        content = gpt_context.gpt(text)
        found_title = extract_title(content)
        logger.info(f"Finished found content : {found_title}")

        destination = (
            f"{config['save_dir']}/{getattr(config, 'save_filename', found_title)}.md"
        )

        write_to_file(destination, f"{content}\n\n---\n\n")
        logger.info(f"Finished saving to : {destination}")
