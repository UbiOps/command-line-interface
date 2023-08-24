import json
import sys

import click

import ubiops as api

from ubiops_cli.src import auth, blobs, buckets, config, deployment_builds, deployment_revisions, deployment_versions, \
    deployments, environment_builds, environment_revisions, environment_variables, environments, exports, files, \
    imports, pipelines, pipeline_versions, projects, logs, run_local, request_schedules, validation
from ubiops_cli.src.helpers.click_helpers import CustomGroup
from ubiops_cli.version import VERSION

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.group(cls=CustomGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option(VERSION, prog_name="UbiOps CLI")
def cli():
    """UbiOps command line interface (CLI)"""

    return


cli.add_command(auth.signin)
cli.add_command(auth.status)
cli.add_command(auth.user)
cli.add_command(auth.signout)
cli.add_command(config.commands)
cli.add_command(projects.current_project)
cli.add_command(projects.commands)
cli.add_command(deployments.commands)
cli.add_command(deployment_versions.commands)
cli.add_command(deployment_revisions.commands)
cli.add_command(deployment_builds.commands)
cli.add_command(environments.commands)
cli.add_command(environment_revisions.commands)
cli.add_command(environment_builds.commands)
cli.add_command(pipelines.commands)
cli.add_command(pipeline_versions.commands)
cli.add_command(blobs.commands)
cli.add_command(buckets.commands)
cli.add_command(files.commands)
cli.add_command(environment_variables.commands)
cli.add_command(logs.commands)
cli.add_command(logs.audit_events)
cli.add_command(request_schedules.commands)
cli.add_command(exports.commands)
cli.add_command(imports.commands)
cli.add_command(validation.commands)
cli.add_command(run_local.deployment_run_local)


def print_error(msg, status=None):
    """
    Format errors and print to screen

    :param msg: the error to print
    :param int|None status: the error status code
    """

    if status:
        click.secho(message=f"Error ({status}): {msg}", fg="red")
    else:
        click.secho(message=f"Error: {msg}", fg="red")
    sys.exit(1)


# pylint: disable=broad-except
def main():
    """
    Main function to start click and handle exceptions
    """

    try:
        cli()
    except api.exceptions.ApiException as e:
        if hasattr(e, 'get_body_message'):
            print_error(e.get_body_message(), status=getattr(e, "status", None))

        elif hasattr(e, 'body') and e.body is not None:
            try:
                message = json.loads(e.body)
                if 'error' in message:
                    print_error(msg=message['error'])
                elif 'error_message' in message:
                    print_error(msg=message['error_message'])
                else:
                    print_error(msg=message)
            except json.JSONDecodeError:
                if hasattr(e, "status") and hasattr(e, "reason"):
                    print_error(msg=e.reason, status=e.status)
                else:
                    print_error(msg="an unknown error occurred.")
        else:
            print_error(msg=e)
    except Exception as e:
        print_error(msg=e)


if __name__ == '__main__':
    main()
