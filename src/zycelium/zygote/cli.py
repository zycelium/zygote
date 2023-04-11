"""
Commandline interface.
"""
import click
import uvicorn
from zycelium.zygote.server import app_tls_cert_path, app_tls_key_path


@click.group()
def cli():
    """Zygote commandline interface."""


@cli.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=3965, help="Port to bind to")
@click.option("--tls/--no-tls", is_flag=True, default=True, help="Enable TLS")
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode")
def serve(host, port, tls, debug):
    """Start the server."""
    log_level = "debug" if debug else "info"
    if tls:
        uvicorn.run(
            "zycelium.zygote.server:app",
            host=host,
            port=port,
            log_level=log_level,
            ssl_keyfile=str(app_tls_key_path),
            ssl_certfile=str(app_tls_cert_path),
        )
    else:
        uvicorn.run(
            "zycelium.zygote.server:app", host=host, port=port, log_level=log_level
        )
