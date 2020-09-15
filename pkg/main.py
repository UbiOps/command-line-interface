import ubiops as api
import click
import json

from pkg.version import VERSION
import pkg.src.projects as projects
import pkg.src.models as models
import pkg.src.model_versions as model_versions
import pkg.src.pipelines as pipelines
import pkg.src.blobs as blobs
import pkg.src.logs as logs
import pkg.src.config as config
import pkg.src.auth as auth
import pkg.src.environment_variables as env_vars

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(VERSION, prog_name="UbiOps CLI")
def cli():
    """UbiOps command line interface."""
    pass


cli.add_command(auth.signin)
cli.add_command(auth.status)
cli.add_command(auth.user)
cli.add_command(auth.signout)
cli.add_command(config.commands)
cli.add_command(projects.current_project)
cli.add_command(projects.commands)
cli.add_command(models.commands)
cli.add_command(model_versions.commands)
cli.add_command(pipelines.commands)
cli.add_command(blobs.commands)
cli.add_command(env_vars.commands)
cli.add_command(logs.commands)


def print_error(msg, status=None):
    if status:
        click.secho("Error (%s): %s" % (status, msg), fg="red")
    else:
        click.secho("Error: %s" % msg, fg="red")


def main():
    try:
        cli()
    except api.exceptions.ApiException as e:
        if hasattr(e, 'body'):
            try:
                message = json.loads(e.body)
                if 'error' in message:
                    print_error(message['error'])
                else:
                    print_error(message)
            except json.JSONDecodeError:
                if hasattr(e, "status") and hasattr(e, "reason"):
                    print_error(e.reason, status=e.status)
                else:
                    print_error("an unknown error occurred.")
        else:
            print_error(e)
    except Exception as e:
        print_error(e)


if __name__ == '__main__':
    main()
