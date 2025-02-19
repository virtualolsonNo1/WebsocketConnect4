#!/usr/bin/env python

import secrets
import asyncio
from connect4 import Connect4, PLAYER1, PLAYER2
from websockets.exceptions import ConnectionClosedOK

from websockets.asyncio.server import serve
import json

JOIN = {}

async def start(websocket):
    # initialize connect 4 game, set of websocket connections receiving game moves, and secret access token
    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    try:
        # send secret access token to browser of first player where it'll be used for buliidng a join link
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        #temporary for testing
        print("first player started game", id(game))
        async for message in websocket:
            print("first player sent", message)

    finally:
        del JOIN[join_key]

async def handler(websocket):
    # receive and parse init event from UI
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    # first player starts a new game
    await start(websocket)
            



async def main():
    async with serve(handler, "", 8001) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())