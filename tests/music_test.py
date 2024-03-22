from . import music_old
import pytest
import math as m

# play music from youtube url


@pytest.fixture
def song_request():
    song = {
        "url": "https://www.youtube.com/watch?v=IAPeF6txDic&ab_channel=JeanTCI",
        "loop": None,
    }
    return song


@pytest.mark.asyncio
async def test_maxFileSize(song_request):
    with pytest.raises(music_old.MaxFileException):
        await music_old.YTDLSource.from_url(
            url=song_request["url"], loop=song_request["loop"]
        )
