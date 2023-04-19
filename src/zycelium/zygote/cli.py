"""
Zygote CLI
"""
import asyncio
from pathlib import Path

import click

from zycelium import zygote


@click.group()
@click.option("--conf", "-c", type=click.Path(exists=True), help="Path to config file.")
@click.pass_context
def main(ctx, conf):
    """Zycelium/Zygote: Personal Automation Framework"""
    ctx.ensure_object(dict)
    ctx.obj["conf"] = Path(conf) if conf else None
    if conf:
        try:
            zygote.config.load(conf)  # pylint: disable=no-member # type: ignore
        except zygote.ConfigParseError:
            click.echo(f"Error reading config file at: {conf}")
    else:
        if zygote.config.app_config_path.exists():
            try:
                zygote.config.load(  # pylint: disable=no-member # type: ignore
                    zygote.config.app_config_path
                )
            except zygote.ConfigParseError:
                click.echo(
                    f"Error reading config file at: {zygote.config.app_config_path}"
                )


@main.command()
def version():
    """Show current version."""
    click.echo(f"Zycelium/Zygote version {zygote.version}")


@main.command()
@click.option("--debug", is_flag=True, help="Enable extra logging.")
@zygote.config.click_option()  # pylint: disable=no-member # type: ignore
def serve(debug: bool):
    """Run Zygote instance."""
    click.echo(f"Debug is {debug}.")


@main.group()
def config():
    """Manage config."""


@config.command("password")
@click.option("--current-password", prompt=True, hide_input=True)
@click.option("--new-password", prompt=True, hide_input=True)
def config_password(current_password, new_password):
    """Change config password."""
    if zygote.config.check_password(current_password):
        zygote.config.change_password(new_password)
        zygote.config.save(  # pylint: disable=no-member # type: ignore
            zygote.config.app_config_path, overwrite=True
        )
        click.echo("Admin password updated.")
    else:
        click.echo("Incorrect password.")


@config.command("edit")
@click.pass_obj
def config_edit(obj):
    """Edit config."""
    conf = obj["conf"] or zygote.config.app_config_path
    if not conf.exists():
        zygote.config.save(conf)  # pylint: disable=no-member # type: ignore
    click.edit(filename=str(conf))


@config.command("reset")
@click.option(
    "--yes", "-y", is_flag=True, default=False, help="Accept reset confirmation prompt."
)
@click.pass_obj
def config_reset(obj, yes):
    """Reset config to defaults."""
    conf = obj["conf"] or zygote.config.app_config_path
    click.echo(f"Reset config: {conf}")
    if yes or click.confirm("Are you sure you want to reset config to defaults?"):
        default_config = zygote.DefaultConfig()
        default_config.save(  # pylint: disable=no-member # type: ignore
            conf, overwrite=True
        )
    else:
        click.echo("Config was not modified.")


@main.group()
def peer():
    """Manage peers."""


@peer.command("add")
@click.option("--name", prompt=True)
@click.option("--url", prompt=True)
def peer_add(name, url):
    """Add peer."""
    click.echo(f"Add peer: {name} {url}")

    async def _add():
        await zygote.models.start_database(zygote.config.database_url)
        await zygote.models.Peer.create(name=name, base_url=url)
        await zygote.models.stop_database()

    asyncio.run(_add())


@peer.command("list")
def peer_list():
    """List peers."""

    async def _list():
        await zygote.models.start_database(zygote.config.database_url)
        peers = await zygote.models.Peer.all()
        if not peers:
            click.echo("No peers found.")
            await zygote.models.stop_database()
            return

        click.echo("Peers:")
        for peer in peers:  # pylint: disable=redefined-outer-name
            click.echo(f"{peer.name} {peer.base_url}")
        await zygote.models.stop_database()

    asyncio.run(_list())


@peer.command("remove")
@click.option("--name", prompt=True)
def peer_remove(name):
    """Remove peer."""
    click.echo(f"Remove peer: {name}")

    async def _remove():
        await zygote.models.start_database(zygote.config.database_url)
        try:
            peer = await zygote.models.Peer.get(  # pylint: disable=redefined-outer-name
                name=name
            )
            await peer.delete()
        except zygote.models.DoesNotExist:
            click.echo(f"Peer not found: {name}")
            return
        finally:
            await zygote.models.stop_database()

    asyncio.run(_remove())
