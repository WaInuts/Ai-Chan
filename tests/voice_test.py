import os

import speech_recognition as sr
import pytest
import filetype

from utils.TTS import *

ROOT_DIR = os.path.abspath(os.curdir)

# def test_audio_speech_recognition():

def test_get_text():
    audioFilePath = fr'{ROOT_DIR}\tests\in\discord_sample.wav'
    text = get_text(audioFilePath)
    assert text.lower() == 'hello hows it going'

def test_silero_tts_pass():
    tts = "this is a test"
    language = "en"
    model = "v3_en"
    speaker = "en_21"

    audio = silero_tts(tts, language, model, speaker)

    recognized_text = get_text(audio)
            
    assert tts.lower() == recognized_text.lower()