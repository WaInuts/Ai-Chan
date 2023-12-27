from discord.ext import commands
import logging
import asyncio
from characterai import PyAsyncCAI
from utils import config

class listeners(commands.Cog):
    def __init__(self, bot, cai):
        self.bot = bot
        self.cai = cai
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self.bot))

    @commands.Cog.listener()
    async def on_message(self, message):

        if self.bot.user in message.mentions:
            async with message.channel.typing():
                async with self.cai.client.connect(config.CHARACTER_AI_TOKEN) as chat2:
                    data = await chat2.send_message(self.cai.char, self.cai.chat_id, message.content, self.cai.author)
                text = data['turn']['candidates'][0]['raw_content']
                print(text)
            await message.channel.send(f"{text}")
