
from discord.ext import commands
import asyncio as ass
from bot import Bot
from cai import Cai
from colorama import init as colorama_init
from utils import config
from utils import logging
# ! NEEDED FOR PYTORCH TO WORK ON UBUNTU SERVER (DISCLOUD)!
# ! MUST BE PUT BEFORE "import torch"
import os
os.system('color') # Add colors to Terminal output
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
import torch

async def main():
  colorama_init(autoreset=True)
  logging.system_info()
  cai = await Cai.setup()
  bot = Bot(cai)
  async with bot:
    await bot.load_extensions()
    await bot.start(config.DISCORD_TOKEN)
    
if __name__=="__main__":
  ass.run(main())


