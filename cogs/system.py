from typing import Coroutine
from discord.ext import commands
import discord
from utils import config, logging, colors
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
    async def help(self, ctx, command: str = None):
        """Need help? Here's a list of commands!

        Parameters
        -----------
        command: str
            Get more information about a specific command.
        """
        embed = discord.Embed(
            color=int(colors.HUTAO_RED, 16)
        )  # Convert color from hex to decimal
        embed.set_author(
            name="Ai-Chan (Hu Tao) v0.727", icon_url="https://imgur.com/aZFuOqZ.png"
        )
        command_names_list = [command.name for command in self.bot.commands]

        system = self.bot.get_cog("System")
        music = self.bot.get_cog("Music")
        ai = self.bot.get_cog("AI")
        fanart = self.bot.get_cog("FanArt")

        if not command:
            embed.title = "Start your commands with 'h.' or '/'!"

            embed.add_field(
                name="Hu Tao! <a:hutao_burger:1187215479400566844>",
                value=f"`{ai.description}`",
            )

            embed.add_field(
                name="System :robot:",
                value=",".join(
                    [f"`/{command.name}`" for command in system.get_commands()]
                ),
            )

            embed.add_field(
                name="Fanart <:hutaopoem:1187257015555334204>",
                value=fanart.description,
                inline=False,
            )

            embed.add_field(
                name="Music <a:hutao_music:1187216417121124413> :musical_note:",
                value=",".join(
                    [f"`/{command.name}`" for command in music.get_commands()]
                ),
                inline=False,
            )

            embed.set_footer(
                text="Type h.help [command] or /help [command] for more info on a command!"
            )

        # If command exists, show more information about the command.
        elif command in command_names_list:
            command = self.bot.get_command(command)
            embed.add_field(
                name=(
                    f"`/{command.name} {command.signature}`"
                    + (
                        "Aliases: " + ", ".join(command.aliases)
                        if command.aliases
                        else ""
                    )
                ),
                value=f"{command.help}",
            )
            embed.set_footer(text="Type h.help or /help for a list of every command!")
        # Command does not exist!
        else:
            embed.add_field(
                name="This command does not exist!",
                value="You silly baka!"
                + (" -Rod" if ctx.guild.id == config.GUILDS_ID.id else ""),
            )
            embed.set_footer(text="Type h.help or /help for a list of every command!")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="hello", aliases=["hi", "yo", "hey", "konichiwa"])
    async def hello(self, ctx):
        """Say Hi to Hu Tao!"""
        embed = discord.Embed(title=f"**Hello {ctx.message.author.display_name}!**")
        embed.set_image(url="https://imgur.com/SPbKVFT.png")
        return await ctx.reply(embed=embed)

    @commands.hybrid_command(name="goodmorning", aliases=["ohayo"])
    async def goodmorning(self, ctx):
        """Wish Hu Tao a Good Morning!"""
        embed = discord.Embed(
            title=f"**Good Morning {ctx.message.author.display_name}.**"
        )
        embed.set_image(url="https://imgur.com/cLvPkDV.png")
        return await ctx.reply(embed=embed)

    @commands.hybrid_command(name="goodnight", aliases=["oyasumi"])
    async def goodnight(self, ctx):
        """Wish Hu Tao a Good Night!"""
        embed = discord.Embed(
            title=f"**Good Night {ctx.message.author.display_name}! <3**"
        )
        embed.set_image(url="https://imgur.com/3IJvykn.png")
        return await ctx.reply(embed=embed)

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


async def setup(bot):
    await bot.add_cog(System(bot))
