"""
Frame broker.
"""
import socketio

from zycelium.zygote.logging import get_logger
from zycelium.zygote.api import api

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
log = get_logger("zygote.broker")
SID_AGENT = {}


@sio.on("connect")  # pyright: reportOptionalCall=false
async def connect(sid, _environ, auth: dict):
    """On connected."""

    log.info("Agent connected: %s", sid)

    # Authenticate agent
    try:
        agent = await api.get_agent_by_token(auth["token"])
    except Exception as exc:
        log.error("Error getting agent by token: %s", exc)
        return False
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
        {
            "name": "identity",
            "data": {"name": agent["name"], "spaces": agent["spaces"]},
        },
        room=sid,
    )


@sio.on("disconnect")
def disconnect(sid):
    """On disconnected."""
    agent = SID_AGENT.pop(sid, None)
    log.info("Agent disconnected: %s", agent["name"] if agent else sid)


@sio.on("command-identity", namespace="/")
async def on_command_identity(sid, data):
    """On command identity."""

    agent = SID_AGENT[sid]
    log.info("Agent %s sent command: %s", agent["name"], data["name"])

    if data["name"] == "identity":
        await sio.emit(
            "command",
            {
                "name": "identity",
                "data": {"name": agent["name"], "spaces": agent["spaces"]},
            },
            room=sid,
        )
    else:
        log.warning("Unknown command: %s", data["name"])


@sio.on("command-config", namespace="/")
async def on_command_config(sid, data):
    """On command config."""
    agent = SID_AGENT[sid]
    log.info("Agent %s sent command: %s", agent["name"], data["name"])

    if data["name"] == "config":
        log.info("Agent %s configured: %s", agent["name"], data["data"])
        await sio.emit(
            "command",
            {
                "name": "config",
                "data": data["data"],
            },
            room=sid,
        )
    else:
        log.warning("Unknown command: %s", data["name"])


@sio.on("*", namespace="/")
async def on_frame(event, sid, frame):
    """On frame."""
    agent = SID_AGENT[sid]
    spaces = frame.pop("spaces", [])
    if not spaces:
        # Use all joined spaces if spaces not specified
        spaces = [s["uuid"] for s in agent["spaces"]]
    else:
        # Filter spaces by name
        spaces = [s["uuid"] for s in agent["spaces"] if s["name"] in spaces]

    frame_name = frame["name"]
    kind = frame["kind"]
    frame["meta"] = {
        "agent": agent["name"],
    }
    if not frame_name:
        raise ValueError("Frame name not specified")

    # Store frame in database
    await api.create_frame(
        kind=kind,
        name=frame_name,
        data=frame["data"],
        space_uuids=spaces,
        agent_uuid=agent["uuid"],
    )

    # Broadcast frame to spaces
    for space in spaces:
        await sio.emit(event, frame, room=space)

    log.info(
        "Agent %s emitted frame %s to spaces: %s",
        agent["name"],
        frame_name,
        ", ".join(spaces),
    )
