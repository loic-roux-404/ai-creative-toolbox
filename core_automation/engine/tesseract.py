from tesserocr import PyTessBaseAPI


def get_img_text(api, img) -> str:
    api.SetImageFile(img)
    return api.GetUTF8Text()


def get_text_from_images(images):
    with PyTessBaseAPI() as api:
        return [get_img_text(api, img) for img in images]


def get_text_from_image_bin(api, img_bin):
    api.SetImageBytes(
        img_bin.tobytes(), img_bin.shape[1], img_bin.shape[0], 1, img_bin.shape[1]
    )
    return api.GetUTF8Text()


def get_text_from_images_bin(imgs_bin: list) -> list[str]:
    with PyTessBaseAPI() as api:
        return [get_text_from_image_bin(api, img) for img in imgs_bin]
