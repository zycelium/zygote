"""
Command-line interface.
"""
import click
import uvicorn

from zycelium.zygote.crypto import ensure_tls_certificate_chain
from zycelium.zygote.server import app_dir


@click.group()
def cli():
    """Zygote command-line interface."""


@cli.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=3965, help="Port to bind to")
@click.option("--tls/--no-tls", is_flag=True, default=True, help="Enable TLS")
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode")
def serve(host, port, tls, debug):
    """Start the server."""
    log_level = "debug" if debug else "info"
    if tls:
        certificate_paths = ensure_tls_certificate_chain("localhost", app_dir, 365)
        uvicorn.run(
            "zycelium.zygote.server:sio_app",
            host=host,
            port=port,
            log_level=log_level,
            ssl_keyfile=str(certificate_paths.key),
            ssl_certfile=str(certificate_paths.cert),
            ssl_ca_certs=str(certificate_paths.ca),
        )
    else:
        uvicorn.run(
            "zycelium.zygote.server:app", host=host, port=port, log_level=log_level
        )


@cli.command()
def destroy():
    """Destroy the database."""
    from zycelium.zygote.server import app_db_path

    app_db_path.unlink()
    click.echo("Database destroyed")
