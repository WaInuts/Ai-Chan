from discord.ext import commands
import discord
import logging
import asyncio
import re
from characterai import PyAsyncCAI
from utils import config

from utils.voice import text_to_speech

class AI(commands.Cog):
    def __init__(self, bot, cai):
        self.bot = bot
        self.cai = cai
    
    description = "To talk to Hu Tao, @Hu Tao with your message!"
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user in message.mentions:
            ctx = await self.bot.get_context(message)

            display_name = ctx.message.author.display_name
            author_text = message.clean_content

            print(f'Message: {author_text}')

            author = {
                'author_id': self.cai.creator_id,
                'is_human': True,
                'name': display_name
            }

            async with message.channel.typing():
                try:
                    async with self.cai.client.connect(config.CHARACTER_AI_TOKEN) as chat2:
                        data = await chat2.send_message(self.cai.char, self.cai.chat_id, author_text, author)   
                    text = data['turn']['candidates'][0]['raw_content']
                    print(f'Hu Tao: {text}')
                except:
                    await message.channel.send(f"*sarcastic* I couldn't quite hear you dear, can you repeat what you said? \n`An Error has occured! Please try again with a different message. blame @box`")
                    return
            await message.channel.send(f"{text}")

            # TODO: Add backup TTS
            #text_to_speech(text)
            #ctx.voice_client.play(discord.FFmpegPCMAudio('voice'))
