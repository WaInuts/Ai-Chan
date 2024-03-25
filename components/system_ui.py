"""UI For User Error, Info, and Warnings."""

import discord
from utils import logging, colors


def warning(error: str, code: str = ""):
    embed = discord.Embed(color=int(colors.HUTAO_RED, 16))
    embed.set_author(
        name="Something went wrong!", icon_url="https://imgur.com/tAdD5wI.png"
    )
    embed.description = f">>> :cross_mark: {error}\n\n" + (f"`{code}`" if code else "")

    return embed


def error(error: str, code: str = ""):
    embed = discord.Embed(color=int(colors.HUTAO_RED, 16))
    embed.set_author(
        name="Something went wrong!", icon_url="https://imgur.com/tAdD5wI.png"
    )
    embed.description = f">>> :cross_mark: {error}\n\n" + (f"`{code}`" if code else "")

    return embed
