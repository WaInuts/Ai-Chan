from discord.ext import commands
import random
import requests

class message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def generate(self, ctx, type):
        headers = {
          'User-Agent' : 'Gamer Bot - B Box9688' 
          }

        if ctx.message.author.name == "nelsons":
            r = requests.get(f'https://www.zerochan.net/Klee?json',headers=headers)
            item = random.choice(tuple(r.json()['items']))
            await ctx.send(item['thumbnail'])
            return
        
        match type:
            case 'girl':
                tags = {'Female', 'Solo'}
            case 'boy':
                tags = {'Male', 'Solo'}

        id = str(random.randint(1, 200))
        r = requests.get(f'https://www.zerochan.net/?p={id}&l=25&s=fav&json',headers=headers)
        items = r.json()['items']
        for item in items:
            if tags.issubset(item['tags']):
                await ctx.send(item['thumbnail'])
                return

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
