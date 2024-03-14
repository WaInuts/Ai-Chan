from discord.ext import tasks, commands
from discord.player import AudioSource
import discord

import sys
import itertools
import traceback
import asyncio
import websockets
import json
import time
from async_timeout import timeout
from functools import partial
import yt_dlp as youtube_dl
from collections import deque
from utils.helpers import send_pings, build_url
from utils import logging
from components import music_ui

from utils.config import LISTEN_MOE

#TODO: Fix bug where second song in queue stops playing midway/randomly? (need to do further testing)
#TODO: Add Spotify Support
ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # ipv6 addresses cause issues sometimes
    'embedthumbnail': True
}

ffmpegopts = {
    'before_options': "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.thumbnail = data.get('thumbnail')
        self.duration_string = data.get('duration_string')
        self.requester = data.get('requester')

        self.data = data

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, bot, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 
                    'requester': ctx.author, 
                    'title': data['title'],
                    'thumbnail': data['thumbnail'],
                    'duration_string': data['duration_string']}

        return cls(discord.FFmpegPCMAudio(source, **ffmpegopts), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpegopts), data=data, requester=requester)

# TODO: Fix Radio being True while queueing the next song
    # Potential fix: add data to song if it's from the radio or not to not rely on boolean and cause race conditions
# TODO: Make the now playing message more consistent
    # Potential fix: If source of song is radio, send a ping to recieve song data.
        # AKA delete infinite loop
