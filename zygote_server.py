import asyncio
from pathlib import Path

import click
from zycelium.zygote.server import Server



@click.group()
def main():
    """Zygote Server"""


@main.command()
@click.option("--host", default="localhost", help="Host")
@click.option("--port", default=3965, help="Port")
@click.option("--debug", default=False, help="Debug")
def serve(host, port, debug):
    """Run Zygote Server"""
    server = Server(name="zygote", debug=debug)
    asyncio.run(server.start(host=host, port=port))


@main.command()
@click.argument("agent")
def config(agent):
    """Edit config file for agent in user's EDITOR."""
    config_path = click.get_app_dir("zygote")
    config_file = Path(config_path).joinpath(f"{agent}.json")
    if config_file.exists():
        click.edit(filename=str(config_file))
    else:
        click.echo(f"Config file for agent {agent} does not exist.")



if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
