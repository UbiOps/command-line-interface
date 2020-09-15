from pkg.src.helpers.options import *


@click.group("config")
def commands():
    """Manage your UbiOps CLI configurations."""
    pass


@commands.command("list")
def config_list():
    """List your UbiOps CLI configurations."""
    click.echo(Config())


@commands.command("set")
@KEY
@SET_VALUE
def config_set(key, value):
    """Set a configuration, like, `default.project`."""
    user_config = Config()
    user_config.set(key, value)
    user_config.write()


@commands.command("get")
@KEY
def config_get(key):
    """Get a configuration, like, `default.project`."""
    user_config = Config()
    value = user_config.get(key)
    if value is not None:
        click.echo(value)


@commands.command("delete")
@KEY
def config_delete(key):
    """Delete a configuration, like, `default.project`."""
    user_config = Config()
    user_config.delete_option(key)
    user_config.write()
