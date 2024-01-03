import discord
import json
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHARACTER_AI_TOKEN = os.getenv('CHARACTER_AI_TOKEN')

prefix = "."
starting_activity = discord.Activity(type=discord.ActivityType.listening, name=' You... :-)')

try:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    CHARACTER_AI_TOKEN = os.getenv('CHARACTER_AI_TOKEN')
except:
    DISCORD_TOKEN = input("Enter Discord bot OAuth2: ")
    CHARACTER_AI_TOKEN = input("Enter Character.ai user OAuth: ")
    configData = {
        'TOKENS' :
        {
            'DISCORD' : DISCORD_TOKEN,
            'CHARACTER_AI' : CHARACTER_AI_TOKEN
        },
        'API_KEYS' :
        {
        }
    }

# DISCORD_TOKEN = configData['TOKENS']['DISCORD']
# CHARACTER_AI_TOKEN = configData['TOKENS']['CHARACTER_AI']
# GOOGLE_API_KEY = configData['API_KEYS']['GOOGLE']

# zeroChan = {
#     'User-Agent' : 'Gamer Bot - B Box9688',
#     "url" : f'https://www.zerochan.net/?p={id}&l=25&s=fav&json'
# }w