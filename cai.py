import asyncio
from characterai import PyAsyncCAI
from utils import config

class Cai(PyAsyncCAI):
    def __init__(self, client, chat_id, author):
        super().__init__(token=config.CHARACTER_AI_TOKEN
        )
        
        self.client = client
        self.chat_id = chat_id
        self.author = author
        self.char = 'U3dJdreV9rrvUiAnILMauI-oNH838a8E_kEYfOFPalE'

    @classmethod
    async def setup(cls):

        client = PyAsyncCAI(config.CHARACTER_AI_TOKEN)
        chat = await client.chat2.get_chat('U3dJdreV9rrvUiAnILMauI-oNH838a8E_kEYfOFPalE')
        print(chat)
        chat_id = chat['chats'][0]['chat_id']
        author = {
            'author_id': chat['chats'][0]['creator_id'],
            'is_human': True,
            'name': 'boo'
        }

        return cls(client, chat_id, author)
