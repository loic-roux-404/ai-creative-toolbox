from split_markdown4gpt.splitter import OPENAI_MODELS, MarkdownLLMSplitter

OFFSET_ROLE_STAMP = 3


def get_max_tokens(model: str):
    return OPENAI_MODELS.get(model, 2048)


def token_limit_with_prompt(model: str, role: str, content: str) -> int:
    return (
        OPENAI_MODELS[model]
        - MarkdownLLMSplitter(gptok_model=model).gpttok_size(f"{role}: {content}")
        - OFFSET_ROLE_STAMP
    )


def token_count(model: str, role: str, content: str) -> int:
    return MarkdownLLMSplitter(gptok_model=model).gpttok_size(f"{role}: {content}")
