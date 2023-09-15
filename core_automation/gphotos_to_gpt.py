from __future__ import print_function

from .core.container import Container
from .engine.easyocr import img_to_text
from .engine.image_magick import convert_image
from .files import url_to_file, write_to_file
from .llms.gpt import ChatGPT
from .platforms.gcp import auth_gcp
from .platforms.gphotos import GooglePhotos
from .text import extract_title


def start(configfile):
    container = Container(configfile)
    config = container.config
    logger = container.logger

    gpt_context = ChatGPT(config)

    creds = auth_gcp(config, GooglePhotos.READ_SCOPES, "gphotos_token.json")
    gphotos = GooglePhotos(creds, logger)

    photos = gphotos.list_photos(config["album_id"])
    logger.info(f"Found {len(photos)} photos, start perspective fix and download")

    images = [
        url_to_file(photo["baseUrl"])
        for photo in photos
        if photo and "baseUrl" in photo
    ]
    image_paths = [image.name for image in images if image is not None]
    joined_image_paths = "\n".join(image_paths)
    logger.info("Finished downloading photos")
    logger.debug(f"Image paths: {joined_image_paths}")

    logger.info("Convert images to compatible format")
    compatible_images = [convert_image(img)[0] for img in image_paths]

    logger.info(f"Started OCR processing of {len(image_paths)} images")

    texts = map(lambda img: img_to_text(img), compatible_images)

    for index, text in enumerate(texts):
        logger.debug(f"Image {index} : {text}")
        photo = photos[index]
        raw_title = extract_title(text)
        logger.debug({i: photo[i] for i in photo if i not in ["baseUrl"]})

        logger.info(f"Started LLM processing of detected : {raw_title}")
        content = gpt_context.gpt(text)
        found_title = extract_title(content)
        logger.info(f"Finished found content : {found_title}")

        dest_filename = (
            config["save_filename"]
            if "save_filename" in config.keys()
            else f"{found_title}.md"
        )
        destination = f"{config['save_dir']}/{dest_filename}.md"

        write_to_file(destination, f"{content}\n\n---\n\n")
        logger.info(f"Finished saving to : {destination}")
