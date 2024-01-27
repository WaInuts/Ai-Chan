
from discord.ext import commands
import asyncio
import sys
from bot import Bot
from cai import Cai
from utils import config

print(f'Using Python {sys.version}')
print(f'{sys.platform}')

async def main():
    cai = await Cai.setup()
    bot = Bot(cai)
    async with bot:
      await bot.load_extensions()
      await bot.start(config.DISCORD_TOKEN)
  
if __name__=="__main__":
  asyncio.run(main())


