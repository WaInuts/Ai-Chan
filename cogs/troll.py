import discord
from discord.ext import commands

class Troll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def gio(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/368567591322779649/1185799736993783848/leagueisFun.PNG?ex=6590ed10&is=657e7810&hm=3b142d0e597d6753d5d328077e5aa58a341891805c3408c177f85a3848eb5300&')
    
    @commands.command()
    async def dridri(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/820804950610149376/954458056404647977/IMG_3376.jpg?ex=658f1ad5&is=657ca5d5&hm=5b935eb7706e3f3910e183a766615fddcd293c88f03819e01d2653b135539329&')

    @commands.command()
    async def bricked(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/368567591322779649/1186152529063579729/bricked.PNG?ex=659235a0&is=657fc0a0&hm=8064f5b83bcfa6511b5f8c0dc6635641d0d9e32536d48e4463c0e518b7ec9e75&')

    @commands.command()
    async def torres(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/368567591322779649/1186152577235173507/torres.PNG?ex=659235ac&is=657fc0ac&hm=f6c9c160a47f156c91b0b9b15938e7cac0816c82a0610136e8ea17ef26e616bf&')

    @commands.command()
    async def dridri2(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/368567591322779649/1186474478528634910/papers.PNG?ex=65936177&is=6580ec77&hm=24c2f0c7f34e377baad7ccfbcff1fd8b9693ccc87cf2d7f857ca6636ca9f5130&')

    @commands.command()
    async def skitzo(self, ctx):
        return await ctx.send('https://media.discordapp.net/attachments/812173836358254625/1186475685041148006/IMG_0483.png?ex=65936296&is=6580ed96&hm=5e370ae2d41d330868c4658eaaf922c785710c2cc843ea494628c3fd04238ac4&=&format=webp&quality=lossless&width=857&height=676')

    @commands.command()
    async def gus(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/368567591322779649/1186477898954190918/Screenshot_20231103_134819_Discord.jpg?ex=659364a6&is=6580efa6&hm=dc4a8ba6000f720ae6f4d337ab229caafad40914ac264b039dcbfb37e6ac4fa4&')

    @commands.command()
    async def ursa(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/368567591322779649/1186478257319710751/femboy.PNG?ex=659364fc&is=6580effc&hm=95db465862b893c89de25e39a49d98ab3f068a1b58415089398a39bc6e7cbff1&')

    @commands.command()
    async def gio2(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/812173836358254625/1186500235002921070/F7FB775B-6CBB-4AF0-ADD5-F83CDD5206D8.png?ex=65937974&is=65810474&hm=e55a41ae4be80b610f4d101f632cc4189808bdd4cfbd762a12fa590ffe4fcc6f&')

    @commands.command()
    async def rod(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/368567591322779649/1186848539549114389/downbad.PNG?ex=6594bdd6&is=658248d6&hm=a8d46c9fda455d2c5a5266c83d26869dd8f9e146ae85ee433f6869b6bb556878&')

    @commands.command()
    async def nicholas(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/1187285011347558440/1187340501603594240/nicholas.PNG?ex=65968803&is=65841303&hm=d5c0e40457e9bdeab1a25d76ae0b97ec5c1609680710a9424badeaee609b3212&')
    
    @commands.command()
    async def rody(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/1187285011347558440/1187340501603594240/nicholas.PNG?ex=65968803&is=65841303&hm=d5c0e40457e9bdeab1a25d76ae0b97ec5c1609680710a9424badeaee609b3212&')
    
    @commands.command()
    async def gio3(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/368567591322779649/1188942986269175908/bbc.PNG?ex=659c5c71&is=6589e771&hm=11f3da942b571bdcab6db2de5f4b862cd2619cf876628da5a13643d207b63a9d&')

    @commands.command()
    async def gio4(self, ctx):
        return await ctx.send('https://cdn.discordapp.com/attachments/1187285011347558440/1199580483206533150/image.png?ex=65c30f62&is=65b09a62&hm=3cf1721d83177d271579777f869b01f57fb97e89058758cb9ced356c1e4a958b&')

async def setup(bot):
    await bot.add_cog(Troll(bot))

