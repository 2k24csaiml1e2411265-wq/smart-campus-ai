from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.realtime import ws_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    await ws.send_json({"type": "hello", "status": "LIVE", "message": "Smart Campus AI realtime channel"})
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
