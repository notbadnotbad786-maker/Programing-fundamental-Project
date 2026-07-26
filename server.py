import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

app = FastAPI()
laptop_client = None
mobile_client = None

# Folder this file lives in — assumes controller.html and index.html
# sit in the SAME folder as this server.py (adjust paths below if you
# later move them into separate game/ and mobile/ subfolders).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.get("/controller.html")
async def serve_controller():
    return FileResponse(os.path.join(BASE_DIR, "controller.html"))


@app.get("/index.html")
async def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.get("/")
async def serve_root():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.websocket("/ws/laptop")
async def websocket_laptop(websocket: WebSocket):
    global laptop_client
    await websocket.accept()
    laptop_client = websocket
    print("✓ Laptop 3D Scene Connected")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("✗ Laptop Disconnected")
        laptop_client = None


@app.websocket("/ws/mobile")
async def websocket_mobile(websocket: WebSocket):
    global mobile_client, laptop_client
    await websocket.accept()
    mobile_client = websocket
    print("✓ Mobile Controller Connected")
    try:
        while True:
            data = await websocket.receive_text()
            if laptop_client:
                await laptop_client.send_text(data)
    except WebSocketDisconnect:
        print("✗ Mobile Disconnected")
        mobile_client = None


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)