#!/usr/bin/env python

import secrets
import asyncio
from connect4 import Connect4, PLAYER1, PLAYER2
from websockets.exceptions import ConnectionClosedOK

from websockets.asyncio.server import serve
import json

JOIN = {}
WATCH = {}

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
        # after second player has joined game, wait for messages from them regarding moves
        print("second player joined game", id(game))
        await play(websocket, game, PLAYER2, connected)
    finally:
        connected.remove(websocket)

async def start(websocket):
    # initialize connect 4 game, set of websocket connections receiving game moves, and secret access token
    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    watch_key = secrets.token_urlsafe(12)
    WATCH[watch_key] = game, connected

    print(watch_key)

    try:
        # send secret access token to browser of first player where it'll be used for buliidng a join link
        event = {
            "type": "init",
            "join": join_key,
            "watch": watch_key,
        }
        await websocket.send(json.dumps(event))

        # after player 1 has joined game, wait for 
        print("first player started game", id(game))
        await play(websocket, game, PLAYER1, connected)

    finally:
        del JOIN[join_key]
        del WATCH[watch_key]

async def handler(websocket):
    # receive and parse init event from UI
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # second player joins existing game
        await join(websocket, event["join"])
    elif "watch" in event:
        # person wants to watch
        await watch(websocket, event["watch"])
    else:
        # first player starts a new game
        await start(websocket)

    # first player starts a new game
    await start(websocket)
            

async def play(websocket, game, player, connected):
    async for message in websocket:
        print(message)
        message = json.loads(message)

        # if message type is play, handle accordingly
        if message["type"] == "play":
            player_turn = PLAYER2 if len(game.moves) % 2 else PLAYER1
            if (player != player_turn):
                print("NOT THIS PLAYER'S TURN!!!!!!!!!!!!!")
                continue
            
            
            print(player)
            print(len(game.moves))

            # check for bad move, ignoring it if that's the case and waiting for another move
            try:
                row = game.play(player, message["column"])
            except ValueError as e:
                print(e)
                continue

            event = {
                "type": "play",
                "player": player,
                "column": message["column"],
                "row": row,
            }

            await websocket.send(json.dumps(event))
            for ws in connected:
                if ws != websocket:
                    await ws.send(json.dumps(event))
            await asyncio.sleep(0.5)
            
            if game.winner is not None:
                event = {
                    "type": "win",
                    "player": game.last_player,
                }
            
            await websocket.send(json.dumps(event))

async def watch(websocket, watch_key):

    try:
        game, connected = WATCH[watch_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return

    # register to receive moves from the game
    connected.add(websocket)

    # TODO: FIGURE OUT IF THIS WORKS RIGHT!!!
    count = 0
    for move in game.moves:
        player_turn = PLAYER2 if len(game.moves) % 2 else PLAYER1
        play(websocket, game, player_turn, connected)

    try:
        await websocket.wait_closed()
    finally:
        connected.remove(websocket)


async def main():
    async with serve(handler, "", 8001) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())