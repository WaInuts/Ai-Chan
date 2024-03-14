import discord
from utils import logging

def queue_song(queue_size=0, song_title="Song Title", song_artist="", song_url="", duration_string="", requester="You", thumbnail=""):
    """Creates embed with the song data and queue postion."""
    embed = discord.Embed(title=f"{song_title}", description= f"by {song_artist}" if song_artist else "" + f"\n`{duration_string}`\n\n[Song Link]({song_url})", )
    embed.set_author(name=f"@{requester} Added to Queue ~", icon_url="https://images.emojiterra.com/google/noto-emoji/unicode-15/color/512px/1f338.png")
    embed.set_thumbnail(url=f'{thumbnail}')
    embed.set_footer(text='Will play soon!'if queue_size<=1 else f'Position #{queue_size}', icon_url='https://imgur.com/PKi66Gs.png')
    return embed

def now_playing(song_title="Song Title", song_artist="", song_url="", duration_string="", source="Song", source_logo="", requester="", footer="", thumbnail=""):
    logging.info(song_url)
    """Creates embed with the currently playing song's data."""
    embed = discord.Embed(title=f":notes: {song_title} :notes:", description= (f"by {song_artist}" if song_artist else "") + f"\n`{duration_string}`\n\n[Song Link]({song_url})", )
    embed.set_author(name=f"{source}", icon_url=source_logo)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text=f"Requested by: @{requester}" if requester else footer)
    return embed   