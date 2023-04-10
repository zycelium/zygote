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


def dummy_process(name) -> None:
    """
    A dummy process.
    """
    import time
    import random

    log_ = get_logger(f"zygote.dummy.{name}")
    try:
        while True:
            if random.randint(0, 10) == 2:
                raise RuntimeError("Boom!")
            log_.info("tick")
            time.sleep(3)
    except KeyboardInterrupt:
        pass


@app.before_serving
async def before_serving():
    """Startup hook."""
    log.info("Starting server")
    await sup.add_process("dummy1", dummy_process, "dummy1")
    await sup.add_process("dummy2", dummy_process, "dummy2")
    await sup.add_process("dummy3", dummy_process, "dummy3")
    await sup.add_process("dummy4", dummy_process, "dummy4")
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


@app.route("/processes")
async def processes():
    """List processes."""
    return {"processes": [name for name in sup.processes]}
