"""
Zygote server.
"""
from pathlib import Path

from tortoise import Tortoise
from click import get_app_dir
from quart import Quart, request, jsonify, render_template, redirect
from quart_cors import cors

from zycelium.zygote.logging import get_logger
from zycelium.zygote.models import (
    init_db,
    Frame,
    PydanticFrame,
    PydanticFrameIn,
    PydanticFrameList,
)
from zycelium.zygote.supervisor import Supervisor

app = Quart(__name__)
app = cors(app, allow_origin="*")
app_dir = Path(get_app_dir("zygote"))
app_db_path = str("zygote.db")  # pylint: disable=invalid-name

sup = Supervisor()
log = get_logger("zygote.server")

# Hooks


@app.before_serving
async def before_serving():
    """Startup hook."""
    log.info("Starting server")
    await init_db(f"sqlite://{app_db_path}")
    await sup.start()


@app.after_serving
async def after_serving():
    """Shutdown hook."""
    log.info("Stopping server")
    await Tortoise.close_connections()
    await sup.stop()


# API


@app.route("/api/v1/frames", methods=["POST"])
async def post_frame():
    """Post frame."""
    data = await request.get_json()
    if not data:
        data = await request.form
    if not data:
        return jsonify({"error": "No data"}), 400
    redirect_url = data.get("redirect_url", None)
    if redirect_url:
        # Remove redirect url parameter from immutable data.
        data = data.copy()
        del data["redirect_url"]
    data = PydanticFrameIn(**data).dict()
    frame = await Frame.create(**data)
    pyframe = await PydanticFrame.from_tortoise_orm(frame)
    if redirect_url:
        return redirect(redirect_url)
    return jsonify(pyframe.dict())


@app.route("/api/v1/frames", methods=["GET"])
async def get_frames():
    """Get frames."""
    frames = await PydanticFrameList.from_queryset(Frame.all().limit(100))
    return jsonify(frames.dict()["__root__"])


@app.route("/api/v1/frames/<uuid>", methods=["GET"])
async def get_frame(uuid):
    """Get frame."""
    frame = await Frame.get(uuid=uuid)
    pyframe = await PydanticFrame.from_tortoise_orm(frame)
    return jsonify(pyframe.dict())


# WebUI


@app.route("/")
async def http_index():
    """Index route."""
    return await render_template("index.html")


@app.route("/frames")
async def http_frames():
    """Frames route."""
    frames = await PydanticFrameList.from_queryset(Frame.all().limit(100))
    return await render_template("frames.html", frames=frames.dict()["__root__"])


@app.route("/frames/<uuid>")
async def http_frame(uuid):
    """Frame route."""
    frame = await Frame.get(uuid=uuid)
    pyframe = await PydanticFrame.from_tortoise_orm(frame)
    return await render_template("frame.html", frame=pyframe.dict())
