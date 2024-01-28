
from discord.ext import commands
import asyncio
import sys
import platform
from bot import Bot
from cai import Cai
from utils import config
# ! NEEDED FOR PYTORCH TO WORK ON UBUNTU SERVER (DISCLOUD)!
# ! MUST BE PUT BEFORE "import torch"
import os
os.environ['OPENBLAS_NUM_THREADS'] = '4'
import torch


print(f'Using Python {sys.version}')
print(platform.system())
print(platform.release())
print(platform.version())
print(platform.machine())
print("Number of cpu threads: {}".format(torch.get_num_threads()))

async def main():
    cai = await Cai.setup()
    bot = Bot(cai)
    async with bot:
      await bot.load_extensions()
      await bot.start(config.DISCORD_TOKEN)
  
if __name__=="__main__":
  asyncio.run(main())


