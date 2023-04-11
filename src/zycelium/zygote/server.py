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
from tortoise import Tortoise
from tortoise.query_utils import Prefetch

from zycelium.zygote.logging import get_logger
from zycelium.zygote.models import (
    init_db,
    Frame,
    PydanticFrame,
    PydanticFrameIn,
    PydanticFrameList,
    Space,
    PydanticSpace,
    PydanticSpaceIn,
    PydanticSpaceList,
    Agent,
    PydanticAgent,
    PydanticAgentIn,
    PydanticAgentList,
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


# Helpers


async def get_data_and_redirect_url():
    """Get data and redirect url."""
    data = await request.get_json()
    if not data:
        data = await request.form
    if not data:
        raise ValueError("No data")
    redirect_url = data.get("redirect_url", None)
    if redirect_url:
        # Remove redirect url parameter from immutable data.
        data = data.copy()
        del data["redirect_url"]
    return data, redirect_url


# API


@app.route("/api/v1/frames", methods=["POST"])
async def post_frame():
    """Post frame."""
    spaces = []
    data = await request.get_json()
    if data:
        spaces = data.pop("spaces", [])
    if not data:
        form = await request.form
        spaces = form.getlist("spaces")
        data = form.to_dict()
    if not data:
        return jsonify({"error": "No data."}), 400
    redirect_url = data.get("redirect_url", None)
    if redirect_url:
        # Remove redirect url parameter from immutable data.
        data = data.copy()
        del data["redirect_url"]
    agent = data.pop("agent", None)
    data.pop("spaces", None)
    data = PydanticFrameIn(**data).dict()
    frame = await Frame.create(**data)
    frame.agent = await Agent.get(uuid=agent)  # type: ignore
    for space in spaces:
        # check if agent has joined space
        if not await frame.agent.spaces.filter(uuid=space).exists():
            continue
        await frame.spaces.add(await Space.get(uuid=space))  # type: ignore
    await frame.save()
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


@app.route("/api/v1/frames/<uuid>", methods=["DELETE"])
async def delete_frame(uuid):
    """Delete frame."""
    await Frame.filter(uuid=uuid).delete()
    return jsonify({"success": True})


@app.route("/api/v1/spaces", methods=["POST"])
async def post_space():
    """Post space."""
    try:
        data, redirect_url = await get_data_and_redirect_url()
    except ValueError:
        return jsonify({"error": "No data."}), 400
    data = PydanticSpaceIn(**data).dict()
    space = await Space.create(**data)
    pyspace = await PydanticSpace.from_tortoise_orm(space)
    if redirect_url:
        return redirect(redirect_url)
    return jsonify(pyspace.dict())


@app.route("/api/v1/spaces", methods=["GET"])
async def get_spaces():
    """Get spaces."""
    spaces = await PydanticSpaceList.from_queryset(Space.all().limit(100))
    return jsonify(spaces.dict()["__root__"])


@app.route("/api/v1/spaces/<uuid>", methods=["GET"])
async def get_space(uuid):
    """Get space."""
    space = await Space.get(uuid=uuid)
    pyspace = await PydanticSpace.from_tortoise_orm(space)
    return jsonify(pyspace.dict())


@app.route("/api/v1/spaces/<uuid>", methods=["DELETE"])
async def delete_space(uuid):
    """Delete space."""
    await Space.filter(uuid=uuid).delete()
    return jsonify({"success": True})


@app.route("/api/v1/agents", methods=["POST"])
async def post_agent():
    """Post agent."""
    try:
        data, redirect_url = await get_data_and_redirect_url()
    except ValueError:
        return jsonify({"error": "No data."}), 400
    data = PydanticAgentIn(**data).dict()
    agent = await Agent.create(**data)
    pyagent = await PydanticAgent.from_tortoise_orm(agent)
    if redirect_url:
        return redirect(redirect_url)
    return jsonify(pyagent.dict())


@app.route("/api/v1/agents", methods=["GET"])
async def get_agents():
    """Get agents."""
    agents = await PydanticAgentList.from_queryset(Agent.all().limit(100))
    return jsonify(agents.dict()["__root__"])


@app.route("/api/v1/agents/<uuid>", methods=["GET"])
async def get_agent(uuid):
    """Get agent."""
    agent = await Agent.get(uuid=uuid)
    pyagent = await PydanticAgent.from_tortoise_orm(agent)
    return jsonify(pyagent.dict())


@app.route("/api/v1/agents/<uuid>", methods=["DELETE"])
async def delete_agent(uuid):
    """Delete agent."""
    await Agent.filter(uuid=uuid).delete()
    return jsonify({"success": True})


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
    frames = await Frame.all().limit(100)
    agents = await Agent.all()
    spaces = await Space.all()
    return await render_template(
        "frames.html", frames=frames, agents=agents, spaces=spaces
    )


@app.route("/frames/<uuid>")
async def http_frame(uuid):
    """Frame route."""
    frame = await Frame.get(uuid=uuid).prefetch_related(
        Prefetch("agent", queryset=Agent.all()),
        Prefetch("spaces", queryset=Space.all()),
    )
    return await render_template("frame.html", frame=frame)


@app.route("/spaces")
async def http_spaces():
    """Spaces route."""
    spaces = await Space.all().limit(100)
    return await render_template("spaces.html", spaces=spaces)


@app.route("/spaces/<uuid>")
async def http_space(uuid):
    """Space route."""
    space = await Space.get(uuid=uuid).prefetch_related(
        Prefetch("agents", queryset=Agent.all())
    )
    return await render_template("space.html", space=space)


@app.route("/agents")
async def http_agents():
    """Agents route."""
    agents = await PydanticAgentList.from_queryset(Agent.all().limit(100))
    return await render_template("agents.html", agents=agents.dict()["__root__"])


@app.route("/agents/<uuid>")
async def http_agent(uuid):
    """Agent route."""
    agent = await Agent.get(uuid=uuid).prefetch_related(
        Prefetch("spaces", queryset=Space.all())
    )
    spaces = await Space.all()
    # spaces = await Space.exclude(
    #     agents__uuid=uuid
    # ).all()
    return await render_template("agent.html", agent=agent, spaces=spaces)


@app.route("/agents/<uuid>/join", methods=["POST"])
async def http_agent_join_space(uuid):
    """Agent join space route."""
    form = await request.form
    space_uuid = form.get("space_uuid")
    space = await Space.get(uuid=space_uuid)
    agent = await Agent.get(uuid=uuid)
    await agent.spaces.add(space)
    return redirect(f"/agents/{uuid}")


@app.route("/agents/<uuid>/leave", methods=["POST"])
async def http_agent_leave_space(uuid):
    """Agent leave space route."""
    form = await request.form
    space_uuid = form.get("space_uuid")
    space = await Space.get(uuid=space_uuid)
    agent = await Agent.get(uuid=uuid)
    await agent.spaces.remove(space)
    return redirect(f"/agents/{uuid}")
