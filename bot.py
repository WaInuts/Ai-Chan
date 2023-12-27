from discord.ext import commands
import discord

from utils import config
import random
import os
from cogs import listeners

discord.utils.setup_logging()

class Bot(commands.Bot):
    def __init__(self, cai):
        super().__init__(
            command_prefix=config.prefix, 
            activity=config.starting_activity, 
            intents=discord.Intents.all(), 
            help_command=None,
        )
        self.cai = cai

    async def load_extensions(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith(('__', 'listeners')):
                await self.load_extension(f"cogs.{filename[:-3]}")
            elif filename.startswith('listeners'):
                await self.add_cog(listeners.listeners(self, self.cai))
    

