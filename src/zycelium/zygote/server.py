"""
Zygote server.
"""
from quart import Quart
from quart_cors import cors

from zycelium.zygote.logging import get_logger
from zycelium.zygote.supervisor import Supervisor

app = Quart(__name__)
app = cors(app, allow_origin="*")

sup = Supervisor()

log = get_logger("zygote.server")


@app.before_serving
async def before_serving():
    """Startup hook."""
    log.info("Starting server")
    await sup.start()


@app.after_serving
async def after_serving():
    """Shutdown hook."""
    log.info("Stopping server")
    await sup.stop()


@app.route("/")
async def index():
    """Index route."""
    return "Hello, World!"
