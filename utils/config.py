import discord
import json

prefix = "."
starting_activity = discord.Activity(type=discord.ActivityType.listening, name=' You... :-)')

with open(r"C:\Users\boo\Desktop/config.json", 'r') as f:
    configData = json.load(f)

DISCORD_TOKEN = configData['TOKENS']['DISCORD']
CHARACTER_AI_TOKEN = configData['TOKENS']['CHARACTER_AI']
GOOGLE_API_KEY = configData['API_KEYS']['GOOGLE']

f.close()

# zeroChan = {
#     'User-Agent' : 'Gamer Bot - B Box9688',
#     "url" : f'https://www.zerochan.net/?p={id}&l=25&s=fav&json'
# }w