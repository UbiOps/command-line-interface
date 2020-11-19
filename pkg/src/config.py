from pkg.src.helpers.options import *


@click.group("config", short_help="Manage your CLI configurations")
def commands():
    """Manage your CLI configurations."""
    pass


@commands.command("list", short_help="List your configurations")
def config_list():
    """List your CLI configurations."""
    click.echo(Config())


@commands.command("set", short_help="Set a configuration")
@KEY
@SET_VALUE
def config_set(key, value):
    """Set a configuration, like, `default.project`."""
    user_config = Config()
    user_config.set(key, value)
    user_config.write()


@commands.command("get", short_help="Get a configuration")
@KEY
def config_get(key):
    """Get a configuration, like, `default.project`."""
    user_config = Config()
    value = user_config.get(key)
    if value is not None:
        click.echo(value)


@commands.command("delete", short_help="Delete a configuration")
@KEY
def config_delete(key):
    """Delete a configuration, like, `default.project`."""
    user_config = Config()
    user_config.delete_option(key)
    user_config.write()
