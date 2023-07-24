from cogs import music
import pytest
import math as m

# play music from youtube url

@pytest.fixture
def song_request():
    song = {
        'url' : 'https://www.youtube.com/watch?v=IAPeF6txDic&ab_channel=JeanTCI',
        'loop' : None
    }
    return song 

@pytest.mark.asyncio
async def test_maxFileSize(song_request):
    with pytest.raises(music.MaxFileException):
        await music.YTDLSource.from_url(url=song_request['url'], loop=song_request['loop'])

