
from discord.ext import commands
import asyncio
import sys
import platform
from bot import Bot
from cai import Cai
from utils import config
import torch
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'

print(f'Using Python {sys.version}')
print(platform.system())
print(platform.release())
print(platform.version())
print(platform.machine())
#print("Number of cpu threads: {}".format(torch.get_num_threads()))

async def main():
    print('Main...')
    cai = await Cai.setup()
    print('CAI...')
    bot = Bot(cai)
    print('Bot...')
    async with bot:
      await bot.load_extensions()
      print('Load_Extensions...')
      await bot.start(config.DISCORD_TOKEN)
    print('Main Finished!')
  
if __name__=="__main__":
  asyncio.run(main())


