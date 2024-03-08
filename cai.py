import sys
import asyncio
# ! Out of commission until further notice
# from characterai import PyAsyncCAI, errors
from charaiPY.AsyncPyCAI2 import PyAsyncCAI2
import tls_client as tls
from utils import config
from utils import logging
from colorama import Fore
from colorama import Style

# Instructions on how to setup with new API: https://github.com/FalcoTK/PyCAI2
# TLDR: "get_chat" function is dead, have to type it manually now
class Cai(PyAsyncCAI2):
    def __init__(self, client, chara_id, chat_id, creator_id):
        super().__init__(token=config.CHARACTER_AI_TOKEN)
        
        self.client = client
        self.chara_id = chara_id
        self.chat_id = chat_id
        self.creator_id = creator_id

    @classmethod
    async def setup(cls):
        # Deprecated, will remove if OG CAI never updates 
        # chat = await client.chat2.get_chat('U3dJdreV9rrvUiAnILMauI-oNH838a8E_kEYfOFPalE')
        # chat_id = chat['chats'][0]['chat_id']
        # creator_id = chat['chats'][0]['creator_id']
        try:
            client = PyAsyncCAI2(config.CHARACTER_AI_TOKEN)
            chara_id = 'U3dJdreV9rrvUiAnILMauI-oNH838a8E_kEYfOFPalE'
            chat_id = '57d8eb6e-808d-4659-b612-7ccaba78e3a8'
            creator_id = '357020589'
            logging.info(f'{Style.BRIGHT}Chat JSON info:{Style.RESET_ALL}\n\nchar_id:{chara_id}\nchat_id: {chat_id}\ncreator_id: {creator_id}', 'CharacterAI')
        except Exception as err:
            logging.error(err, "CharacterAi")
            client = None
            chara_id = None
            chat_id = None
            creator_id = None
            pass

        return cls(client, chara_id, chat_id, creator_id)
