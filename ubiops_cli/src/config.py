import click

from ubiops_cli.utils import Config
from ubiops_cli.src.helpers import options


@click.group(name="config", short_help="Manage your CLI configurations")
def commands():
    """Manage your CLI configurations."""

    return


@commands.command(name="list", short_help="List your configurations")
def config_list():
    """List your CLI configurations."""

    click.echo(Config())


@commands.command(name="set", short_help="Set a configuration")
@options.KEY
@options.SET_VALUE
def config_set(key, value):
    """Set a configuration, like, `default.project`."""

    user_config = Config()
    user_config.set(key, value)
    user_config.write()


@commands.command(name="get", short_help="Get a configuration")
@options.KEY
def config_get(key):
    """Get a configuration, like, `default.project`."""

    user_config = Config()
    value = user_config.get(key)
    if value is not None:
        click.echo(value)


@commands.command(name="delete", short_help="Delete a configuration")
@options.KEY
def config_delete(key):
    """Delete a configuration, like, `default.project`."""

    user_config = Config()
    user_config.delete_option(key)
    user_config.write()
