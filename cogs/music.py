from discord.ext import commands
import discord

import yt_dlp as youtube_dl
import discord
import requests
import asyncio

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

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.loop = {}
        self.queue = {}

    @commands.command()    
    async def play(self, ctx, url):
        print(url)
        # server = ctx.message.guild
        # voice_channel = server.voice_client
        voice_state = ctx.author.voice
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.loop)
            voice = await voice_state.channel.connect()
            voice.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: {}'.format(player.title))
    
    @commands.command()
    async def joinVoice(self, ctx):
        voice_state = ctx.author.voice

        if voice_state is not None:
            await voice_state.channel.connect()
        else:
            # Exiting if the user is not in a voice channel
            return await ctx.send('You need to be in a voice channel to use this command')

async def setup(bot):
    await bot.add_cog(Music(bot))