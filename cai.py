import sys
import asyncio
from characterai import PyAsyncCAI, errors
import traceback
from utils import config
from utils import logging
from colorama import Fore
from colorama import Style

class Cai(PyAsyncCAI):
    def __init__(self, client, chat_id, creator_id):
        super().__init__(token=config.CHARACTER_AI_TOKEN
        )
        
        self.client = client
        self.chat_id = chat_id
        self.creator_id = creator_id
        self.char = 'U3dJdreV9rrvUiAnILMauI-oNH838a8E_kEYfOFPalE'

    @classmethod
    async def setup(cls):
        try:
            client = PyAsyncCAI(config.CHARACTER_AI_TOKEN)
            chat = await client.chat2.get_chat('U3dJdreV9rrvUiAnILMauI-oNH838a8E_kEYfOFPalE')
            print(chat)
            chat_id = chat['chats'][0]['chat_id']
            creator_id = chat['chats'][0]['creator_id']
        except Exception as err:
            logging.error(err, "CharacterAi")
            client = None
            chat = None
            chat_id = None
            creator_id = None
            pass

        return cls(client, chat_id, creator_id)
