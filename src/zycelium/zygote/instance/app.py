"""
Zygote Instance App.
"""
from quart import Quart
from quart_cors import cors

from zycelium.zygote import config


app = Quart(__name__)
app = cors(app, allow_origin=config.server_identities)


@app.route("/")
async def index():
    """Index."""
    return "Hello, World!"
