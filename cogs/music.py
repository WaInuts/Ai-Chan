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
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import deque
from utils.helpers import send_pings, build_url
from utils import logging
from components import system_ui, music_ui

from utils.config import LISTEN_MOE

# TODO: Fix bug where second song in queue stops playing midway/randomly? (need to do further testing) (only happens on the server)
# TODO: Add Spotify Support
ytdlopts = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # ipv6 addresses cause issues sometimes
    "embedthumbnail": True,
}

ffmpegopts = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl = youtube_dl.YoutubeDL(ytdlopts)
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class SongSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get("title")
        self.artist = data.get("artist")
        self.web_url = data.get("webpage_url")
        self.thumbnail = data.get("thumbnail")
        self.duration_string = data.get("duration_string")
        self.platform = data.get("platform")
        self.requester = data.get("requester")

        self.data = data

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def get_user_audio_source(cls, bot, ctx, query: str, *, loop, download=False):
        "Gets AudioSource from Youtube or Spotify."
        title = ""
        artists = ""
        webpage_url = ""
        platform = "Spotify"

        if (
            "https://open.spotify.com/track" in query
            or "open.spotify.com/track" in query
        ):
            try:
                result = spotify.track(query)
                title = result["name"]
                artists_data = result["artists"]
                artists = [artist["name"] for artist in artists_data]
                artists = ",".join(str(artist) for artist in artists)
                webpage_url = result["external_urls"]["spotify"]
                logging.info(result)
                logging.info(title)
                logging.info(artists_data)
                logging.info(artists)
                query = f"{title} by {artists}"
                await ctx.send(query)
            except Exception as err:
                logging.error(err, "SongSource")
                await ctx.send(
                    f"There was an error getting the song! <:HuTao_DED:1187215483729092619>\n\n`{err}"
                )
                return None
        elif "https://youtu" in query or "youtube.com" in query:
            platform = "Youtube"
        else:
            try:
                results = spotify.search(query)
                title = results["tracks"]["items"][0]["name"]
                artists_data = results["tracks"]["items"][0]["artists"]
                artists = [artist["name"] for artist in artists_data]
                artists = ",".join(str(artist) for artist in artists)
                webpage_url = results["tracks"]["items"][0]["external_urls"]["spotify"]
                logging.info(results)
                logging.info(title)
                logging.info(artists_data)
                logging.info(artists)
                query = f"{title} by {artists}"
                await ctx.send(query)
            except Exception as err:
                logging.error(err, "SongSource")
                await ctx.send(
                    f"There was an error getting the song! <:HuTao_DED:1187215483729092619>\n\n`{err}"
                )
                return None
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=query, download=download)
        data = await loop.run_in_executor(None, to_run)

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        if download:
            source = ytdl.prepare_filename(data)
        else:
            song_data = {
                "artist": artists,  # TODO: refactor 'artist' to 'artists'
                "webpage_url": webpage_url if webpage_url else data["webpage_url"],
                "youtube_url": data["webpage_url"],
                "requester": ctx.author,
                "title": title if title else data["title"],
                "thumbnail": data["thumbnail"],
                "duration_string": data["duration_string"],
                "platform": platform,
            }
            # cls.data = song_data
            return song_data

        return cls(
            discord.FFmpegPCMAudio(source, **ffmpegopts),
            data=data,
            requester=ctx.author,
        )

    @classmethod
    async def create_YTDL_source(cls, bot, ctx, query: str, *, loop, download=False):
        "Creates an AudioSource from Youtube."
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=query, download=download)
        data = await loop.run_in_executor(None, to_run)

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        if download:
            source = ytdl.prepare_filename(data)
        else:
            song_data = {
                "webpage_url": data["webpage_url"],
                "requester": ctx.author,
                "title": data["title"],
                "thumbnail": data["thumbnail"],
                "duration_string": data["duration_string"],
                "platform": "Youtube",
            }
            # cls.data = song_data
            return song_data

        return cls(
            discord.FFmpegPCMAudio(source, **ffmpegopts),
            data=data,
            requester=ctx.author,
        )

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data["requester"]
        platform = data["platform"]
        # TODO: Refactor platform as class return variable instead of dict argument (similar to how "request" is done here by OG programmer)
        title = data["title"]
        artists = data["artist"]
        webpage_url = data["webpage_url"]

        to_run = partial(ytdl.extract_info, url=data["youtube_url"], download=False)
        data = await loop.run_in_executor(None, to_run)
        data["platform"] = platform
        data["title"] = title
        data["artist"] = artists
        data["webpage_url"] = webpage_url

        # cls.data = data

        return cls(
            discord.FFmpegPCMAudio(data["url"], **ffmpegopts),
            data=data,
            requester=requester,
        )

    @classmethod
    async def create_listen_moe_source(cls, bot, ctx):
        """Get song data from listen.moe websocket and creates an AudioSource."""
        uri = "wss://listen.moe/gateway_v2"
        requester = ctx.author
        async with websockets.connect(uri, ping_interval=None) as websocket:
            response = json.loads(await websocket.recv())
            while True:
                response = json.loads(await websocket.recv())
                if response["op"] == 0:
                    heartbeat = response["d"]["heartbeat"] / 1000
                    bot.loop.create_task(send_pings(websocket, heartbeat))
                elif response["op"] == 1:
                    song_data = cls.decode_song_data(cls, response)
                    break

        try:
            source = discord.FFmpegPCMAudio(source=LISTEN_MOE, **ffmpegopts)
        except Exception as err:
            logging.error(err, "listen.moe")

        return cls(source, data=song_data, requester=requester)

    def decode_song_data(cls, data):
        """Gets songtitle and artist an sets them for class from JSON response."""
        song_data = {
            "title": data["d"]["song"]["title"],
            "artist": data["d"]["song"]["artists"][0]["name"],
            "image": data["d"]["song"]["artists"][0]["image"],
            "sources": data["d"]["song"]["sources"],
            "duration": data["d"]["song"]["duration"],
            "duration_string": time.strftime(
                "%M:%S", time.gmtime(int(data["d"]["song"]["duration"]))
            ),
            "platform": "listen.moe",
        }

        # Create URL for Song
        try:
            songHeader = song_data["title"] + " by " + song_data["artist"]
        except:
            songHeader = song_data["title"]
            song_data["artist"] = ""

        logging.info(f"Radio Now Playing: {songHeader}", "listen.moe")
        webpage_url = build_url("https://www.google.com", "query", {"q": songHeader})
        song_data["webpage_url"] = webpage_url

        # return data
        cls.data = song_data
        return song_data


