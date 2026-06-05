import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.services import monitoring

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)


manager = ConnectionManager()


@router.websocket("/monitoring")
async def monitoring_ws(websocket: WebSocket, token: str | None = None):
    if not token or not decode_access_token(token):
        await websocket.close(code=4401)
        return
    await manager.connect(websocket)
    try:
        while True:
            db = SessionLocal()
            try:
                payload = {
                    "type": "live_summary",
                    "data": monitoring.get_live_summary(db),
                }
            finally:
                db.close()
            await websocket.send_text(json.dumps(payload, default=str))
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
