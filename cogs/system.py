from discord.ext import commands
import discord
from utils import logging
from utils import config
from colorama import Style


class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.system(
            f"{Style.BRIGHT}Logged in as {self.bot.user}{Style.RESET_ALL} (ID: {self.bot.user.id})",
            "discord.client",
        )
        if config.DEBUG == "TRUE":
            self.bot.tree.copy_global_to(guild=config.GUILDS_ID)
            await self.bot.tree.sync(guild=config.GUILDS_ID)
        else:
            await self.bot.tree.sync()

        print("------")

    @commands.hybrid_command(
        name="help", aliases=["helpmemommy"], description="List of Commands"
    )
    async def help(self, ctx):
        title = "Here are my commands!"
        icon_url = "https://imgur.com/WvLDLj0.png"

        system = self.bot.get_cog("System")
        music = self.bot.get_cog("Music")
        # TODO: recaterogize to AI cog
        ai = self.bot.get_cog("AI")
        fanart = self.bot.get_cog("FanArt")

        helptext = ""

        ai_commands = f"\n**Start your commands with `h.`!\n\n{ai.description}**\n\n"
        helptext += ai_commands

        fanart_commands = (
            f"**Fanart <:hutaopoem:1187257015555334204>**\n{fanart.description}\n\n"
        )
        helptext += fanart_commands

        system_commands = f"**System :robot:\n**`"
        for command in system.get_commands():
            system_commands += f"{command},"
        system_commands += "`\n\n"
        helptext += system_commands

        music_commands = f"**Music :musical_note:\n**`"
        for command in music.get_commands():
            music_commands += f"{command},"
        music_commands += "`\n\n"
        helptext += music_commands

        footer = "Type h.help [command] for more info on a command!"

        embed = discord.Embed(description=helptext)
        embed.set_author(name=title, icon_url=icon_url)
        embed.set_footer(text=footer)

        helptext = "```"
        for command in self.bot.commands:
            helptext += f"{command}\n"
        helptext += "```"
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="hello",
        aliases=["hi", "yo", "hey", "konichiwa"],
        description="Say Hi to Hu Tao!",
    )
    async def hello(self, ctx):
        embed = discord.Embed(title=f"**Hello {ctx.message.author.display_name}!**")
        embed.set_image(url="https://imgur.com/SPbKVFT.png")
        return await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="goodmorning", aliases=["ohayo"], description="Wish Hu Tao a Good Morning!"
    )
    async def goodmorning(self, ctx):
        embed = discord.Embed(
            title=f"**Good Morning {ctx.message.author.display_name}.**"
        )
        embed.set_image(url="https://imgur.com/cLvPkDV.png")
        return await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="goodnight", aliases=["oyasumi"], description="Wish Hu Tao a Good Night!"
    )
    async def goodnight(self, ctx):
        embed = discord.Embed(
            title=f"**Good Night {ctx.message.author.display_name}! <3**"
        )
        embed.set_image(url="https://imgur.com/3IJvykn.png")
        return await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(System(bot))
