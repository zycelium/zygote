"""
Frame broker.
"""
import socketio

from zycelium.zygote.logging import get_logger

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
log = get_logger("zygote.broker")


@sio.on("connect")
async def connect(sid, _environ, auth: dict):
    """On connected."""
    from zycelium.zygote.server import api  # pylint: disable=import-outside-toplevel

    log.info("Agent connected: %s", sid)
    agent = await api.get_agent_by_token(auth["token"])
    if agent == {"success": False}:
        log.error("Invalid token: %s", auth["token"])
        return False
    log.info("Agent authenticated: %s", agent["name"])


@sio.on("disconnect")
def disconnect(sid):
    """On disconnected."""
    print("disconnect ", sid)


@sio.on("*")
async def frame(event, sid, data):
    """On frame."""
    print("frame ", event, sid, data)
    await sio.emit(event, data)
