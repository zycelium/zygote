"""
Frame broker.
"""
import socketio

from zycelium.zygote.logging import get_logger
from zycelium.zygote.api import api

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
log = get_logger("zygote.broker")
SID_AGENT = {}


@sio.on("connect")
async def connect(sid, _environ, auth: dict):
    """On connected."""

    log.info("Agent connected: %s", sid)

    # Authenticate agent
    agent = await api.get_agent_by_token(auth["token"])
    if agent == {"success": False}:
        log.error("Invalid token: %s", auth["token"])
        return False
    log.info("Agent authenticated: %s", agent["name"])

    # Store agent
    SID_AGENT[sid] = agent

    # Add agent to spaces
    for space in agent["spaces"]:
        sio.enter_room(sid, space["uuid"])
        log.info("Agent %s joined space %s", agent["name"], space["name"])

    # Send command: identity
    await sio.emit(
        "command",
        {"name": "identity", "data": {"name": agent["name"], "spaces": agent["spaces"]}},
        room=sid,
    )


@sio.on("disconnect")
def disconnect(sid):
    """On disconnected."""
    agent = SID_AGENT.pop(sid, None)
    log.info("Agent disconnected: %s", agent["name"] if agent else sid)


@sio.on("*")
async def frame(event, sid, data):
    """On frame."""
    # Store frames in database
    # broadcast to all joined spaces if space not specified
    agent = SID_AGENT[sid]

    print("frame ", event, agent["name"], data)
    await sio.emit(event, data)
