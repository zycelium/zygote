"""
Zygote Instance Server.
"""
import asyncio
import hypercorn
import uvicorn

from zycelium.zygote import config as zygote_config
from zycelium.zygote.instance.app import app as zygote_app


def run_hypercorn_server():
    """Run Zygote instance using Hypercorn."""
    hyper_config = hypercorn.Config()
    hyper_config.bind = [
        f"{zygote_config.http_host}:{zygote_config.http_port}"  # pylint: disable=no-member # type: ignore
    ]
    hyper_config.ca_certs = zygote_config.ca_cert_file
    hyper_config.certfile = zygote_config.server_cert_file
    hyper_config.keyfile = zygote_config.server_key_file

    asyncio.run(hypercorn.asyncio.serve(zygote_app, hyper_config))


def run_uvicorn_server():
    """Run Zygote instance using Uvicorn."""
    uvicorn.run(
        "zycelium.zygote.instance.app:app",
        host=zygote_config.http_host,
        port=zygote_config.http_port,
        ssl_ca_certs=zygote_config.ca_cert_file,
        ssl_certfile=zygote_config.server_cert_file,
        ssl_keyfile=zygote_config.server_key_file,
    )
