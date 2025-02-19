#!/usr/bin/env python

import asyncio
from connect4 import Connect4, PLAYER1, PLAYER2
from websockets.exceptions import ConnectionClosedOK

from websockets.asyncio.server import serve
import json

async def handler(websocket):
    # initialize a game
    game = Connect4()
    async for message in websocket:
        print(message)
        message = json.loads(message)

        # if message type is play, handle accordingly
        if message["type"] == "play":
            player = PLAYER2 if len(game.moves) % 2 else PLAYER1
            
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
            await asyncio.sleep(0.5)
            
            if game.winner is not None:
                event = {
                    "type": "win",
                    "player": game.last_player,
                }
            
            await websocket.send(json.dumps(event))



async def main():
    async with serve(handler, "", 8001) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())