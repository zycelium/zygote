import asyncio
import click
from zycelium.zygote.server import Server


@click.command()
@click.option("--host", default="localhost", help="Host")
@click.option("--port", default=3965, help="Port")
@click.option("--debug", default=False, help="Debug")
def main(host, port, debug):
    """Zygote App"""
    server = Server(name="zygote", debug=debug)
    asyncio.run(server.start(host=host, port=port))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
