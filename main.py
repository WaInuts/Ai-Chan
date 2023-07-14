import os
import random

from discord.ext import commands
import discord
import requests

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def hello(ctx):
  await ctx.send("Hello!")

@bot.command()
async def generate(ctx, type):
  headers = {
    'User-Agent' : 'Gamer Bot - B Box9688' 
  }
  
  if type == 'girl':
    waifuTags = {'Female', 'Solo'}
    id = str(random.randint(1, 1000))
    r = requests.get(f'https://www.zerochan.net/?p={id}&json',headers=headers)
    items = r.json()['items']

    for item in items:
      if waifuTags.issubset(item['tags']):
        await ctx.send(item['thumbnail'])
        return

keep_alive()
bot.run(os.environ['TOKEN'])