class MusicPlayer(commands.Cog):
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = (
        "bot",
        "_guild",
        "_channel",
        "_cog",
        "queue",
        "next",
        "current",
        "np",
        "volume",
    )

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.songs_data = (
            list()
        )  # Stores songs data for song removal and queue info since queues are not random access

        self.radio = False
        self.radio_is_running = False
        self.song_history = deque([], 25)  # History of songs played
        self.queued_user_song = False

        self.np = None  # Now playing message
        self.np_embed = None  # Now playing embed
        self.volume = 0.5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())
        self.radio_data = None
        self.websocket = None

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            # Check if
            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue_get()  # Get AudioSource + song + data
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            # Got song from Queue so this is now...
            self.queued_user_song = False

            if source:  # If song was not removed...
                if source["platform"] == "listen.moe":
                    # AudioSource is from listen.moe
                    # Update AudioSource so it gets the link for the latest song and not the saved one from the queue
                    # (prevents duplicate song links and starting at halfway point of a song)
                    try:
                        source = await SongSource.create_listen_moe_source(
                            self.bot, self.ctx
                        )
                    except Exception as err:
                        logging.error(err, "listen.moe")
                else:
                    # AudioSource is not from listen.moe, so Radio is no longer running.
                    self.radio_is_running = False

                if not isinstance(source, SongSource):
                    # AudioSource was probably a stream (not downloaded)
                    # So we should regather to prevent stream expiration
                    try:
                        source = await SongSource.regather_stream(
                            source, loop=self.bot.loop
                        )
                    except Exception as e:
                        await self._channel.send(
                            f"There was an error processing your song.\n"
                            f"```css\n[{e}]\n```"
                        )
                        continue

                source.volume = self.volume
                self.current = source

                self._guild.voice_client.play(
                    source,
                    # Once song is finished, resume the thread.
                    after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set),
                )

                # Create and send embed message with song data.
                embed = music_ui.now_playing(
                    song_title=source["title"],
                    song_artist=source["artist"],
                    song_url=source["web_url"],
                    duration_string=source["duration_string"],
                    platform=source["platform"],
                    requester=source["requester"],
                    thumbnail=source["thumbnail"],
                )
                self.np_embed = embed

                self.np = await self._channel.send(embed=self.np_embed)

                # Wait until self.next.set is called...
                await self.next.wait()

                self.song_history.append(source)

                # If song was from listen.moe, add another listen.moe song to continue the radio loop.
                # Will not do it if a user requested song is queued.
                if source["platform"] == "listen.moe" and not self.queued_user_song:
                    new_source = await SongSource.create_listen_moe_source(
                        self.bot, self.ctx
                    )
                    await self.queue_put(new_source)

                # Make sure the FFmpeg process is cleaned up.
                source.cleanup()
                self.current = None

                try:
                    # We are no longer playing this song...
                    await self.np.delete()
                except discord.HTTPException:
                    pass

    async def queue_put(self, data):
        """Gets item from queue and song data list."""
        await self.queue.put(data)
        self.songs_data.append(data)

    async def queue_get(self):
        """Pops item from queue and song data list. Checks if song was removed from queue."""
        source = await self.queue.get()
        try:
            song_data = self.songs_data[0]
        except IndexError:
            logging.info("No more songs in queue!", "discord.MusicPlayer")
            # remove song
            source = None
            return source
        except Exception as err:
            logging.info(err, "discord.MusicPlayer")

        # Check if song was removed
        if source["title"] != song_data["title"]:
            # remove song
            source = None
        else:
            # If titles match, remove title from songs_data list.
            self.songs_data.pop(0)

        return source

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ("bot", "players")

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

    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(
                    "This command can not be used in Private Messages."
                )
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            embed = system_ui.error(
                "Error connecting to Voice Channel!\n\nPlease make sure you are in a valid channel or provide me with one baka!"
            )
            await ctx.send(embed=embed)

        # TODO: Change this to logging
        print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

    async def _is_running(self, task):
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

    @commands.hybrid_command(name="connect", aliases=["join"])
    async def connect_(self, ctx):
        """Invite me to your voice channel!"""
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise InvalidVoiceChannel("No channel to join.")

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f"Moving to channel: <{channel}> timed out.")
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(
                    f"Connecting to channel: <{channel}> timed out."
                )
        embed = discord.Embed(title="Joined A Call")
        embed.add_field(name="Connected To :", value=channel, inline=True)

        await ctx.send(embed=embed)

    # TODO: Add Optional Parameter to select platform (once other platforms are added)
    @commands.hybrid_command(name="play", aliases=["sing", "p"])
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

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await SongSource.get_user_audio_source(
            self.bot, ctx, search, loop=self.bot.loop, download=False
        )

        if source:
            await player.queue_put(source)

            player.queued_user_song = True

            # Tell user the song's position in queue.
            queue_size = player.queue.qsize()
            embed = music_ui.queue_song(
                song_title=source["title"],
                song_url=source["webpage_url"],
                queue_size=queue_size,
                duration_string=source["duration_string"],
                requester=source["requester"].display_name,
                thumbnail=source["thumbnail"],
                platform=source["platform"],
            )

            await ctx.send(embed=embed)

    # TODO: Make Command have parameter to choose type of radio, ex. ./radio jp -> weeb music
    # TODO: Add JP as a choice (look at discordpy slash commands documentation)
    @commands.hybrid_command(name="radio")
    async def start_radio(self, ctx, force: bool = False):
        """Radio that plays Japanese Pop Music 24/7.

        Parameters
        -----------
        force: bool
            Stop current song and play the Radio.
        """
        # TODO: Add parameter that clears the queue and plays radio after
        # TODO: Add parameter that enables/disables np song data
        await ctx.typing()

        player = self.get_player(ctx)

        vc = ctx.voice_client
        color_data = music_ui.get_platform_colors("listen.moe")
        color = color_data["color"]

        if not vc:
            await ctx.invoke(self.connect_)

        if force:
            await ctx.invoke(self.queue_clear)
            vc.stop()

        if player.current != None:
            if player.current.platform == "listen.moe" or player.radio_is_running:
                await ctx.send(":cross_mark: Already playing/queued Radio!")
                return
            else:
                if not force:
                    embed = discord.Embed(
                        title="Queued Radio!",
                        description="Will play after queue is empty!",
                        color=color,
                    )
                    embed.set_footer(
                        text="To play immediately, do /radio again with 'Force' enabled!"
                    )
                    await ctx.send(embed=embed)

        player.radio_is_running = True

        source = await SongSource.create_listen_moe_source(self.bot, ctx)

        await player.queue_put(source)

    @commands.hybrid_command(name="pause")
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send("I am not currently playing anything!")
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f"**`{ctx.author.display_name}`**: Paused the song!")

    @commands.hybrid_command(name="resume", aliases=["unpause"])
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently playing anything!",
            )
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f"**`{ctx.author.display_name}`**: Resumed the song!")

    @commands.hybrid_command(name="skip")
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently playing anything!")

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()

        await ctx.send(f"**`{ctx.author.display_name}`**: Skipped the song!")

    @commands.hybrid_command(name="remove", aliases=["d", "delete"])
    async def remove_(self, ctx, position: int):
        """Remove a song from the queue.

        Parameters
        -----------
        position: int
            Position of song that will be removed.
        """
        position -= 1

        player = self.get_player(ctx)

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently playing anything!")

        try:
            song_data = player.songs_data[position]
            del player.songs_data[position]
        except IndexError:
            if player.songs_data:
                logging.info("List index out of range!", "discord.Music")
                return await ctx.send(
                    f":cross_mark: Song title or position does not exist!"
                )
            else:
                logging.info("Queue is empty!", "discord.Music")
                return await ctx.send(
                    f"The Queue is Empty... <:hutaodumbomoebay:1187257013869232189>"
                )
        except Exception as err:
            logging.error(err, "discord.Music")
            return await ctx.send(f":cross_mark: An Error Occured!\n\n`{err}`")

        return await ctx.send(f"Removed {song_data['title']} at position {position}!")

    @commands.hybrid_command(name="queue", aliases=["q", "playlist"])
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently connected to voice!")

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send("There are currently no more queued songs.")

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.songs_data, 0, 5))

        fmt = "\n".join(
            f'**{postiion+1}:** **`{_["title"]}`**'
            for postiion, _ in enumerate(upcoming)
        )
        embed = discord.Embed(title=f"Upcoming - Next {len(upcoming)}", description=fmt)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="history", aliases=["h", "radio_history"])
    async def history(self, ctx):
        """Retrieve a list of the last twenty played songs on the radio."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently connected to voice!")

        player = self.get_player(ctx)
        if len(player.song_history) == 0:
            return await ctx.send("There are currently no saved songs.")

        latest = player.song_history
        fmt = "\n".join(
            f'**{postiion+1}:** [**`{_["title"]}`**]({_["web_url"]})'
            + (f' by {_["artist"]}' if _["artist"] else "")
            for postiion, _ in enumerate(latest)
        )
        embed = discord.Embed(
            title=(
                f":notes: Last {len(latest)} Played Songs:"
                if (len(latest) > 1)
                else f":notes: Last Played Song:"
            ),
            description=fmt,
        )
        embed.set_author(name=f"Song History")
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="now_playing", aliases=["np", "current", "currentsong", "playing"]
    )
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!",
            )

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send("I am not currently playing anything!")

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(embed=player.np_embed)

    @commands.hybrid_command(name="volume", aliases=["vol"])
    async def change_volume(self, ctx, *, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(
                "I am not currently connected to voice!",
            )

        if not 0 < vol < 101:
            return await ctx.send("Please enter a value between 1 and 100.")

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        embed = discord.Embed(
            title="Volume Message",
            description=f"The Volume Was Changed By **{ctx.author.display_name}**",
        )
        embed.add_field(name="Current Volume", value=vol, inline=True)
        await ctx.send(embed=embed)
        # await ctx.send(f'**`{ctx.author}`**: Set the volume to **{vol}%**')

    @commands.hybrid_command(
        name="clear", aliases=["empty", "remove_all", "delete_all"]
    )
    async def queue_clear(self, ctx):
        """Removes every song from the queue."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently connected to voice!")

        player = self.get_player(ctx)
        if not player.songs_data:
            return await ctx.send("There are currently no more queued songs.")

        # while not player.queue.empty():
        #     player.queue.get_nowait()
        #     player.queue.task_done()

        player.songs_data.clear()

        return await ctx.send("Cleared the queue!")

    @commands.hybrid_command(name="stop", aliases=["leave"])
    async def stop_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send("I am not currently playing anything!")

        embed = discord.Embed(description="**Disconnected From Voice Channel!**")
        await ctx.send(embed=embed)
        await vc.disconnect()
        await self.cleanup(ctx.guild)


async def setup(bot):
    await bot.add_cog(Music(bot))
