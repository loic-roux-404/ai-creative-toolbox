def exclude_specials(content: str):
    return "".join(e for e in content if e.isalnum() or e == " ")


def limit_title(content: str, max_length: int = 40):
    if len(content) <= max_length:
        return content

    return content[:max_length] + "..."


def extract_title(content: str, max_length: int = 40):
    if len(content.split("\n")) <= 1:
        return limit_title(exclude_specials(content), max_length)

    return limit_title(exclude_specials(content.split("\n")[0]), max_length)
