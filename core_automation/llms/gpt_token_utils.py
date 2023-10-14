from split_markdown4gpt.splitter import OPENAI_MODELS, MarkdownLLMSplitter


def token_limit_with_prompt(model: str, role: str, content: str) -> int:
    return (
        OPENAI_MODELS[model]
        - MarkdownLLMSplitter(gptok_model=model).gpttok_size(f"{role}: {content}")
        - 3
    )


def token_count(model: str, role: str, content: str) -> int:
    return MarkdownLLMSplitter(gptok_model=model).gpttok_size(f"{role}: {content}")
