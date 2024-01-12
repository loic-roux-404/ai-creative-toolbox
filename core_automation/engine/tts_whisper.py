from openai import OpenAI

client = OpenAI()


def text_to_speech_wav(text: str, destination, config={}):
    response = client.audio.speech.create(
        model="tts-1", voice=config.get("speaker", "alloy"), input=text
    )

    response.stream_to_file(destination)
