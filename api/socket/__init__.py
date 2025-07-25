import socketio # Import the Device model

sio_server = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[]
)

@sio_server.event
async def connect(sid):
    print(f"Client connected: {sid}")
    await sio_server.emit('message', {'data': 'Welcome!'}, to=sid)

@sio_server.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")