from discord.ext import commands
import discord

import yt_dlp as youtube_dl
import discord
import os
import requests
import asyncio
import json
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
    'max_filesize' : 100000000, # bytes
    # 'writethumbnail': True,
    'embedthumbnail': True,
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# TODO
# listen for status of bot's voice state to update voice client accordingly
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        
        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.thumbnail = data.get('thumbnail')
        self.duration_string = data.get('duration_string')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        print(url)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        #print(json.dumps(ytdl.sanitize_info(data)))
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
            firstItemData = data['entries'][0]['original_url']
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(firstItemData, download=not stream))

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
            channel = ctx.message.author.voice.channel
            return await channel.connect()
        elif ctx.voice_client is not None:
            return ctx.voice_client
            # Exiting if the user is already in a voice channel
        else:
            await ctx.send('<:PD_hutao:1187216515477540945> You aren\'t in a voice channel.')
            return False
            # Exiting if the user is not in a voice channel
        
    @commands.command()
    async def leavevoice(self, ctx):
        if(ctx.voice_client):
            await ctx.guild.voice_client.disconnect()
            await ctx.send("Leaving Voice Channel...")
        else:
            await ctx.send("I'm not in a Voice Channel!")
        
    @commands.command()    
    async def play(self, ctx, *, url):
        vc = await self.joinvoice(ctx)
        if vc is False: return

        async with ctx.typing():
            
            # get audio source of requested url
            try:
                player = await YTDLSource.from_url(url, loop=self.loop)
                print(player)
                print(player.title)
            except MaxFileException:
                await ctx.send('Failed to play <:gi_hutao_notlikethis:1187215478083563662> Max file size is {} MB!' \
                               .format(ytdl_format_options['max_filesize'] / 10**6))
                return

            # play audio source through bot
            try: 
                vc.play(player, after= lambda e: print('Player error: %s'  % e) if e
                         else asyncio.run(self.after_play(ctx)))
            except discord.ClientException:
                # playlist.append(player.url)
                print('queued')
                print(player.title)
                queueEmbed = discord.Embed(title="Added to Queue! <:HuTao_GotThis:1187259987291021352> ", 
                                    description=f'{player.title}\n `{player.duration_string}`')
                queueEmbed.set_thumbnail(url='{}'.format(player.thumbnail))
                queueEmbed.set_footer(text= 'Will play after the current song!'if len(playlist)<3 else f'Position #{len(playlist)}')

                await ctx.send(embed=queueEmbed)
                # await ctx.send('Added to queue: {}'.format(player.title))
                return

        embed = discord.Embed(title="<a:hutao_dance:1187215482844098641> Now Playing <a:hutao_dance:1187215482844098641>", 
                              description=f'{player.title}\n`{player.duration_string}`\n\nRequested by: {ctx.message.author.mention}')
        embed.set_thumbnail(url='{}'.format(player.thumbnail))

        await ctx.send(embed=embed)

    async def after_play(self, ctx):
        if len(playlist) > 0:
            playlist.pop(0)
            print("after_play")
            ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print(ROOT_DIR)
            # await self.play(ctx, playlist[0])
            server = ctx.message.channel
            voice_channel = ctx.message.guild.voice_client
            player = await YTDLSource.from_url(playlist[0], loop=self.loop)
            voice_channel.play(player, after=lambda e: asyncio.run(self.after_play(ctx)))
            embed = discord.Embed(title="<a:hutao_dance:1187215482844098641> Now Playing <a:hutao_dance:1187215482844098641>", 
                                description=f'{player.title}\n`{player.duration_string}`\n\nRequested by: {ctx.message.author.mention}')
            embed.set_thumbnail(url='{}'.format(player.thumbnail))
            # To Fix: "RuntimeError: Timeout context manager should be used inside a task" 
            asyncio.run_coroutine_threadsafe(ctx.send(embed=embed), self.bot.loop)
    
    async def delete_song():
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(ROOT_DIR)
        print('Song Deleted.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.bot.user.id:
            return

        elif before.channel is None:
            channel = member.guild.system_channel
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 300:
                    embed = discord.Embed(title="Disconnected due to inactivity!")
                    embed.set_image(url='https://imgur.com/3IJvykn.png')
                    await channel.send(embed=embed)
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    @commands.command()
    async def playingaudio(self, ctx, msg = ':arrow_forward: **Playing Audio!**', imageURL = 'https://imgur.com/Ptd2Xxc.gif'):
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            embed = discord.Embed(title=msg)
            embed.set_image(url=imageURL)
            await ctx.reply(embed=embed)
            return True
        else:
            await ctx.reply("**Nothing is Playing...**", "https://imgur.com/3IJvykn.png")
            return False
    
    @commands.command()
    async def pause(self, ctx):
        if await self.playingaudio(ctx, ':pause_button: **Pausing Song...**', 'https://imgur.com/5J2YtXV.png'):
            await ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        if await self.playingaudio(ctx, ':arrow_forward: **Resuming Song!**', 'https://imgur.com/Ptd2Xxc.gif'):
            await ctx.voice_client.resume()
        
    @commands.command()
    async def stop(self, ctx):
        if await self.playingaudio(ctx, ':stop_button: **Stopping Song.**', 'https://imgur.com/3IJvykn.png'):
            await ctx.voice_client.stop()

    @commands.command()
    async def skip(self, ctx):
        if await self.playingaudio(ctx, ':fast_forward: **Skipping Song!**', 'https://imgur.com/7NVmyh2.png') and len(playlist) >= 0:
            await ctx.voice_client.stop()
            # await ctx.invoke(self.bot.get_command('play'))
            await self.after_play(ctx)
    
    @commands.command()
    async def clearq(self, ctx):
        if len(playlist) > 0:
            await ctx.reply('**Clearing Queue!** <:hutaodumbomoebay:1187257013869232189>')
            playlist.clear()
        return

    @commands.command()
    async def listq(self, ctx):
        if len(playlist) > 0:
            await ctx.send('**Currently in Queue**: {} '.format(playlist))
        else:
            embed = discord.Embed(title='**Nothing in Queue!**')
            embed.set_image(url='https://imgur.com/3IJvykn.png')
            await ctx.reply(embed=embed)

    @commands.command()
    async def sing(self, ctx):
        try:
            if ctx.voice_client.is_playing():

                await ctx.send(':arrow_forward: **Playing Audio!**')
            else:
                embed = discord.Embed(title=':musical_note: **Hope you enjoy!~** :musical_note:')
                embed.set_image(url='https://imgur.com/iYZeeZd.png')
                await ctx.send(embed=embed)
                await ctx.invoke(self.bot.get_command('play'), url='https://youtube.com/playlist?list=PLdGAH7P9YXly2QO_Mpx_fmsBleDynSqGC&si=ko4vIy0kAKOLUsD3')

        except:
            embed = discord.Embed(title=':musical_note: **Hope you enjoy!~** :musical_note:')
            embed.set_image(url='https://imgur.com/iYZeeZd.png')
            await ctx.send(embed=embed)
            await ctx.invoke(self.bot.get_command('play'), url='https://youtube.com/playlist?list=PLdGAH7P9YXly2QO_Mpx_fmsBleDynSqGC&si=ko4vIy0kAKOLUsD3')

async def setup(bot):
    await bot.add_cog(Music(bot))

