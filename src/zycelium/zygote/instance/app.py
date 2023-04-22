"""
Zygote Instance App.
"""
from quart import Quart
from quart_cors import cors

from zycelium.zygote import config
from zycelium.zygote.discovery import LocalDNS

app = Quart(__name__)
app = cors(app, allow_origin=config.server_identities)


@app.before_serving
async def before_serving():
    """Before serving."""
    app.local_dns = LocalDNS()
    await app.local_dns.start(
        domain=config.server_default_identity,
        host=config.http_host,
        port=config.http_port,
    )


@app.after_serving
async def after_serving():
    """After serving."""
    await app.local_dns.stop()


@app.route("/")
async def index():
    """Index."""
    return "Hello, World!"
