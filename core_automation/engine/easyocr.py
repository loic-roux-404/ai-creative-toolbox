import easyocr


def img_to_text(img: str, langs=["en", "fr", "es"]) -> str:
    reader = easyocr.Reader(langs)
    return "\n".join(reader.readtext(img, detail=0))
