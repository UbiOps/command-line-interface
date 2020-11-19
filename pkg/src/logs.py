import ubiops as api
from datetime import datetime, timedelta

from pkg.utils import init_client, get_current_project
from pkg.src.helpers.formatting import print_item, format_logs_reference, format_logs_oneline, parse_datetime, \
    print_list
from pkg.src.helpers.options import *


@click.group("logs", short_help="View your logs")
def commands():
    """View your logs."""
    pass


@commands.command("list", short_help="List logs")
@DEPLOYMENT_NAME_OPTIONAL
@VERSION_NAME_OPTIONAL
@REQUEST_ID_OPTIONAL
@PIPELINE_REQUEST_ID_OPTIONAL
@SYSTEM
@START_DATE
@START_LOG
@DATE_RANGE
@LIMIT
@LOGS_FORMATS
def logs_list(deployment_name, version_name, request_id, pipeline_request_id, system, start_date, start_log,
              date_range, limit, format_):
    """Get the logs of your project.

    Use the command options as filters.
    """

    project_name = get_current_project(error=True)
    client = init_client()

    filters = {}
    if deployment_name:
        filters['deployment_name'] = deployment_name
    if version_name:
        filters['deployment_version'] = version_name
    if request_id:
        filters['request_id'] = request_id
    if pipeline_request_id:
        filters['pipeline_request_id'] = pipeline_request_id
    if system is not None:
        filters['system'] = system
    if start_date is not None:
        try:
            parse_datetime(start_date)
        except ValueError:
            raise Exception("Failed to parse start_date. Please use iso-format, "
                            "for example, '2020-01-01T00:00:00.000000Z'")
    elif start_date is None and start_log is None:
        start_date = str(datetime.now())
    log_filters = api.LogsCreate(filters=filters, date=start_date, id=start_log, date_range=date_range, limit=limit)
    logs = client.projects_log_list(project_name=project_name, data=log_filters)
    client.api_client.close()

    if len(logs) > 0:
        if format_ == 'oneline':
            lines = format_logs_oneline(logs)
        elif format_ == 'reference':
            lines = format_logs_reference(logs)
        elif format_ == 'extended':
            lines = format_logs_reference(logs, extended=['request_id', 'pipeline_request_id', 'deployment_name',
                                                          'deployment_version', 'pipeline_name',
                                                          'pipeline_object_name'])
        else:
            lines = format_logs_reference(logs)
        click.echo_via_pager(lines)
    elif start_date:
        starting_point = parse_datetime(start_date).isoformat()
        if date_range > 0:
            end_point = parse_datetime(start_date) + timedelta(seconds=date_range)
        else:
            end_point = (parse_datetime(start_date)
                         - timedelta(seconds=abs(date_range))).isoformat()
        click.echo("No logs found between <%s> and <%s>" % (starting_point, end_point))


@commands.command("get", short_help="Get details of a log")
@LOG_ID
@GET_FORMATS
def logs_get(log_id, format_):
    """
    \b
    Get more details of a log:
    - date
    - deployment_name
    - version_name
    - pipeline_name
    - pipeline_object_name
    - request_id
    - pipeline_request_id
    - system (boolean)
    """

    project_name = get_current_project(error=True)
    client = init_client()

    log_filters = api.LogsCreate(filters={}, id=log_id, limit=1)
    log = client.projects_log_list(project_name=project_name, data=log_filters)[0]
    client.api_client.close()

    print_item(
        log,
        row_attrs=['id', 'date', 'log'],
        required_front=['id', 'date', 'system'],
        optional=['request_id', 'pipeline_request_id', 'deployment_name', 'version',
                  'pipeline_name', 'pipeline_object_name'],
        required_end=['log'],
        rename={'version': 'version_name'}, fmt=format_
    )


@click.group(["audit_events", "audit"], short_help="View your audit events")
def audit_events():
    """View your audit events."""
    pass


@audit_events.command("list", short_help="List audit events")
@DEPLOYMENT_NAME_OPTIONAL
@PIPELINE_NAME_OPTIONAL
@AUDIT_LIMIT
@AUDIT_OFFSET
@AUDIT_ACTION
@LIST_FORMATS
def audit_list(deployment_name, pipeline_name, format_, **kwargs):
    """List the audit events.

    Use the command options as filters.
    """

    project_name = get_current_project(error=True)
    client = init_client()

    if deployment_name and pipeline_name:
        raise Exception("Please, filter either on deployment or pipeline name, not both")
    elif deployment_name:
        events = client.deployment_audit_events_list(project_name=project_name, deployment_name=deployment_name,
                                                     **kwargs)
    elif pipeline_name:
        events = client.pipeline_audit_events_list(project_name=project_name, pipeline_name=pipeline_name, **kwargs)
    else:
        events = client.project_audit_events_list(project_name=project_name, **kwargs)
    client.api_client.close()

    print_list(events, ['date', 'action', 'user', 'event'], fmt=format_, pager=len(events) > 10)
