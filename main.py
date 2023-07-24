
from discord.ext import commands
import discord
from utils.keep_alive import keep_alive
import os
import asyncio
from bot import Bot
from utils import config


async def main():
    bot = Bot()
    async with bot:
        await bot.load_extensions()
        await bot.start(config.TOKEN)

if __name__=="__main__":
  asyncio.run(main())


