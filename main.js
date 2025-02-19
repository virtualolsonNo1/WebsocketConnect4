import {createBoard, playMove } from "../connect4.js"

function initGame(websocket) {
    websocket.addEventListener("open", () => {
        // send init event according to who is connecting
        const params = new URLSearchParams(window.location.search);

        let event = { type: "init" };
        if (params.has("join")) {
            // second player joins existing game
            event.join = params.get("join");
        } else {
            // first player starts a new game
        }
        websocket.send(JSON.stringify(event));
    });
}
function sendMoves(board, websocket) {
    // send play event on click for move in clicked col
    board.addEventListener("click", ({target}) => {
        const column = target.dataset.column;
        // ignore clicks elsewhere
        if (column === undefined) {
            return;
        }
        const event = {
            type: "play",
            column: parseInt(column, 10),
        };
        websocket.send(JSON.stringify(event));
    });
}

function showMessage(message) {
    window.setTimeout(() => window.alert(message, 50));
}

function receiveMoves(board, websocket) {
    websocket.addEventListener("message", ({ data }) => {
        const event = JSON.parse(data);
        switch (event.type) {
            case "play": 
            // udpate the UI with mvoe
                playMove(board, event.player, event.column, event.row);
                break;
            case "win":
                showMessage('Player ${event.player} wins!');
                websocket.close(1000);
                break;
            case "error":
                showMessage(event.message);
                break;
            case "init":
                // create link for inviting second player
                document.querySelector(".join").href = "?join=" + event.join;
                break;
            default:
                throw new Error('Unsupported event type: ${event.type}.');

        }
    });
}

window.addEventListener("DOMContentLoaded", () => {
    // Initialize the UI
    const board = document.querySelector(".board");
    createBoard(board);
    // open websocket connection and register event handlers
    const websocket = new WebSocket("ws://localhost:8001/");
    initGame(websocket);
    receiveMoves(board, websocket);
    sendMoves(board, websocket);
})
