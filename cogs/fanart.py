from discord.ext import commands
import random
import requests

class FanArt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    description = '`Request Anime Art of your favorite character! Type "h.generate [tag]" to recieve a picture. For example, "h.generate hu tao" will give you a picture of me!` <:hutao_owo:1187215501974319185>'
    
    # Zerochan.net will sometimes return the front end HTML code instead of a JSON.
    # This function is used to decode that HTML and find the appropriate tag.
    def _decodeHTMLContent(self, content):
        startOfTag = '<title>'
        dash = ' -'
        paranthesis = ' ('

        offset = len(startOfTag)

        startIndex = content.find(startOfTag) + offset
        endIndex = content.find(paranthesis) if content.find(paranthesis) < content.find(dash) else content.find(dash)

        tag = content[startIndex:endIndex].replace(' ', '+')

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
                print(f"We got HTML! New Tag: {tag}")
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
            print(f'Exception Occured: {err}')
            return []
        return items
    
    # Command to get anime fanart from zerochan.net
    # ex. h.generate hu tao -> return random picture of Hu Tao
    @commands.command()
    async def generate(self, ctx, *, tag):

        items = []

        match tag:
            case 'girl' | 'woman' | 'women' :
                tag = 'Female'
            case 'boy':
                tag = 'Male'
            case 'queen':
                tag = 'Hatsune+Miku'
        
        print(f"User Entered: {tag}")

        items = await self._getPictures(ctx, tag)

        if not items:
            await ctx.send(f"No Pictures Found! <:gi_hutao_notlikethis:1187215478083563662>\n\nTry another tag!")
        else:
            picID = random.randint(0, len(items) - 1)
            print(f"Index of chosen picture: {picID}")
            await ctx.send(items[picID]['thumbnail'])

        return
        
async def setup(bot):
    await bot.add_cog(FanArt(bot))
