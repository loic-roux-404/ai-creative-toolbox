from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI

from ..files import write_to_file

client = OpenAI()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4096,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)


def text_to_speech_wav(text: str, destination, config={}):
    texts = text_splitter.split_text(text)

    responses = [
        client.audio.speech.create(
            model="tts-1", voice=config.get("speaker", "alloy"), input=text
        )
        for text in texts
    ]

    results = b"".join([response.read() for response in responses])

    write_to_file(destination, results)