class MusicPlayer(commands.Cog):
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.radio = False
        self.song_history = deque([], 25) # History of songs played

        self.np = None # Now playing message
        self.np_embed = None # Now playing embed
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())
        #ctx.bot.loop.create_task(self.toggle_radio_data())
        self.radio_data = None
        self.websocket = None
    
    async def enable_radio(self):
        """Starts a listen.moe stream and starts sending song data via WebSockets from them."""
        self.radio = True
        self.radio_data = self.bot.loop.create_task(self.radio_data_loop())
        await self.radio_data

    async def disable_radio(self):
        """Disables radio loop radio data loop."""
        self.radio = False
        if self.radio_data in asyncio.all_tasks():
            await self.websocket.close()
            self.radio_data.cancel()
    
    # async def toggle_radio_data(self):
    #     """Starts websocket that recieves song data if radio is playing, else closes it."""
    #     if self.radio_data in asyncio.all_tasks():
    #         self.radio_data.cancel()

    async def add_radio_song(self):
        """Puts listen.moe song in queue."""
        try:
            source = discord.FFmpegOpusAudio(source=LISTEN_MOE, **ffmpegopts)
        except Exception as err:
            logging.error(err, "listen.moe")
        
        await self.queue.put(source)
        
    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()
            if self.radio is True:
                await self.add_radio_song()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)
            
            if not isinstance(source, AudioSource):
                if not isinstance(source, YTDLSource):
                    # Source was probably a stream (not downloaded)
                    # So we should regather to prevent stream expiration
                    try:
                        source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                    except Exception as e:
                        await self._channel.send(f'There was an error processing your song.\n'
                                                f'```css\n[{e}]\n```')
                        continue
            
            # source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            if self.radio is False:
                embed = music_ui.now_playing(song_title=source['title'], song_url=source['webpage_url'], duration_string=source['duration_string'], source="Youtube", source_logo="https://1000logos.net/wp-content/uploads/2017/05/Red-YouTube-logo.png", requester=source.requester, thumbnail=source.thumbnail)
                self.np_embed = embed 

            self.np = await self._channel.send(embed=self.np_embed)
                
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    async def radio_data_loop(self):
        """Coroutine that uses WebSockets to receive song data from listen.moe"""
        uri = 'wss://listen.moe/gateway_v2'
        async with websockets.connect(uri, ping_interval=None) as websocket:
            self.websocket = websocket
            while True:
                data = json.loads(await websocket.recv())
                if data['op'] == 0:
                    heartbeat = data['d']['heartbeat'] / 1000
                    self.bot.loop.create_task(send_pings(websocket, heartbeat))
                elif data['op'] == 1:
                    await self.set_now_playing(data)

    async def get_song_data(self):
        """Get song data from listen.moe websocket."""
        uri = 'wss://listen.moe/gateway_v2'
        async with websockets.connect(uri, ping_interval=None) as websocket:
            self.websocket = websocket
            data = json.loads(await websocket.recv())
            if data['op'] == 0:
                heartbeat = data['d']['heartbeat'] / 1000
                self.bot.loop.create_task(send_pings(websocket, heartbeat))
            elif data['op'] == 1:
                await self.set_now_playing(data)

    async def set_now_playing(self, data):
        """Gets songtitle and artist an sets them for class from JSON response."""
        song_data = {
            'title' : data['d']['song']['title'],
            'artist' : data['d']['song']['artists'][0]['name'],
            'image' : data['d']['song']['artists'][0]['image'],
            'sources' : data['d']['song']['sources'],
            'duration' : data['d']['song']['duration'],
            'duration_string' : time.strftime("%M:%S", time.gmtime(int(data['d']['song']['duration'])))
        }

        # Create URL for Song
        try:
            songHeader = song_data['title'] + ' by ' + song_data['artist']
        except:
            songHeader = song_data['title']
            song_data['artist'] = ''

        logging.info(f'Radio Now Playing: {songHeader}', 'listen.moe')
        webpage_url = build_url('https://www.google.com', 'search', {'q' : songHeader})
        song_data['webpage_url'] = webpage_url

        # Push data to history
        self.song_history.appendleft(song_data)

        logging.info(song_data['webpage_url'])
        embed = music_ui.now_playing(song_title=song_data['title'], song_artist=song_data['artist'], song_url=webpage_url, duration_string=song_data['duration_string'], source="JP Radio", source_logo="https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/Flag_of_Japan.svg/1280px-Flag_of_Japan.svg.png", footer="listen.moe (c) 2024")
        self.np_embed = embed

        # embed = discord.Embed(title=f":notes: {song_data['title']} :notes:", description=f"by {song_data['artist']}\n\n[Song Link]({song_data['webpage_url']})")
        # embed.set_author(name="JP Radio", icon_url="https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/Flag_of_Japan.svg/1280px-Flag_of_Japan.svg.png")
        # embed.set_footer(text="listen.moe (c) 2024")

        # self.np = await self._channel.send(embed=embed)

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class RadioPlayer(commands.Cog):
    """A class which is assigned to each guild using the bot for the Radio.
    This class implements a loop, which allows for different guilds to listen to different radios
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    def __init__(self, ctx):
            self.bot = ctx.bot
            self._guild = ctx.guild
            self.next = asyncio.Event()

            self.np = None  # Now playing message
            self.volume = .5
            self.current = None

            ctx.bot.loop.create_task(self.radio_loop())
            ctx.bot.loop.create_task(self.song_data_loop(ctx))

    async def radio_loop(self):
        """Coroutine that plays music from listen.moe through Discord's voice client"""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear() # Block from RePlaying
        try:
            source = discord.FFmpegOpusAudio(source=LISTEN_MOE, **ffmpegopts)
        except Exception as err:
            logging.error(err, "listen.moe")
        
        source.volume = self.volume

        self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
        await self.next.wait()

        # Make sure the FFmpeg process is cleaned up.
        source.cleanup()

    async def song_data_loop(self, ctx):
        """Coroutine that uses WebSockets to receive song data from listen.moe"""
        uri = 'wss://listen.moe/gateway_v2'
        async with websockets.connect(uri, ping_interval=None) as websocket:
            while True:
                data = json.loads(await websocket.recv())
                if data['op'] == 0:
                    heartbeat = data['d']['heartbeat'] / 1000
                    self.bot.loop.create_task(send_pings(websocket, heartbeat))
                    # logging.info(f"{len(asyncio.all_tasks())}")
                elif data['op'] == 1:
                    await self._send_song_data(ctx, data)

    async def _send_song_data(self, ctx, data):
        """Gets songtitle and artist from JSON response."""
        songTitle = data['d']['song']['title']
        artist = data['d']['song']['artists'][0]['name']
        try:
            songHeader = songTitle + ' by ' + artist
        except:
            songHeader = songTitle
        logging.info(f'Radio Now Playing: {songHeader}', 'listen.moe')
        embed = discord.Embed(title=':notes: ' + songHeader + ' :notes:')
        await self._channel.send(embed=embed)

