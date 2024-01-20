from discord.ext import commands
import discord

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', aliases=['helpmemommy'])
    async def help_(self, ctx): 
        title = 'Here are my commands!'
        icon_url = 'https://imgur.com/WvLDLj0.png'

        system = self.bot.get_cog('System')
        music = self.bot.get_cog('Music')
        #TODO: recaterogize to AI cog
        ai = self.bot.get_cog('listeners')
        fanart = self.bot.get_cog('FanArt')

        helptext = '' 
        
        ai_commands = f'\n**Start your commands with `h.`!\n\n{ai.description}**\n\n'
        helptext += ai_commands

        fanart_commands = f'**Fanart <:hutaopoem:1187257015555334204>**\n{fanart.description}\n\n'
        helptext += fanart_commands

        system_commands = f'**System :robot:\n**`'
        for command in system.get_commands():
            system_commands+=f'{command},'
        system_commands += '`\n\n'
        helptext += system_commands

        music_commands = f'**Music :musical_note:\n**`'
        for command in music.get_commands():
            music_commands+=f'{command},'
        music_commands += '`\n\n'
        helptext += music_commands

        footer = 'Type h.help [command] for more info on a command!'

        embed = discord.Embed(description=helptext)
        embed.set_author(name=title, icon_url=icon_url)
        embed.set_footer(text=footer)

        helptext = "```"
        for command in self.bot.commands:
            helptext+=f"{command}\n"
        helptext+="```"
        await ctx.send(embed=embed)

    @commands.command(name='hello', aliases=['hi', 'yo', 'hey', 'konichiwa'])
    async def hello(self, ctx):
        embed = discord.Embed(title=f'**Hello {ctx.message.author}!**')
        embed.set_image(url='https://imgur.com/SPbKVFT.png')
        return await ctx.reply(embed=embed)
    
    @commands.command(name='goodmorning', aliases=['ohayo'])
    async def goodmorning(self, ctx):
        embed = discord.Embed(title=f'**Good Morning {ctx.message.author}.**')
        embed.set_image(url='https://imgur.com/cLvPkDV.png')
        return await ctx.reply(embed=embed)
    
    @commands.command(name='goodnight', aliases=['oyasumi'])
    async def goodnight(self, ctx):
        embed = discord.Embed(title=f'**Good Night {ctx.message.author}! <3**')
        embed.set_image(url='https://imgur.com/3IJvykn.png')
        return await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(System(bot)) 