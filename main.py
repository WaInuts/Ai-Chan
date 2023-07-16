import os
import random

from discord.ext import commands
import discord
import requests
import nacl
import yt_dlp as youtube_dl

from keep_alive import keep_alive

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

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
      tags = {'Female', 'Solo'}
    case 'boy':
      tags = {'Male', 'Solo'}

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

@bot.command()
async def play(ctx, url):
    print(url)
    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop)
        ctx.voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.send('Now playing: {}'.format(player.title))
      
@bot.command()
async def joinVoice(ctx):
    voice_state = ctx.author.voice

    if voice_state is not None:
      await voice_state.channel.connect()
    else:
        # Exiting if the user is not in a voice channel
        return await ctx.send('You need to be in a voice channel to use this command')
  # discord.VoiceState.channel(ctx.message.author.name)
  # await connect
  # TODO: Spotify playlist
  # 1) Ask spotify to play a random song from a listed playlist (also play song
  #      from playlist)
  #     - Retrieve user playlists
  #     - Play a song by random or selection from playlist
  # 2) Ask spotify to play a recommended song based on a playlist
  # 3) General functionality
  #     - Join voice channel
  #     - Pause/play
  #     - Skip
  #     - Queue
  #     - List song/artist/link
keep_alive()
bot.run(os.environ['TOKEN'])
