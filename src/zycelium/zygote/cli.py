"""
Zygote CLI
"""
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
