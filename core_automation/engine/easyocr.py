import easyocr


def img_to_text(img: str, langs=["en", "fr", "es"]) -> str:
    reader = easyocr.Reader(langs)
    return "".join(reader.readtext(img, detail=0))
