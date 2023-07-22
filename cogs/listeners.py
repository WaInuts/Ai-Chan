from discord.ext import commands

class listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self.bot))

async def setup(bot):
    await bot.add_cog(listeners(bot))

