from os import path

from wand.image import Image


def convert_image(image_path, output_format="png", output_path=None):
    if not output_path:
        output_path = image_path

    expanded_image_path = path.expanduser(image_path)
    expanded_output_path = path.expanduser(output_path)

    with Image(filename=expanded_image_path) as img:
        img.format = output_format
        img.save(filename=expanded_output_path)

    return output_path, img
