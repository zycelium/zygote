"""
Frame broker.
"""
import socketio

from zycelium.zygote.api import api
from zycelium.zygote.config import app_config
from zycelium.zygote.frame import Frame
from zycelium.zygote.logging import get_logger

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=app_config.log_level == "debug",
    engineio_logger=app_config.log_level == "debug",
)
log = get_logger("zygote.broker")
SID_AGENT = {}


@sio.on("connect", namespace="/")  # pyright: reportOptionalCall=false
async def connect(sid, _environ, auth: dict):
    """On connected."""

    log.info("Agent connected: %s", sid)

    # Authenticate agent
    try:
        agent = await api.get_agent_by_token(auth["token"])
    except Exception as exc:  # pylint: disable=broad-except
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
    frame = Frame(
        "identity",
        kind="command",
        data={"name": agent["name"], "spaces": agent["spaces"]},
    )
    await sio.emit("command", frame.to_dict(), room=sid)


@sio.on("disconnect", namespace="/")
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
        frame = Frame(
            "identity",
            kind="command",
            data={"name": agent["name"]},
            meta={"spaces": agent["spaces"]},
        )
        await sio.emit("command", frame.to_dict(), room=sid)
    else:
        log.warning("Unknown command: %s", data["name"])


@sio.on("command-config", namespace="/")
async def on_command_config(sid, data):
    """On command config."""
    agent = SID_AGENT[sid]
    if data["name"] == "config":
        agent = await api.get_agent(agent["uuid"])
        if agent["meta"].get("config"):
            config = agent["meta"]["config"]
            data["data"] = {**data["data"], **config}

        agent = await api.update_agent(agent["uuid"], meta={"config": data["data"]})
        SID_AGENT[sid] = agent

        log.info("Agent %s configured.", agent["name"])
        frame = Frame("config", kind="command", data=data["data"])
        await sio.emit("command", frame.to_dict(), room=sid)
    else:
        log.warning("Unknown command: %s", data["name"])


@sio.on("command-config-update", namespace="/")
async def on_command_config_update(sid, data):
    """On command config update."""
    agent = SID_AGENT[sid]
    log.info("Agent %s sent command: %s", agent["name"], data["name"])

    if data["name"] == "config-update":
        agent = await api.get_agent(agent["uuid"])
        config = agent["meta"].get("config", {})
        config.update(data["data"])
        agent = await api.update_agent(agent["uuid"], meta={"config": config})
        SID_AGENT[sid] = agent

        log.info("Agent %s configured: %s", agent["name"], config)
        frame = Frame("config", kind="command", data=config)
        await sio.emit("command", frame.to_dict(), room=sid)
    else:
        log.warning("Unknown command: %s", data["name"])


@sio.on("*", namespace="/")
async def on_frame(event, sid, data):
    """On frame."""
    agent = SID_AGENT[sid]
    spaces = data.pop("spaces", [])
    if not spaces:
        # Use all joined spaces if spaces not specified
        spaces = [s["uuid"] for s in agent["spaces"]]
    else:
        # Filter spaces by name
        spaces = [s["uuid"] for s in agent["spaces"] if s["name"] in spaces]

    frame_name = data["name"]
    kind = data["kind"]
    data["meta"] = {
        "agent": agent["name"],
    }
    if not frame_name:
        raise ValueError("Frame name not specified")

    # Store frame in database
    await api.create_frame(
        kind=kind,
        name=frame_name,
        data=data["data"],
        space_uuids=spaces,
        agent_uuid=agent["uuid"],
    )

    # Broadcast frame to spaces
    frame = Frame(frame_name, kind=kind, data=data["data"])
    for space in spaces:
        await sio.emit(event, frame.to_dict(), room=space)

    log.info(
        "Agent %s sent frame %s to spaces: %s",
        agent["name"],
        frame_name,
        ", ".join(spaces),
    )
