import discord
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Use Dev Token or Production Token
DEBUG = os.getenv('DEBUG')

# Prefix for commands on Discord
prefix = "h."
# Activity shown when users play videogames/music, but instead it's for our bot :3
starting_activity = discord.Activity(type=discord.ActivityType.listening, name=' You... :-)')

try:
    if DEBUG == 'TRUE':
        DISCORD_TOKEN = os.getenv('DISCORD_TOKEN_DEV')
        # TODO: change to other character ai token for debugging
        CHARACTER_AI_TOKEN = os.getenv('CHARACTER_AI_TOKEN_DEV')
    else: 
        DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        CHARACTER_AI_TOKEN = os.getenv('CHARACTER_AI_TOKEN')
except:
    DISCORD_TOKEN = input("Enter Discord bot OAuth2: ")
    CHARACTER_AI_TOKEN = input("Enter Character.ai user OAuth: ")

LISTEN_MOE = 'https://listen.moe/stream'