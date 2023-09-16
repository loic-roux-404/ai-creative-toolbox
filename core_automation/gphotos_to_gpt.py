from __future__ import print_function

import logging

from .base_automation import BaseAutomation
from .engine.easyocr import img_to_text
from .engine.image_magick import convert_image
from .files import url_to_file, write_to_file
from .llms.gpt import ChatGPT
from .platforms.gcp import auth_gcp
from .platforms.gphotos import GooglePhotos
from .text import extract_title


class GphotosToGPT(BaseAutomation):
    def __init__(self, config: dict):
        super().__init__(config)
        self.gpt_context = ChatGPT(self.config)

    def start(self):
        creds = auth_gcp(self.config, GooglePhotos.READ_SCOPES, "gphotos_token.json")
        gphotos = GooglePhotos(creds, logging)

        photos = gphotos.list_photos(self.config["album_id"])
        logging.info(f"Found {len(photos)} photos, start perspective fix and download")

        images = [
            url_to_file(photo["baseUrl"])
            for photo in photos
            if photo and "baseUrl" in photo
        ]
        image_paths = [image.name for image in images if image is not None]
        joined_image_paths = "\n".join(image_paths)
        logging.info("Finished downloading photos")
        logging.debug(f"Image paths: {joined_image_paths}")

        logging.info("Convert images to compatible format")
        compatible_images = [convert_image(img)[0] for img in image_paths]

        logging.info(f"Started OCR processing of {len(image_paths)} images")

        texts = map(lambda img: img_to_text(img), compatible_images)

        for index, text in enumerate(texts):
            logging.debug(f"Image {index} : {text}")
            photo = photos[index]
            raw_title = extract_title(text)
            logging.debug({i: photo[i] for i in photo if i not in ["baseUrl"]})

            logging.info(f"Started LLM processing of detected : {raw_title}")
            content = self.gpt_context.gpt(text)
            found_title = extract_title(content)
            logging.info(f"Finished found content : {found_title}")

            dest_filename = (
                self.config["save_filename"]
                if "save_filename" in self.config.keys()
                else f"{found_title}.md"
            )
            destination = f"{self.config['save_dir']}/{dest_filename}.md"

            write_to_file(destination, f"{content}\n\n---\n\n")
            logging.info(f"Finished saving to : {destination}")
