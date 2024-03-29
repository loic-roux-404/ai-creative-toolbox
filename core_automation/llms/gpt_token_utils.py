import tiktoken

OPENAI_MODELS = {
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
    "gpt-4-0613": 8192,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
}


def token_count(model: str, content: str) -> int:
    gptoker = tiktoken.encoding_for_model(model)
    return len(list(gptoker.encode(content)))
