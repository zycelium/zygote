import click

from zycelium import zygote


@click.group()
def main():
    """Zygote: Personal Automation Framework"""
    if zygote.config.app_config_path.exists():
        try:
            zygote.config.load(zygote.config.app_config_path)  # type: ignore
        except zygote.ConfigParseError:
            click.echo(f"Error parsing config file at: {zygote.config.app_config_path}")


@main.command()
def version():
    """Show current version."""
    click.echo(f"Zycelium/Zygote version {zygote.version}")


@main.command()
@click.option("--reset", is_flag=True, default=False, help="Reset config to defaults.")
def config(reset):
    """Edit config."""
    if reset:
        default_config = zygote.DefaultConfig()
        default_config.save(zygote.config.app_config_path, overwrite=True)  # type: ignore

    if not zygote.config.app_config_path.exists():
        zygote.config.save(zygote.config.app_config_path)  # type: ignore

    click.edit(filename=str(zygote.config.app_config_path))


@main.command()
@click.option("--debug", is_flag=True, help="Enable extra logging.")
@zygote.config.click_option()  # type: ignore
def serve(debug: bool):
    """Run Zygote instance."""
    click.echo(f"Debug is {debug}.")
