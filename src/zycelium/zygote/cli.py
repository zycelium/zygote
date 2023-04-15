"""
Command-line interface.
"""
import click
import trustme
import uvicorn
from zycelium.zygote.server import app_dir, app_tls_cert_path, app_tls_key_path


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
        if not app_tls_key_path.exists() or not app_tls_cert_path.exists():
            ca = trustme.CA()
            server_cert = ca.issue_cert("localhost")

            ca.cert_pem.write_to_path(str(app_dir / "ca.pem"))
            server_cert.private_key_and_cert_chain_pem.write_to_path(
                str(app_tls_key_path)
            )
            server_cert.cert_chain_pems[0].write_to_path(str(app_tls_cert_path))
            
        uvicorn.run(
            "zycelium.zygote.server:sio_app",
            host=host,
            port=port,
            log_level=log_level,
            ssl_keyfile=str(app_tls_key_path),
            ssl_certfile=str(app_tls_cert_path),
            ssl_ca_certs=str(app_dir / "ca.pem"),
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