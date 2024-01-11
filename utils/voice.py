# import requests

# CHUNK_SIZE = 1024
# url = "https://api.elevenlabs.io/v1/text-to-speech/<voice-id>"

# headers = {
import requests
import os
import json
import elevenlabs
from dotenv import load_dotenv

load_dotenv()

elevenlabs.set_api_key(os.getenv('ELEVEN_LABS_API_KEY'))

def text_to_speech(textData):
    audio_stream = elevenlabs.generate(
        text=textData,
        voice="D4WOR9jBKvHgnblSvM6q",
        model="eleven_monolingual_v1",
    )

    elevenlabs.save(audio_stream, 'voice')

