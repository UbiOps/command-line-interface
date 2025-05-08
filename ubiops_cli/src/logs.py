from datetime import datetime, timedelta

import click
import ubiops as api

from ubiops_cli.utils import init_client, get_current_project
from ubiops_cli.src.helpers.formatting import (
    print_item,
    format_logs_reference,
    format_logs_oneline,
    parse_datetime,
    print_list,
    format_json,
    format_datetime,
)
from ubiops_cli.src.helpers import options


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
@click.group(name="logs", short_help="View your logs", invoke_without_command=True)
@click.pass_context
@options.LOGS_START
@options.LOGS_END
@options.LOGS_QUERY
@options.LOGS_LIMIT
@options.LOGS_NO_PAGER
@options.LOGS_FORMATS
def commands(ctx, start, end, query, limit, no_pager, format_):
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


# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
@commands.command(name="list", short_help="List logs [DEPRECATED]")
@options.DEPLOYMENT_NAME_OPTIONAL
@options.DEPLOYMENT_VERSION_OPTIONAL
@options.PIPELINE_NAME_OPTIONAL
@options.PIPELINE_VERSION_OPTIONAL
@options.PIPELINE_OBJECT_NAME
@options.BUILD_ID_OPTIONAL
@options.INSTANCE_ID_OPTIONAL
@options.PROCESS_ID_OPTIONAL
@options.REQUEST_ID_OPTIONAL
@options.PIPELINE_REQUEST_ID_OPTIONAL
@options.SYSTEM
@options.LEVEL
@options.START_DATE
@options.START_LOG
@options.DATE_RANGE
@options.LOGS_LIMIT
@options.LOGS_FORMATS
def logs_list_deprecated(
    start_date,
    start_log,
    date_range,
    limit,
    format_,
    **kwargs,
):
    """
    [DEPRECATED] This method is deprecated, please use `ubiops logs` instead.

    Get the logs of your project.

    Use the command options as filters.
    """

    project_name = get_current_project(error=True)
    client = init_client()

    filters = {}
    for filter_option in LOG_FILTERS:
        input_field = LOG_FILTERS_RENAMED[filter_option] if filter_option in LOG_FILTERS_RENAMED else filter_option
        if kwargs.get(input_field, ""):
            filters[filter_option] = kwargs[input_field]

    if start_date is not None:
        try:
            start_date = format_datetime(parse_datetime(start_date), fmt="%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ValueError(
                "Failed to parse start_date. Please use iso-format, for example, '2020-01-01T00:00:00.000000Z'"
            )
    elif start_date is None and start_log is None:
        start_date = str(datetime.now())

    log_filters = api.LogsCreate(filters=filters, date=start_date, id=start_log, date_range=date_range, limit=limit)
    logs = client.projects_log_list(project_name=project_name, data=log_filters)
    client.api_client.close()

    if format_ == "json":
        click.echo(format_json(logs))
        return

    if len(logs) > 0:
        if format_ == "oneline":
            # Make sure logs are sorted old to new
            logs = list(reversed(logs)) if date_range < 0 else logs
            lines = format_logs_oneline(logs)
            click.echo(lines)
        elif format_ == "reference":
            lines = format_logs_reference(logs)
            click.echo_via_pager(lines)
        elif format_ == "extended":
            lines = format_logs_reference(logs=logs, extended=LOG_FILTERS)
            click.echo_via_pager(lines)
        else:
            lines = format_logs_reference(logs)
            click.echo_via_pager(lines)

    elif start_date:
        starting_point = parse_datetime(start_date).isoformat()
        if date_range > 0:
            end_point = (parse_datetime(start_date) + timedelta(seconds=date_range)).isoformat()
        else:
            end_point = (parse_datetime(start_date) - timedelta(seconds=abs(date_range))).isoformat()
        click.echo(f"No logs found between <{starting_point}> and <{end_point}>")


@commands.command(name="get", short_help="Get details of a log [DEPRECATED]")
@options.LOG_ID
@options.GET_FORMATS
def logs_get(log_id, format_):
    """
    [DEPRECATED] This method is deprecated, please use `ubiops logs` instead.

    \b
    Get more details of a log:
    - date
    - deployment_name
    - deployment_version_name
    - build_id
    - instance_id
    - process_id
    - pipeline_name
    - pipeline_version_name
    - pipeline_object_name
    - deployment_request_id
    - pipeline_request_id
    - system (boolean)
    - level
    """

    project_name = get_current_project(error=True)
    client = init_client()

    log_filters = api.LogsCreate(filters={}, id=log_id, limit=1)
    log = client.projects_log_list(project_name=project_name, data=log_filters)[0]
    log.log = log.log.strip()
    client.api_client.close()

    print_item(
        log,
        row_attrs=["id", "date", "log", "level"],
        required_front=["id", "date", "system"],
        optional=LOG_FILTERS,
        required_end=["log"],
        rename=LOG_FILTERS_RENAMED,
        fmt=format_,
    )


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
