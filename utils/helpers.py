from pprint import pprint
import json
import asyncio

import websockets


# Listen MOE
async def send_ws(ws, data):
	json_data = json.dumps(data)
	await ws.send(json_data)

async def send_pings(ws, interval=45):
	while True:
		await asyncio.sleep(interval)
		msg = { 'op': 9 }
		await send_ws(ws, msg)