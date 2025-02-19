#!/usr/bin/env python

import secrets
import asyncio
from connect4 import Connect4, PLAYER1, PLAYER2
from websockets.exceptions import ConnectionClosedOK

from websockets.asyncio.server import serve
import json

JOIN = {}

async def error(websocket, message):
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))

async def join(websocket, join_key):
    # Find connect Four game
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return

    # register to receive moves from the game
    connected.add(websocket)
    try:
        #temporary - for testing
        print("second player joined game", id(game))
        async for message in websocket:
            print("Second player sent", message)
    finally:
        connected.remove(websocket)

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

    if "join" in event:
        # second player joins existing game
        await join(websocket, event["join"])
    else:
        # first player starts a new game
        await start(websocket)

    # first player starts a new game
    await start(websocket)
            



async def main():
    async with serve(handler, "", 8001) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())