import asyncio
from characterai import PyAsyncCAI
from utils import config

class Cai(PyAsyncCAI):
    def __init__(self, client, history_id, tgt):
        super().__init__(token=config.CHARACTER_AI_TOKEN
        )
        
        self.client = client
        self.history_id = history_id
        self.tgt = tgt
        self.char = 'U3dJdreV9rrvUiAnILMauI-oNH838a8E_kEYfOFPalE'

    @classmethod
    async def setup(cls):

        client = PyAsyncCAI(config.CHARACTER_AI_TOKEN)
        await client.start()
        chat = await client.chat.get_chat('U3dJdreV9rrvUiAnILMauI-oNH838a8E_kEYfOFPalE')

        history_id = chat['external_id']
        participants = chat['participants']

        # In the list of "participants",
        # a character can be at zero or in the first place
        if not participants[0]['is_human']:
            tgt = participants[0]['user']['username']
        else:
            tgt = participants[1]['user']['username']

        return cls(client, history_id, tgt)
