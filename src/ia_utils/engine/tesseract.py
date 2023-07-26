from tesserocr import PyTessBaseAPI


def get_img_text(api, img) -> str:
    api.SetImageFile(img)
    return api.GetUTF8Text()


def get_text_from_images(images):
    with PyTessBaseAPI() as api:
        return [get_img_text(api, img.name) for img in images]
