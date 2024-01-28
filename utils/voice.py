
# ! NEEDED FOR PYTORCH TO WORK ON UBUNTU SERVER (DISCLOUD)!
# ! MUST BE PUT BEFORE "import torch"
# https://stackoverflow.com/questions/52026652/openblas-blas-thread-init-pthread-create-resource-temporarily-unavailable
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import asyncio

import speech_recognition as sr
from discord.ext import commands
import torch


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""

class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""

# https://github.com/snakers4/silero-models#text-to-speech
def silero_tts(text):
    language = "en"
    model = "v3_en"
    speaker = "en_21"
    try:
        print('SET DEVICE FOR TORCH')
        device = torch.device('cpu')
        print('SET NUM OF THREADS')
        torch.set_num_threads(1)
        local_file = 'model.pt'
        print('OS PATH')
        if not os.path.isfile(local_file):
            print('DOWNLOADING')
            torch.hub.download_url_to_file(f'https://models.silero.ai/models/tts/{language}/{model}.pt',
                                        local_file)  
        print('IMPORT PACKAGE')
        model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
        print('MODEL TO DEVICE')
        model.to(device)

        sample_rate = 48000

        print('SAVE WAV')
        return model.save_wav(text=text,
                                    speaker=speaker,
                                    sample_rate=sample_rate)

    except OSError as err:
        print("OS error:", err)
        return
    except RuntimeError as err:
        print('Failed to create Threads: ', err)
        return
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return

def get_text(audioFilePath):
    r = sr.Recognizer()
    with sr.AudioFile(audioFilePath) as source:
        audioFilePath = r.record(source)
        try:
            return r.recognize_google(audioFilePath, language='en-US')
            print('Decoded text from Audio is {}'.format(recognized_text))
        except:
            print('Sorry could not recognize voice')

async def connect(ctx):
    try:
        channel = ctx.author.voice.channel
    except AttributeError:
        raise InvalidVoiceChannel('No channel to join.')
    vc = ctx.voice_client
    if vc:
        if vc.channel.id == channel.id:
            return vc
        try:
            await vc.move_to(channel)
            return vc
        except asyncio.TimeoutError:
            raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
    else:
        try:
            await channel.connect()
            return vc
        except asyncio.TimeoutError:
            raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

