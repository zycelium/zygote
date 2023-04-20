"""
Zygote Instance Server.
"""
import asyncio
import hypercorn
import uvicorn

from zycelium.zygote import config as zygote_config
from zycelium.zygote.instance.app import app as zygote_app


def run_server(host: str, port: int, ca_cert: str, server_cert: str, server_key: str):
    """Run Zygote instance using Uvicorn."""
    uvicorn.run(
        "zycelium.zygote.instance.app:app",
        host=host,
        port=port,
        ssl_ca_certs=ca_cert,
        ssl_certfile=server_cert,
        ssl_keyfile=server_key,
    )
