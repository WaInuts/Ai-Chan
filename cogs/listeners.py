from discord.ext import commands
import asyncio
from characterai import PyAsyncCAI


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
                data = await self.cai.client.chat.send_message(
                self.cai.char, message.content, 
                history_external_id=self.cai.history_id, tgt=self.cai.tgt
                )
                text = data['replies'][0]['text']
            await message.channel.send(f"{text}")

# async def setup(bot):
#     await bot.add_cog(listeners(bot))

