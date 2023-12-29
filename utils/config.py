import discord
import json
import os

prefix = "."
starting_activity = discord.Activity(type=discord.ActivityType.listening, name=' You... :-)')

configJsonDir = os.getcwd() + r"\utils\config.json"
try:
    with open(configJsonDir, 'r') as f:
        configData = json.load(f)
        f.close()
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

    with open(configJsonDir, 'w+') as f:
        json.dump(configData, f, indent=4)
        f.close()

DISCORD_TOKEN = configData['TOKENS']['DISCORD']
CHARACTER_AI_TOKEN = configData['TOKENS']['CHARACTER_AI']
# GOOGLE_API_KEY = configData['API_KEYS']['GOOGLE']

# zeroChan = {
#     'User-Agent' : 'Gamer Bot - B Box9688',
#     "url" : f'https://www.zerochan.net/?p={id}&l=25&s=fav&json'
# }w