
from discord.ext import commands
import discord
from utils.keep_alive import keep_alive
import os
import asyncio
from bot import Bot
from cai import Cai
from utils import config


async def main():
    cai = await Cai.setup()
    bot = Bot(cai)
    async with bot:
      await bot.load_extensions()
      await bot.start(config.DISCORD_TOKEN)
  
if __name__=="__main__":
  asyncio.run(main())


