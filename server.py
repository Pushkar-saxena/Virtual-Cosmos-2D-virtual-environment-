import asyncio, json, uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class Manager:
    def __init__(self):
        self.users = {} # {id: {x, y, name}}
    
    async def broadcast(self, data):
        for ws in self.users.values():
            await ws["socket"].send_text(json.dumps(data))

manager = Manager()

@app.websocket("/ws/{uid}")
async def websocket_endpoint(websocket: WebSocket, uid: str):
    await websocket.accept()
    manager.users[uid] = {"socket": websocket, "x": 400, "y": 400, "name": f"User_{uid[:3]}"}
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg["type"] == "move":
                manager.users[uid].update({"x": msg["x"], "y": msg["y"]})
                # Send positions to everyone (excluding the socket object)
                pos_data = {k: {"x": v["x"], "y": v["y"], "name": v["name"]} for k, v in manager.users.items()}
                await manager.broadcast({"type": "sync", "users": pos_data})
            elif msg["type"] == "chat":
                await manager.broadcast({"type": "chat", "user": manager.users[uid]["name"], "msg": msg["msg"]})
    except WebSocketDisconnect:
        del manager.users[uid]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)