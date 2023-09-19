import logging
from os import path

import nltk
import numpy as np
from bark import SAMPLE_RATE
from bark.api import semantic_to_waveform
from bark.generation import generate_text_semantic, preload_models
from scipy.io import wavfile

from ..intents.lang import detect

GEN_TEMP = 0.6
SPEAKER = "v2/%s_speaker_%s"
silence = np.zeros(int(0.25 * SAMPLE_RATE))
nltk.download("punkt")

preload_models()


def re_tokenize(sent, speaker=1):
    lang = detect(sent)
    full_speaker = SPEAKER % (lang.part1, speaker)
    logging.debug(f"Speaker : {full_speaker} for sent : {sent}")
    try:
        return (nltk.sent_tokenize(sent, lang.name.lower()), full_speaker)
    except LookupError:
        return (nltk.sent_tokenize(sent), SPEAKER % ("en", speaker))


def text_to_speech_wav(text: str, destination, speaker=1):
    adapted_text = [f"{sent} " for sent in text.strip().split("\n")]
    full_dest = path.expanduser(destination)
    sents_with_speaker = [re_tokenize(text_part, speaker) for text_part in adapted_text]

    twodimension_pieces = [
        _sentence_to_piece(sub_sent, sent[1])
        for sent in sents_with_speaker
        for sub_sent in sent[0]
    ]

    pieces = [piece for sublist in twodimension_pieces for piece in sublist]

    wavfile.write(full_dest, SAMPLE_RATE, np.concatenate(pieces))

    return wavfile.read(full_dest)


def _sentence_to_piece(sentence: str, speaker: str):
    logging.debug(f"WAV - processing sentence : {sentence}")
    logging.debug(f"WAV - speaker : {speaker}")
    semantic_tokens = generate_text_semantic(
        sentence,
        history_prompt=speaker,
        temp=GEN_TEMP,
        min_eos_p=0.05,  # this controls how likely the generation is to end
    )

    audio_array = (
        semantic_to_waveform(semantic_tokens, history_prompt=speaker)
        if len(sentence) > 3
        else silence.copy()
    )
    return [audio_array, silence.copy()]
