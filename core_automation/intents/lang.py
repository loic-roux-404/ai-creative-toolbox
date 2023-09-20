from typing import Optional

import nltk
from iso639 import Language, LanguageNotFoundError

nltk.download("crubadan")
tc = nltk.classify.textcat.TextCat()


def detect(sent: str, fallback_to: Optional[str] = "en") -> Language:
    try:
        lang = tc.guess_language(sent).strip()
        return Language.from_part3(lang)
    except LanguageNotFoundError as e:
        if fallback_to is None:
            raise e
        return Language.from_part1(fallback_to)
