from discord.ext import commands
from utils import config
from utils.voice import *

class AI(commands.Cog):
    def __init__(self, bot, cai):
        self.bot = bot
        self.cai = cai
    
    description = "To talk to Hu Tao, @Hu Tao with your message!"
    
    @commands.Cog.listener()
    # Listener that allows bot to reply to user if they mention Hu Tao in their message.
    # Bot will also join voice channel to verbally state message.
    async def on_message(self, message):
        
        if self.bot.user not in message.mentions: return

        # Conditional to check if users (mellowtrippy) is in the right channel. (temporary)
        slimecraft_id = 812173836358254625
        kamasutra = self.bot.get_channel(1184754753473892373)
        if message.channel.id != slimecraft_id:
            ctx = await self.bot.get_context(message)

            display_name = ctx.message.author.display_name
            author_text = message.clean_content
            print(f'Message: {author_text}')
            author = {
                'author_id': self.cai.creator_id,
                'is_human': True,
                'name': display_name
            }

            async with message.channel.typing():
                try:
                    async with self.cai.client.connect(config.CHARACTER_AI_TOKEN) as chat2:
                        data = await chat2.send_message(self.cai.char,
                                                        self.cai.chat_id,
                                                        author_text, author)   
                    text = data['turn']['candidates'][0]['raw_content']
                    print(f'Hu Tao: {text}')
                except:
                    await message.channel.send(
                        f"`*sarcastic* I couldn't quite hear you dear, can you repeat what you said?`")
                    return
            await message.channel.send(f"{text}")
            
            # # If user is in voice channel, join VC and verbally state message.
            # if message.author.voice:
            #     audio = silero_tts(text)
            #     if not ctx.message.guild.voice_client:
            #         await connect(ctx)
            #     if not ctx.message.guild.voice_client.is_playing:
            #         ctx.message.guild.voice_client.play(discord.FFmpegPCMAudio(audio))
            #     else:
            #         #TODO: Bot pauses music and plays audio? Queues Audio? 
            #         print('Currently playing music or talking already, so I cannot talk!')

        else:
            await message.channel.send(f"Go to {kamasutra.mention} to speak to me {message.author.mention} :)")


