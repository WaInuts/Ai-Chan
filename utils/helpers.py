from pprint import pprint
import json
import asyncio

import websockets
from utils import logging
import urllib.parse


# Listen MOE
async def send_ws(ws, data):
    json_data = json.dumps(data)
    try:
        await ws.send(json_data)
    except websockets.exceptions.ConnectionClosedError as err:
        logging.error(err, "websockets")


async def send_pings(ws, interval=45):
    while True:
        await asyncio.sleep(interval)
        msg = {"op": 9}
        await send_ws(ws, msg)


# Format links for listen.moe
def build_url(base_url, path, args_dict):
    # Returns a list in the structure of urlparse.ParseResult
    url_parts = list(urllib.parse.urlparse(base_url))
    url_parts[2] = path
    url_parts[4] = urllib.parse.urlencode(args_dict)
    return urllib.parse.urlunparse(url_parts)
