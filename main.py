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
async def test(ctx):
  print(ctx.message.author.name)

@bot.command()
async def generate(ctx, type):
  headers = {
    'User-Agent' : 'Gamer Bot - B Box9688' 
  }

  if ctx.message.author.name == "nelsons":
    r = requests.get(f'https://www.zerochan.net/Klee?json',headers=headers)
    item = random.choice(tuple(r.json()['items']))
    await ctx.send(item['thumbnail'])
    return
  
  match type:
    case 'girl':
      # tags = {'Female', 'Solo'}
      tags = ['Female','Solo']
    case 'boy':
      # tags = {'Male', 'Solo'}
      tags = ['Male','Solo']

  # experimental concept for $generate but requires new parsing method
  # to generate json objects and improved random generator

  # url = 'https://www.zerochan.net/'
  # for tag in tags:
  #   url += tag
  #   if tag == tags[-1]:
  #     url += '?json'
  #   else:
  #     url += ','

  # print(url)
  # r = requests.get(url,headers=headers)
  # print(r.json()['items'])
  # item = random.choice(tuple(r.json()['items']))
  # await ctx.send(item['thumbnail'])
  # return
  
  id = str(random.randint(1, 200))
  r = requests.get(f'https://www.zerochan.net/?p={id}&l=25&s=fav&json',headers=headers)
  items = r.json()['items']
  for item in items:
    if tags.issubset(item['tags']):
      await ctx.send(item['thumbnail'])
      return

  # TODO: Spotify playlist
keep_alive()
bot.run(os.environ['TOKEN'])
