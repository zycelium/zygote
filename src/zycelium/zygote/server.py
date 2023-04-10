"""
Zygote server.
"""
from os import environ
from pathlib import Path

from tortoise import Tortoise
from click import get_app_dir
from quart import (
    Quart,
    ResponseReturnValue,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
)
from quart_auth import (
    AuthManager,
    AuthUser,
    Unauthorized,
    login_required,
    login_user,
    logout_user,
    current_user,
)
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

ZYGOTE_SECRET_KEY = environ.get("ZYGOTE_SECRET_KEY", None)
if not ZYGOTE_SECRET_KEY:
    raise ValueError("ZYGOTE_SECRET_KEY not set")

app = Quart(__name__)
app.secret_key = ZYGOTE_SECRET_KEY

quart_auth = AuthManager(app)
app = cors(app, allow_origin="*")
app_dir = Path(get_app_dir("zygote"))
app_db_path = "zygote.db"  # pylint: disable=invalid-name

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


@app.errorhandler(Unauthorized)
async def redirect_to_login(*_: Exception) -> ResponseReturnValue:
    """Redirect to login."""
    return redirect(url_for("http_login"))


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
@login_required
async def http_index():
    """Index route."""
    return await render_template("index.html", user=current_user)


@app.route("/login", methods=["GET", "POST"])
async def http_login():
    """Login route."""
    if request.method == "POST":
        form = await request.form
        username = form.get("username")
        password = form.get("password")
        if username == "admin" and password == "admin":
            login_user(AuthUser(auth_id="1"))
            return redirect("/")
        return "Bad username or password", 401
    return await render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
async def http_logout():
    """Logout route."""
    logout_user()
    return redirect("/")


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
