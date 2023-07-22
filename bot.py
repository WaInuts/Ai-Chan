from discord.ext import commands
import discord

from utils import config
import random
import os

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.prefix, 
            activity=config.starting_activity, 
            intents=discord.Intents.all(), 
            help_command=None,
        )

    async def load_extensions(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
    

