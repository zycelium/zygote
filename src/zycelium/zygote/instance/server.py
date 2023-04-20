"""
Zygote Instance Server.
"""
import uvicorn


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
