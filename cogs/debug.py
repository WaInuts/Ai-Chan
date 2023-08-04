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

    @commands.command()
    async def help(self, ctx):
        helptext = "```"
        for command in self.bot.commands:
            helptext+=f"{command}\n"
        helptext+="```"
        await ctx.send(helptext)

async def setup(bot):
    await bot.add_cog(Debug(bot)) 