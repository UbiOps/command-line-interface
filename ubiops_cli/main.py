import sys
import ubiops as api
import click
import json

from ubiops_cli.version import VERSION
import ubiops_cli.src.projects as projects
import ubiops_cli.src.deployments as deployments
import ubiops_cli.src.deployment_versions as deployment_versions
import ubiops_cli.src.deployment_revisions as deployment_revisions
import ubiops_cli.src.deployment_builds as deployment_builds
import ubiops_cli.src.environments as environments
import ubiops_cli.src.environment_revisions as environment_revisions
import ubiops_cli.src.environment_builds as environment_builds
import ubiops_cli.src.exports as exports
import ubiops_cli.src.imports as imports
import ubiops_cli.src.pipelines as pipelines
import ubiops_cli.src.pipeline_versions as pipeline_versions
import ubiops_cli.src.blobs as blobs
import ubiops_cli.src.buckets as buckets
import ubiops_cli.src.files as files
import ubiops_cli.src.logs as logs
import ubiops_cli.src.config as config
import ubiops_cli.src.auth as auth
import ubiops_cli.src.environment_variables as env_vars
import ubiops_cli.src.request_schedules as schedules
import ubiops_cli.src.validation as validation
import ubiops_cli.src.run_local as runlocal
from ubiops_cli.src.helpers.click_helpers import CustomGroup

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(cls=CustomGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option(VERSION, prog_name="UbiOps CLI")
def cli():
    """UbiOps command line interface (CLI)"""
    pass


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
cli.add_command(env_vars.commands)
cli.add_command(logs.commands)
cli.add_command(logs.audit_events)
cli.add_command(schedules.commands)
cli.add_command(exports.commands)
cli.add_command(imports.commands)
cli.add_command(validation.commands)
cli.add_command(runlocal.deployment_run_local)


def print_error(msg, status=None):
    if status:
        click.secho("Error (%s): %s" % (status, msg), fg="red")
    else:
        click.secho("Error: %s" % msg, fg="red")
    sys.exit(1)


def main():
    try:
        cli()
    except api.exceptions.ApiException as e:
        if hasattr(e, 'get_body_message'):
            print_error(e.get_body_message(), status=getattr(e, "status", None))

        elif hasattr(e, 'body') and e.body is not None:
            try:
                message = json.loads(e.body)
                if 'error' in message:
                    print_error(message['error'])
                elif 'error_message' in message:
                    print_error(message['error_message'])
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
