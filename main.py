
from discord.ext import commands
import discord
from utils.keep_alive import keep_alive
import os
import asyncio


bot = commands.Bot(command_prefix=".", intents=discord.Intents().all())
bot.remove_command('help')

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        # TOKEN = "MTEyODkzMTk3MDI2OTg0NzU2Mg.Gkilhq.UDjdSsK6iRH9Gp7nmgekgurUCDPgrDQ-QVJbPI"
        TOKEN = open(r"C:\Users\Rj\Desktop/TOKEN.txt","r").readline()
        @bot.event
        async def on_ready():
          print('We have logged in as {0.user}'.format(bot))
        await bot.start(TOKEN)

if __name__=="__main__":
  asyncio.run(main())

# from utils.keep_alive import keep_alive
# from utils.bot import Bot
# import os

# def main():
#   bot = Bot()
#   cog = bot.get_cog('Greetings')
#   commands = cog.get_commands()
#   print([c.name for c in commands])
#   # TOKEN = os.environ.get("TOKEN")
#   TOKEN = "MTEyODkzMTk3MDI2OTg0NzU2Mg.Gkilhq.UDjdSsK6iRH9Gp7nmgekgurUCDPgrDQ-QVJbPI"
#   @bot.event
#   async def on_ready():
#     print('We have logged in as {0.user}'.format(bot))
#   keep_alive()
#   bot.run(TOKEN)

# if __name__=="__main__":
#   main()

# import os
# import random

# from discord.ext import commands
# import discord
# import requests
# import nacl
# import asyncio

# intents = discord.Intents.default()
# intents.message_content = True

# bot = commands.Bot(command_prefix='$', intents=intents)

# @bot.event
# async def on_ready():
#   print('We have logged in as {0.user}'.format(bot))

# @bot.command()
# async def test(ctx):
#   print(ctx.message.author.name)

# @bot.command()
# async def generate(ctx, type):
#   headers = {
#     'User-Agent' : 'Gamer Bot - B Box9688' 
#   }

#   if ctx.message.author.name == "nelsons":
#     r = requests.get(f'https://www.zerochan.net/Klee?json',headers=headers)
#     item = random.choice(tuple(r.json()['items']))
#     await ctx.send(item['thumbnail'])
#     return
  
#   match type:
#     case 'girl':
#       tags = {'Female', 'Solo'}
#     case 'boy':
#       tags = {'Male', 'Solo'}

#   # experimental concept for $generate but requires new parsing method
#   # to generate json objects and improved random generator

#   # url = 'https://www.zerochan.net/'
#   # for tag in tags:
#   #   url += tag
#   #   if tag == tags[-1]:
#   #     url += '?json'
#   #   else:
#   #     url += ','

#   # print(url)
#   # r = requests.get(url,headers=headers)
#   # print(r.json()['items'])
#   # item = random.choice(tuple(r.json()['items']))
#   # await ctx.send(item['thumbnail'])
#   # return
  
#   id = str(random.randint(1, 200))
#   r = requests.get(f'https://www.zerochan.net/?p={id}&l=25&s=fav&json',headers=headers)
#   items = r.json()['items']
#   for item in items:
#     if tags.issubset(item['tags']):
#       await ctx.send(item['thumbnail'])
#       return

      
# @bot.command()
# async def joinVoice(ctx):
#     voice_state = ctx.author.voice

#     if voice_state is not None:
#       await voice_state.channel.connect()
#     else:
#         # Exiting if the user is not in a voice channel
#         return await ctx.send('You need to be in a voice channel to use this command')
#   # discord.VoiceState.channel(ctx.message.author.name)
#   # await connect
#   # TODO: Spotify playlist
#   # 1) Ask spotify to play a random song from a listed playlist (also play song
#   #      from playlist)
#   #     - Retrieve user playlists
#   #     - Play a song by random or selection from playlist
#   # 2) Ask spotify to play a recommended song based on a playlist
#   # 3) General functionality
#   #     - Join voice channel
#   #     - Pause/play
#   #     - Skip
#   #     - Queue
#   #     - List song/artist/link
# keep_alive()
# bot.run('MTEyODkzMTk3MDI2OTg0NzU2Mg.Gkilhq.UDjdSsK6iRH9Gp7nmgekgurUCDPgrDQ-QVJbPI')
