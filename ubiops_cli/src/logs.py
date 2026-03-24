import click

from .helpers.formatting import (
    format_logs_reference,
    format_logs_oneline,
    print_list,
    format_json,
)
from .helpers import options
from ..utils import init_client, get_current_project


LOG_FILTERS = [
    "pipeline_name",
    "pipeline_version",
    "pipeline_object_name",
    "deployment_name",
    "deployment_version",
    "deployment_version_revision_id",
    "environment_name",
    "environment_build_id",
    "instance_id",
    "process_id",
    "pipeline_request_id",
    "deployment_request_id",
    "webhook_name",
    "system",
    "level",
]
LOG_FILTERS_RENAMED = {
    "deployment_version": "deployment_version_name",
    "pipeline_version": "pipeline_version_name",
}


# pylint: disable=too-many-arguments
@click.command(name="logs", short_help="View your logs")
@click.pass_context
@options.LOGS_START
@options.LOGS_END
@options.LOGS_QUERY
@options.LOGS_LIMIT
@options.LOGS_NO_PAGER
@options.LOGS_FORMATS
def logs_list(ctx, start, end, query, limit, no_pager, format_):
    """
    Get the logs of your project.

    If start < end, the logs are searched forward.
    If start > end, the logs are searched backward.

    \b
    Use the `query` option to filter logs.
    e.g. text search:
    ```
    --query '|= "text"'
    ```
    e.g. Deployment filters:
    ```
    --query '| deployment_name="deployment-1" | deployment_version="v1"'
    ```
    e.g. Pipeline filters:
    ```
    --query '| pipeline_name="pipeline-1" | pipeline_version="v1"'
    ```
    e.g. Text search + request filters
    ```
    --query '|= "text" | deployment_request_id="request-id-1"'
    ```

    \b
    Available line filters:
    - `|=` for exact string match
    - `|~` for regex match
    - `!=` for negative exact string match (matched logs will be excluded)
    - `!~` for negative regex match (matched logs will be excluded)

    \b
    Available label filters (come after `|`):
    - `=` for exact match
    - `=~` for regex match
    - `!=` for negative exact match (matched logs will be excluded)
    - `!~` for negative regex match (matched logs will be excluded)

    \b
    Label filters can be chained using connectors `and` (equivalent to `|`) and `or`.
    e.g. Specific deployment version
    ```
    --query '| deployment_name="my-deployment" and deployment_version="v1"'
    ```
    e.g. All logs of request 1 and request 2
    ```
    --query '| deployment_request_id="request-id-1" or deployment_request_id="request-id-2"'
    ```
    """

    # Skip for (deprecated) subcommands 'logs list' and 'logs get'
    if ctx.invoked_subcommand:
        return

    project_name = get_current_project(error=True)
    client = init_client()

    logs = client.logs_list(project_name=project_name, start=start, end=end, query=query, limit=limit)
    client.api_client.close()

    if format_ == "json":
        click.echo(format_json(logs))
        return

    if len(logs) > 0:
        if format_ == "oneline":
            lines = format_logs_oneline(logs)
        elif format_ == "reference":
            lines = format_logs_reference(logs)
        else:  # format_ == "extended"
            lines = format_logs_reference(logs=logs, extended=LOG_FILTERS)

        if no_pager:
            click.echo(lines)
        else:
            click.echo_via_pager(lines)

    elif start and end:
        click.echo(f"No logs found between <{start}> and <{end}>")


@click.group(name=["audit_events", "audit"], short_help="View your audit events")
def audit_events():
    """
    View your audit events.
    """

    return


@audit_events.command(name="list", short_help="List audit events")
@options.DEPLOYMENT_NAME_OPTIONAL
@options.PIPELINE_NAME_OPTIONAL
@options.AUDIT_LIMIT
@options.OFFSET
@options.AUDIT_ACTION
@options.LIST_FORMATS
def audit_list(deployment_name, pipeline_name, format_, **kwargs):
    """
    List the audit events.

    Use the command options as filters.
    """

    project_name = get_current_project(error=True)
    client = init_client()

    if deployment_name and pipeline_name:
        raise AssertionError("Please, filter either on deployment or pipeline name, not both")

    if deployment_name:
        events = client.deployment_audit_events_list(
            project_name=project_name, deployment_name=deployment_name, **kwargs
        )
    elif pipeline_name:
        events = client.pipeline_audit_events_list(project_name=project_name, pipeline_name=pipeline_name, **kwargs)
    else:
        events = client.project_audit_events_list(project_name=project_name, **kwargs)
    client.api_client.close()

    print_list(items=events, attrs=["date", "action", "user", "event"], fmt=format_, pager=len(events) > 10)