class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        # TODO: Change this to logging
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def is_running(self, task):
        """Checks if a task is running."""
        if task in asyncio.all_tasks():
            return True
        else:
            return False
        
    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]

        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.hybrid_command(name='connect', aliases=['join'])
    async def connect_(self, ctx):
        """Invite me to your voice channel!"""
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise InvalidVoiceChannel('No channel to join.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')
        embed = discord.Embed(title="Joined A Call")
        embed.add_field(name="Connected To :", value=channel, inline=True)

        await ctx.send(embed=embed)

    # TODO: Add Optional Parameter to select platform (once other platforms are added)
    @commands.hybrid_command(name='play', aliases=['sing', 'p'])
    async def play_(self, ctx, *, search: str):
        """Look up a song from one of our supported platforms!

        Parameters
        -----------
        search: str
            Can be a link or a search term
        """
        await ctx.typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)
        await player.disable_radio()

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(self.bot, ctx, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)   

        # Tell user the song's position in queue.
        queue_size = player.queue.qsize()
        embed = music_ui.queue_song(song_title=source['title'], song_url=source['webpage_url'], queue_size=queue_size, duration_string=source['duration_string'], requester=source['requester'].display_name, thumbnail=source['thumbnail'])

        # embed = discord.Embed(title=f"{source['title']}", 
        #                     description=f"\n`{source['duration_string']}`")
        # embed.set_author(name="Added to Queue ~")
        # embed.set_thumbnail(url='{}'.format(source['thumbnail']))
        # embed.set_footer(text='Will play soon!'if queue_size<=1 else f'Position #{queue_size}', icon_url='https://imgur.com/PKi66Gs.png')
        
        await ctx.send(embed=embed)


    @commands.hybrid_command(name='pause')
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!')
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f'**`{ctx.author.display_name}`**: Paused the song!')

    @commands.hybrid_command(name='resume', aliases=['unpause'])
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', )
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f'**`{ctx.author.display_name}`**: Resumed the song!')

    @commands.hybrid_command(name='skip')
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!')

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f'**`{ctx.author.display_name}`**: Skipped the song!')

    # TODO: Make this work with Radio in queue
    @commands.hybrid_command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!')

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('There are currently no more queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**{postiion+1}:** **`{_["title"]}`**' for postiion, _ in enumerate(upcoming))
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name='history', aliases=['h', 'radio_history'])
    async def history(self, ctx):
        """Retrieve a list of the last twenty played songs on the radio."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!')

        player = self.get_player(ctx)
        if len(player.song_history) == 0:
            return await ctx.send('There are currently no saved songs.')

        latest = player.song_history
        fmt = '\n'.join(f'**{postiion+1}:** [**`{_["title"]}`**]({_["webpage_url"]})' + f' by {_["artist"]}' if _["artist"] else '' for postiion, _ in enumerate(latest))
        embed = discord.Embed(title= f':notes: Last {len(latest)} Played Songs:' if (len(latest) > 1) else f':notes: Last Played Song:', description=fmt)
        embed.set_author(name=f"Song History")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', )

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(embed=player.np_embed)

    @commands.hybrid_command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', )

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        embed = discord.Embed(title="Volume Message",
        description=f'The Volume Was Changed By **{ctx.author.display_name}**')
        embed.add_field(name="Current Volume", value=vol, inline=True)
        await ctx.send(embed=embed)
        # await ctx.send(f'**`{ctx.author}`**: Set the volume to **{vol}%**')

    # TODO: Make Command have parameter to choose type of radio, ex. ./radio jp -> weeb music
    # TODO: Add JP as a choice (look at discordpy slash commands documentation)
    @commands.hybrid_command(name="radio")
    async def start_radio(self, ctx):
        """Radio that plays Japanese Pop Music 24/7."""
        # TODO: Add parameter that clears the queue and plays radio after
        # TODO: Add parameter that enables/disables np song data
        await ctx.typing()

        player = self.get_player(ctx)

        if player.radio is False:
            vc = ctx.voice_client

            if not vc:
                await ctx.invoke(self.connect_)

            if ctx.voice_client.is_playing():
                embed = discord.Embed(title="Queued Radio!", description="Will play after queue is empty!")
                embed.set_footer(text="To play immediately, do /radio again with 'Force' enabled!")
                logging.info("Song is Playing")
                await ctx.send(embed=embed)

            await player.enable_radio()
            # source = discord.FFmpegOpusAudio(source=LISTEN_MOE, **ffmpegopts)
            # await player.queue.put(source)

        else:
            await ctx.send(":cross_mark: Already playing/queued Radio!")

        # _next = asyncio.Event() # 
        # voice_channel = ctx.voice_client
        
        # if not voice_channel:
        #     await ctx.invoke(self.connect_)
        #     voice_channel = ctx.voice_client

        # radio = self.bot.loop.create_task(self.radio_loop(ctx, _next))
        # song_data = self.bot.loop.create_task(self.song_data_loop(ctx)) # Connect to listen.moe with websocket to keep recieving song data.

        # await radio
        # await song_data

    # async def radio_loop(self, ctx, _next):
    #     """Coroutine that plays music from listen.moe through Discord's voice client"""
    #     await self.bot.wait_until_ready()

    #     while not self.bot.is_closed():
    #         _next.clear()

    #         source = discord.FFmpegOpusAudio(source=LISTEN_MOE, **ffmpegopts)
    #         source.volume = .5

    #         ctx.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(_next.set))
    #         await _next.wait()

    #         # Make sure the FFmpeg process is cleaned up.
    #         source.cleanup()

    # async def song_data_loop(self, ctx):
    #     """Coroutine that uses WebSockets to receive song data from listen.moe"""
    #     uri = 'wss://listen.moe/gateway_v2'
    #     async with websockets.connect(uri, ping_interval=None) as websocket:
    #         while True:
    #             data = json.loads(await websocket.recv())
    #             if data['op'] == 0:
    #                 heartbeat = data['d']['heartbeat'] / 1000
    #                 self.bot.loop.create_task(send_pings(websocket, heartbeat))
    #                 # logging.info(f"{len(asyncio.all_tasks())}")
    #             elif data['op'] == 1:
    #                 await self._send_song_data(ctx, data)
                
    # async def _send_song_data(self, ctx, data):
    #     """Gets songtitle and artist from JSON response."""
    #     songTitle = data['d']['song']['title']
    #     artist = data['d']['song']['artists'][0]['name']
    #     try:
    #         songHeader = songTitle + ' by ' + artist
    #     except:
    #         songHeader = songTitle
    #     logging.info(f'Radio Now Playing: {songHeader}', 'listen.moe')
    #     embed = discord.Embed(title=':notes: ' + songHeader + ' :notes:')
    #     await ctx.send(embed=embed)

    @commands.hybrid_command(name='stop', aliases=['leave'])
    async def stop_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!')

        embed = discord.Embed(description='**Disconnected From Voice Channel!**')
        await ctx.send(embed=embed)
        await vc.disconnect()
        await self.cleanup(ctx.guild)

async def setup(bot):
    await bot.add_cog(Music(bot))