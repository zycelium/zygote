"""
Zygote server.
"""
import json
from pathlib import Path

import socketio
from click import get_app_dir
from quart import (
    Quart,
    ResponseReturnValue,
    jsonify,
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
from quart_uploads import configure_uploads, UploadSet, ALL, UploadNotAllowed

from zycelium.zygote.api import api
from zycelium.zygote.broker import sio
from zycelium.zygote.config import app_config
from zycelium.zygote.logging import get_logger
from zycelium.zygote.plugin import discover_agents, start_agent
from zycelium.zygote.supervisor import Supervisor
from zycelium.zygote.utils import secret_key, py_string_to_dict

app_dir = Path(get_app_dir("zygote"))
app_db_path = app_dir / "zygote.db"
app_files_path = app_dir / "files"

app = Quart(__name__)
app.secret_key = secret_key(app_dir / "secret_key")
app.config["UPLOADS_DEFAULT_DEST"] = app_files_path

file_store = UploadSet("files", ALL)  # type: ignore
configure_uploads(app, file_store)

quart_auth = AuthManager(app)
app = cors(app, allow_origin="*")

sio_app = socketio.ASGIApp(sio, app)

sup = Supervisor()
log = get_logger("zygote.server")

# Utils


async def provision_and_start_agent(
    agent_name: str, host: str, port: int, tls: bool
) -> None:
    """Start an agent."""
    log.info("Starting agent %s", agent_name)
    url = f"{'https' if tls else 'http'}://{host}:{port}"
    agent = await api.get_agent_by_name(agent_name.split(".")[-1])
    if agent != {"success": False}:
        tokens = await api.get_auth_tokens_for_agent(agent["uuid"])
        if tokens:
            token = tokens["tokens"][0]["token"]
            auth = {"token": token}
        else:
            log.error("Creating token for agent: %s", agent_name)
            token = await api.create_auth_token(agent["uuid"])
            auth = {"token": token["token"]}
    else:
        log.error("Creating agent in database: %s", agent_name)
        agent = await api.create_agent(agent_name.split(".")[-1])
        token = await api.create_auth_token(agent["uuid"])
        auth = {"token": token["token"]}

    await sup.add_process(agent_name, start_agent, agent_name, url=url, auth=auth)


# Hooks


@app.before_serving
async def before_serving():
    """Startup hook."""
    log.info("Starting server")

    await api.start(f"sqlite://{app_db_path}")
    for agent_name in discover_agents():
        await provision_and_start_agent(
            agent_name,
            host=app_config.host,
            port=app_config.port,
            tls=app_config.tls_enable,
        )
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
    agent["data"] = json.dumps(agent["data"], indent=0)
    agent["meta"] = json.dumps(agent["meta"], indent=0)
    spaces = (await api.get_spaces())["spaces"]
    tokens = (await api.get_auth_tokens_for_agent(uuid))["tokens"]
    return await render_template(
        "agent.html", agent=agent, spaces=spaces, tokens=tokens
    )


@app.route("/agents/<uuid>/update", methods=["POST"])
@login_required
async def http_agent_update(uuid):
    """Agent update route."""
    form = await request.form
    name = form.get("name", None)
    data = form.get("data", None)
    meta = form.get("meta", None)
    if data:
        data = py_string_to_dict(data)
    if meta:
        meta = py_string_to_dict(meta)
    await api.update_agent(uuid, name=name, data=data, meta=meta)
    return redirect(f"/agents/{uuid}")


@app.route("/agents/<uuid>/delete", methods=["POST"])
@login_required
async def http_agent_delete(uuid):
    """Agent delete route."""
    await api.delete_agent(uuid)
    return redirect("/agents")


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


@app.route("/agents/<uuid>/token", methods=["POST"])
@login_required
async def http_agent_create_auth_token(uuid):
    """Agent create auth token route."""
    await api.create_auth_token(uuid)
    return redirect(f"/agents/{uuid}")


@app.route("/agents/<uuid>/token/<token_uuid>/delete", methods=["POST"])
@login_required
async def http_agent_delete_auth_token(uuid, token_uuid):
    """Agent delete auth token route."""
    await api.delete_auth_token(token_uuid)
    return redirect(f"/agents/{uuid}")


@app.route("/files", methods=["GET", "POST"])
async def http_files():
    """Files route."""
    try:
        if request.method == "POST":
            files = await request.files
            form = await request.form
            log.info("Form: %s", form)
            log.info("Files: %s", files)
            file = files["file"]
            name = file.filename
            try:
                path = await file_store.save(file)
            except UploadNotAllowed as exc:
                return await render_template("files.html", error=str(exc))

            await api.create_file(
                name=name,
                path=path,
                meta={
                    "content_type": file.content_type,
                    "content_length": file.content_length,
                },
            )
            return redirect("/files")

        files = (await api.get_files())["files"]
        if request.headers.get("Accept") == "application/json":
            return jsonify(files)
        return await render_template("files.html", files=files)
    except Exception as exc:  # pylint: disable=broad-except
        log.exception(exc)
        return await render_template("files.html", error=str(exc))


@app.route("/files/<uuid>")
async def http_file(uuid):
    """File route."""
    file = await api.get_file(uuid)
    if request.headers.get("Accept") == "application/json":
        return jsonify(file)
    return await render_template("file.html", file=file)


@app.route("/files/<uuid>/delete", methods=["POST"])
async def http_file_delete(uuid):
    """File delete route."""
    await api.delete_file(uuid)
    return redirect("/files")


@app.route("/files/<uuid>/download")
async def http_file_download(uuid):
    """File download route."""
    file = await api.get_file(uuid)
    return redirect(file_store.url(file["name"]))