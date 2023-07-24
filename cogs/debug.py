from discord.ext import commands

class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def yourvc(self, ctx):
        await ctx.send(f'{ctx.voice_client}')

    @commands.command()
    async def myvc(self, ctx):
        await ctx.send(f'{ctx.author.voice}')

async def setup(bot):
    await bot.add_cog(Debug(bot)) 