import os
import torch
import requests
import urllib.parse
from pathlib import Path

import speech_recognition as sr
from pydub import AudioSegment

# https://github.com/snakers4/silero-models#text-to-speech
def silero_tts(tts, language, model, speaker):
    device = torch.device('cpu')
    torch.set_num_threads(4)
    local_file = 'model.pt'

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(f'https://models.silero.ai/models/tts/{language}/{model}.pt',
                                    local_file)  

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    sample_rate = 48000

    return model.save_wav(text=tts,
                                speaker=speaker,
                                sample_rate=sample_rate)


def get_text(audioFilePath):
    r = sr.Recognizer()
    with sr.AudioFile(audioFilePath) as source:
        audioFilePath = r.record(source)
        try:
            return r.recognize_google(audioFilePath, language='en-US')
            print('Decoded text from Audio is {}'.format(recognized_text))
        except:
            print('Sorry could not recognize voice')