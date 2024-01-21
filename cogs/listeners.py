from discord.ext import commands
import discord
import logging
import asyncio
import re
from characterai import PyAsyncCAI
from utils import config

from utils.voice import text_to_speech

class listeners(commands.Cog):
    def __init__(self, bot, cai):
        self.bot = bot
        self.cai = cai
    
    description = "To talk to Hu Tao, @Hu Tao with your message!"
    @commands.Cog.listener()
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self.bot))
    
    #TODO: recaterogize to AI cog
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user in message.mentions:
            ctx = await self.bot.get_context(message)

            # Format Message for CharacterAI:
            # - Take away Hu Tao Mention ID 
            # - Add message author at end, so bot can TRY to differentiate between people in the chat.
            # TODO: make it more consistent
            # - Replace @Mentions with raw text
            bot_name = '@Hu Tao '
            offset = len(bot_name)

            display_name = ctx.message.author.display_name
            content = message.clean_content + f" *Stated by: {display_name}*"

            author_text = content[offset:len(content)]
            print(f'Message: {author_text}')

            async with message.channel.typing():
                async with self.cai.client.connect(config.CHARACTER_AI_TOKEN) as chat2:
                    data = await chat2.send_message(self.cai.char, self.cai.chat_id, author_text, self.cai.author)
                text = data['turn']['candidates'][0]['raw_content']
                print(text)

            await message.channel.send(f"{text}")
            text_to_speech(text)
            ctx.voice_client.play(discord.FFmpegPCMAudio('voice'))
