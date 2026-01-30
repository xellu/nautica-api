import asyncio
import json
import websockets

URI = "ws://localhost:8300/test"  # change to your websocket URL

async def main():
    async with websockets.connect(URI) as ws:
        payload = {"id": "hello", "hello": "world"}
        await ws.send(json.dumps(payload))
        print("Sent:", payload)

        # optional: receive a response
        response = await ws.recv()
        print("Received:", response)

asyncio.run(main())
