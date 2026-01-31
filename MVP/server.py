"""
@file server.py
@description FastAPI WebSocket Server with Real-Time Background Physics Loop.
@module APIServer
"""

import os
import asyncio
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from MVP.main import GameEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Engine Instance
engine = GameEngine()

# Connected Clients
clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    print("[SERVER] Client Connected")
    
    # Send Init
    await websocket.send_text(json.dumps({
        "type": "INIT",
        "message": "Connection Established. Telemetry Stream Active.",
        "telemetry": engine.get_telemetry()
    }))

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_input = payload.get("text", "")
            
            # Handle Command (Blocking LLM call for now - could be async)
            # Running in thread pool to not block the physics loop
            response = await asyncio.to_thread(engine.handle_command, user_input)
            
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        print("[SERVER] Client Disconnected")
        clients.remove(websocket)
    except Exception as e:
        print(f"[SERVER] Error: {e}")
        if websocket in clients:
            clients.remove(websocket)
        await websocket.close()

async def physics_loop():
    """Background task to tick the physics engine every second."""
    print("[SERVER] Physics Loop Started")
    while True:
        start_time = time.time()
        
        # 1. Tick Engine
        tick_result = engine.tick(delta_time=1.0)
        
        # 2. Broadcast Telemetry to all clients
        if clients:
            msg = json.dumps({
                "type": "TELEMETRY",
                "telemetry": tick_result['telemetry'],
                "sensory": tick_result['sensory'] # Optional: Send sensory text for HUD logs
            })
            # Broadcast
            disconnected = []
            for client in clients:
                try:
                    await client.send_text(msg)
                except Exception:
                    disconnected.append(client)
            
            for d in disconnected:
                clients.remove(d)
        
        # 3. Sleep remainder of 1 second
        elapsed = time.time() - start_time
        sleep_time = max(0.0, 1.0 - elapsed)
        await asyncio.sleep(sleep_time)

@app.on_event("startup")
async def startup_event():
    # Start the physics loop on server startup
    asyncio.create_task(physics_loop())

# Mount Static Files (Frontend)
# Must be last to avoid overriding API routes
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    print(f"[WARNING] Frontend dist not found at {frontend_dist}")
