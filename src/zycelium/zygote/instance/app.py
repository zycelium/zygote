"""
Zygote Instance App.
"""
from quart import Quart
from quart_cors import cors


app = Quart(__name__)
app = cors(app, allow_origin="*")


@app.route("/")
async def index():
    """Index."""
    return "Hello, World!"
