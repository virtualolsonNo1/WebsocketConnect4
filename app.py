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
        if message["type"] == "play":
            player = PLAYER2 if len(game.moves) % 2 else PLAYER1
            print(game.last_player)
            print(player)
            print(len(game.moves))
            row = game.play(player, message["column"])
            event = {
                "type": "play",
                "player": player,
                "column": message["column"],
                "row": row,
            }
            await websocket.send(json.dumps(event))
            await asyncio.sleep(0.5)

    # for player, column, row in [
    #     (PLAYER1, 3, 0),
    #     (PLAYER2, 3, 1),
    #     (PLAYER1, 4, 0),
    #     (PLAYER2, 4, 1),
    #     (PLAYER1, 2, 0),
    #     (PLAYER2, 1, 0),
    #     (PLAYER1, 5, 0),
    # ]:
    #     event = {
    #         "type": "play",
    #         "player": player,
    #         "column": column,
    #         "row": row,
    #     }
    #     await websocket.send(json.dumps(event))
    #     await asyncio.sleep(0.5)
    # event = {
    #     "type": "win",
    #     "player": PLAYER1,
    # }
    # await websocket.send(json.dumps(event))

async def main():
    async with serve(handler, "", 8001) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())