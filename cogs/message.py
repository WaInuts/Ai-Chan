from discord.ext import commands
import random
import requests
import discord

class message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Zerochan.net will sometimes return the front end HTML code instead of a JSON.
    # This function is used to decode that HTML and find the appropriate tag.
    def _decodeHTMLContent(self, content):
        print("type: ", type(content))
        print(content)
        startOfTag = '<title>'
        endOfTagDash = ' -'
        endOfTagPara = ' ('

        offset = len(startOfTag)
        print(offset)

        startIndex = content.find(startOfTag) + offset
        print(startIndex)
        endIndex = content.find(endOfTagPara) if content.find(endOfTagPara) < content.find(endOfTagDash) else content.find(endOfTagDash)
        print(endIndex)

        tag = content[startIndex:endIndex].replace(' ', '+')
        
        print(tag)

        return tag
    
    async def _getPictures(self, ctx, tag, tries=0):
        headers = {
          'User-Agent' : 'Gamer Bot - B Box9688' 
          }
        
        try:
            r = requests.get(f'https://www.zerochan.net/{tag}?p=1&l=25&s=fav&json',headers=headers, timeout=5)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print('HTTP Error: ', err)
            return []
        except requests.exceptions.ReadTimeout:
            # Maybe set up for a retry, or continue in a retry loop
            print('Timeout')
            return []
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print('TooManyRedirects')
            return []
        except requests.exceptions.RequestException as err:
            # catastrophic error. bail.
            print('Exception Occured: ', err)
            return []
        
        try:
            json = r.json()
            if not json:
                return []
            
            items = json['items']
        except requests.exceptions.JSONDecodeError as err:
            # If API returns frontend, decode tag from it and request again with new tag.
            if tries <= 1:
                content = str(r.content)
                tag = self._decodeHTMLContent(content)
                print("We got HTML! New Tag: ", tag)
                tries += 1
                items = await self._getPictures(ctx, tag, tries)
                return items
            # If decode fails, exit.
            else:
                print('tries > 1')
                return []
        except requests.exceptions.InvalidJSONError | TypeError:
            print("Invalid JSON Error.")
            return []
        except requests.exceptions.RequestException as err:
            print('Exception Occured: ', err)
            return []
        return items
    
    @commands.command()
    async def generate(self, ctx, *, tag):
        # if ctx.message.author.name == "poop":
        #     r = requests.get(f'https://www.zerochan.net/Hu+Tao?json',headers=headers)
        #     item = random.choice(tuple(r.json()['items']))
        #     await ctx.send(item['thumbnail'])
        #     return
        
        match tag:
            case 'girl' | 'woman' | 'women' :
                tag = 'Female'
            case 'boy':
                tag = 'Male'
            case 'femboy':
                tag = 'Rider+of+Black'
            case 'queen':
                tag = 'Hatsune+Miku'
            case 'minecraft':
                tag = 'Creeper+%28Minecraft%29'
        
        print('User Entered: ', tag)
        items = []
        items = await self._getPictures(ctx, tag)

        if not items:
            await ctx.send(f"No Pictures Found! :3\n\nTry another tag!")
        else:
            picID = random.randint(0, len(items) - 1)
            print(picID)
            await ctx.send(items[picID]['thumbnail'])

        return
    
    @commands.command()
    async def goodnight(self, ctx):
        embed = discord.Embed(title=f'**Good Night {ctx.message.author.mention}! <3**')
        embed.set_image(url='https://imgur.com/3IJvykn.png')
        return await ctx.reply(embed=embed)
    
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

async def setup(bot):
    await bot.add_cog(message(bot))


#   # experimental concept for $generate but requires new parsing method
#   # to generate json objects and improved random generator

#   # url = 'https://www.zerochan.net/'
#   # for tag in tags:
#   #   url += tag
#   #   if tag == tags[-1]:
#   #     url += '?json'
#   #   else:
#   #     url += ','

#   # print(url)
#   # r = requests.get(url,headers=headers)
#   # print(r.json()['items'])
#   # item = random.choice(tuple(r.json()['items']))
#   # await ctx.send(item['thumbnail'])
#   # return
