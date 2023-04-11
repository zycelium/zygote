"""
Zygote server.
"""
from os import environ
from pathlib import Path

from click import get_app_dir
from quart import (
    Quart,
    ResponseReturnValue,
    request,
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

from zycelium.zygote.api import ZygoteAPI
from zycelium.zygote.logging import get_logger
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
api = ZygoteAPI()

# Hooks


@app.before_serving
async def before_serving():
    """Startup hook."""
    log.info("Starting server")
    await api.start(f"sqlite://{app_db_path}")
    await sup.start()


@app.after_serving
async def after_serving():
    """Shutdown hook."""
    log.info("Stopping server")
    await api.stop()
    await sup.stop()


@app.errorhandler(Unauthorized)
async def redirect_to_login(*_: Exception) -> ResponseReturnValue:
    """Redirect to login."""
    return redirect(url_for("http_login"))


# Helpers

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


@app.route("/frames", methods=["GET", "POST"])
@login_required
async def http_frames():
    """Frames route."""
    if request.method == "POST":
        form = await request.form
        kind = form["kind"]
        name = form["name"]
        data = form["data"]
        agent = form["agent"]
        spaces = form.getlist("spaces")
        frame = await api.create_frame(
            kind=kind, name=name, data=data, agent_uuid=agent, space_uuids=spaces
        )
        return redirect(f"/frames/{frame['uuid']}")

    frames = (await api.get_frames())["frames"]
    agents = (await api.get_agents())["agents"]
    spaces = (await api.get_spaces())["spaces"]
    return await render_template(
        "frames.html", frames=frames, agents=agents, spaces=spaces
    )


@app.route("/frames/<uuid>")
@login_required
async def http_frame(uuid):
    """Frame route."""
    frame = await api.get_frame(uuid)
    return await render_template("frame.html", frame=frame)


@app.route("/frames/<uuid>/delete", methods=["POST"])
@login_required
async def http_frame_delete(uuid):
    """Frame delete route."""
    await api.delete_frame(uuid)
    return redirect("/frames")


@app.route("/spaces", methods=["GET", "POST"])
@login_required
async def http_spaces():
    """Spaces route."""
    if request.method == "POST":
        form = await request.form
        name = form["name"]
        data = form["data"]
        meta = form["meta"]
        space = await api.create_space(name=name, data=data, meta=meta)
        return redirect(f"/spaces/{space['uuid']}")

    spaces = (await api.get_spaces())["spaces"]
    return await render_template("spaces.html", spaces=spaces)


@app.route("/spaces/<uuid>")
@login_required
async def http_space(uuid):
    """Space route."""
    space = await api.get_space(uuid)
    return await render_template("space.html", space=space)


@app.route("/agents", methods=["GET", "POST"])
@login_required
async def http_agents():
    """Agents route."""
    if request.method == "POST":
        form = await request.form
        name = form["name"]
        data = form["data"]
        meta = form["meta"]
        agent = await api.create_agent(name=name, data=data, meta=meta)
        return redirect(f"/agents/{agent['uuid']}")

    agents = (await api.get_agents())["agents"]
    return await render_template("agents.html", agents=agents)


@app.route("/agents/<uuid>")
@login_required
async def http_agent(uuid):
    """Agent route."""
    agent = await api.get_agent(uuid)
    spaces = (await api.get_spaces())["spaces"]
    return await render_template("agent.html", agent=agent, spaces=spaces)


@app.route("/agents/<uuid>/join", methods=["POST"])
@login_required
async def http_agent_join_space(uuid):
    """Agent join space route."""
    form = await request.form
    space_uuid = form["space_uuid"]
    await api.join_space(space_uuid, uuid)
    return redirect(f"/agents/{uuid}")


@app.route("/agents/<uuid>/leave", methods=["POST"])
@login_required
async def http_agent_leave_space(uuid):
    """Agent leave space route."""
    form = await request.form
    space_uuid = form["space_uuid"]
    await api.leave_space(space_uuid, uuid)
    return redirect(f"/agents/{uuid}")
