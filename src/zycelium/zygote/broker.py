"""
Frame broker.
"""
import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.on("connect")
async def connect(sid, _environ):
    """On connected."""
    print("connect ", sid)


@sio.on("disconnect")
def disconnect(sid):
    """On disconnected."""
    print("disconnect ", sid)


@sio.on("*")
async def frame(event, sid, data):
    """On frame."""
    print("frame ", event, sid, data)
    await sio.emit(event, data)
