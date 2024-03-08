from discord.ext import commands
from utils import logging
import random
import requests

class FanArt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    description = '`Request Anime Art of your favorite character! Type "h.generate [tag]" to recieve a picture. For example, "h.generate hu tao" will give you a picture of me!` <:hutao_owo:1187215501974319185>'
    description_short = description[1:46]
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
            logging.error(f'HTTP Error - {err}', 'Zerochan.net')
            return []
        except requests.exceptions.ReadTimeout as err:
            # Maybe set up for a retry, or continue in a retry loop
            logging.error(f'Timeout - {err}', 'Zerochan.net')
            return []
        except requests.exceptions.TooManyRedirects as err:
            # Tell the user their URL was bad and try a different one
            logging.error(f'TooManyRedirects - {err}', 'Zerochan.net')
            return []
        except requests.exceptions.RequestException as err:
            # catastrophic error. bail.
            logging.error(err, 'Zerochan.net')
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
                logging.info(f"We got HTML! New Tag: {tag}", 'Zerochan.net')
                tries += 1
                items = await self._getPictures(ctx, tag, tries)
                return items
            # If decode fails, exit.
            else:
                logging.warning('We keep receiving HTML, bail.', 'Zerochan.net')
                return []
        except requests.exceptions.InvalidJSONError | TypeError as err:
            logging.error(f"Invalid JSON Error - {err}", 'Zerochan.net')
            return []
        except requests.exceptions.RequestException as err:
            logging.error(err, 'Zerochan.net')
            return []
        return items
    
    # Command to get anime fanart from zerochan.net
    # ex. h.generate hu tao -> return random picture of Hu Tao
    @commands.hybrid_command(name="generate", description=description_short)
    async def generate(self, ctx, *, tag: str):
        """Request Anime Art of your favorite character!

        Parameters
        -----------
        tag: str
            Who do you want a picture of?
        """
        items = []

        match tag:
            case 'girl' | 'woman' | 'women' :
                tag = 'Female'
            case 'boy':
                tag = 'Male'
            case 'queen':
                tag = 'Hatsune+Miku'
        
        logging.info(f"User Entered: {tag}", 'Zerochan.net')

        items = await self._getPictures(ctx, tag)

        if not items:
            await ctx.send(f"No Pictures Found! <:gi_hutao_notlikethis:1187215478083563662>\n\nTry another tag!")
        else:
            picID = random.randint(0, len(items) - 1)
            logging.info(f"Index of chosen picture: {picID}", 'Zerochan.net')
            await ctx.send(items[picID]['thumbnail'])

        return
        
async def setup(bot):
    await bot.add_cog(FanArt(bot))
