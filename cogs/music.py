from discord.ext import commands
import discord

import yt_dlp as youtube_dl
import discord
import requests
import asyncio
import random

playlist = []

class MaxFileException(Exception):
    def __init__(self):
       pass

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    # 'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'max_filesize' : 5000000 # bytes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# TODO
# listen for status of bot's voice state to update voice client accordingly
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

        # for individual videos
        if url not in playlist and 'entries' not in data:
            playlist.append(url)
        
        # for playlist
        if 'entries' in data:
            for entry in data['entries']:
                playlist.append(entry['original_url'])

            # if shuffle == 'true':
            #     playlist = random.shuffle(playlist)

            # take first item data from a playlist
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(playlist[0], download=not stream))

        if data['filesize'] > ytdl_format_options['max_filesize']:
            raise MaxFileException()

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.loop = {}
        self.queue = {}

    @commands.command()
    async def joinvoice(self, ctx):
        voice_state = ctx.author.voice

        if voice_state and ctx.voice_client is None:
            return await voice_state.channel.connect()
        elif ctx.voice_client is not None:
            return ctx.voice_client
            # Exiting if the user is already in a voice channel
        else:
            await ctx.send('You need to be in a voice channel to use this command.')
            return False
            # Exiting if the user is not in a voice channel
        
    @commands.command()    
    async def play(self, ctx, url):
        vc = await self.joinvoice(ctx)
        if vc is False: return

        async with ctx.typing():
            
            # get audio source of requested url
            try:
                player = await YTDLSource.from_url(url, loop=self.loop)
            except MaxFileException:
                await ctx.send('Failed to play: Max file size is {} MB' \
                               .format(ytdl_format_options['max_filesize'] / 10**6))
                return

            # play audio source through bot
            try: 
                vc.play(player, after= lambda e: print('Player error: %s'  % e) if e
                         else asyncio.run(self.after_play(ctx)))
            except discord.ClientException:
                # playlist.append(player.url)
                await ctx.send('Added to queue: {}'.format(player.title))
                return

        await ctx.send('Now playing: {}'.format(player.title))

    async def after_play(self, ctx):
        playlist.pop(0)
        # await self.play(ctx, playlist[0])
        server = ctx.message.guild
        voice_channel = server.voice_client
        player = await YTDLSource.from_url(playlist[0], loop=self.loop)
        voice_channel.play(player, after=lambda e: asyncio.run(self.after_play(ctx)))
        await server.send('Now playing: {}'.format(player.title))
    
    @commands.command()
    async def playingaudio(self, ctx, msg = 'Playing audio :)'):
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await ctx.reply(msg)
            return True
        else:
            await ctx.reply("Nothing is playing")
            return False
    
    @commands.command()
    async def pause(self, ctx):
        if await self.playingaudio(ctx, 'Pausing song'):
            await ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        if await self.playingaudio(ctx, 'Resuming song'):
            await ctx.voice_client.resume()
        
    @commands.command()
    async def stop(self, ctx):
        if await self.playingaudio(ctx, 'Stopping song'):
            await ctx.voice_client.stop()

    @commands.command()
    async def skip(self, ctx):
        if await self.playingaudio(ctx, 'Skipping song') and len(playlist) >= 0:
            await ctx.voice_client.stop()
            await self.after_play(ctx)
    
    @commands.command()
    async def clearq(self, ctx):
        if len(playlist) > 0:
            await ctx.reply('Clearing queue!')
            playlist.clear()
        return

    @commands.command()
    async def listq(self, ctx):
        if len(playlist) > 0:
            await ctx.send('Currently in queue: {} '.format(playlist))
        else:
            await ctx.reply('Nothing in queue!')

    @commands.command()
    async def sing(self, ctx):
        try:
            if ctx.voice_client.is_playing():
                await ctx.send('Audio currently playing!')
            else:
                await ctx.send('Hope you enjoy! ;)')
                await self.play(ctx, 'https://youtube.com/playlist?list=PLdGAH7P9YXly2QO_Mpx_fmsBleDynSqGC&si=ko4vIy0kAKOLUsD3')
        except:
            await ctx.send('Hope you enjoy! ;)')
            await self.play(ctx, 'https://youtube.com/playlist?list=PLdGAH7P9YXly2QO_Mpx_fmsBleDynSqGC&si=ko4vIy0kAKOLUsD3')

async def setup(bot):
    await bot.add_cog(Music(bot))

