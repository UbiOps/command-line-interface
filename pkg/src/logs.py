import ubiops as api
from datetime import datetime, timedelta

from pkg.utils import init_client, get_current_project
from pkg.src.helpers.formatting import print_item, format_logs_reference, format_logs_oneline
from pkg.src.helpers.options import *


@click.group("logs")
def commands():
    """Manage your blobs."""
    pass


@commands.command("list")
@MODEL_NAME_OPTIONAL
@VERSION_NAME_OPTIONAL
@REQUEST_ID_OPTIONAL
@PIPELINE_REQUEST_ID_OPTIONAL
@SYSTEM
@START_DATE
@START_LOG
@DATE_RANGE
@LIMIT
@LOGS_FORMATS
def logs_list(model_name, version_name, request_id, pipeline_request_id, system, start_date, start_log,
              date_range, limit, format_):
    """Get the logs of your project.

    Use the command options as filters.
    """

    project_name = get_current_project(error=True)
    client = init_client()

    filters = {}
    if model_name:
        filters['model_name'] = model_name
    if version_name:
        filters['model_version'] = version_name
    if request_id:
        filters['request_id'] = request_id
    if pipeline_request_id:
        filters['pipeline_request_id'] = pipeline_request_id
    if system is not None:
        filters['system'] = system
    if start_date is not None:
        try:
            datetime.fromisoformat(start_date)
        except ValueError:
            raise Exception("Failed to parse start_date. Please use iso-format, "
                            "for example, '2020-01-01T00:00:00.000000Z'")
    elif start_date is None and start_log is None:
        start_date = str(datetime.now())
    log_filters = api.models.LogsCreate(filters=filters, date=start_date, id=start_log,
                                        date_range=date_range, limit=limit)
    logs = client.projects_log_list(project_name=project_name, data=log_filters)
    if len(logs) > 0:
        if format_ == 'oneline':
            lines = format_logs_oneline(logs)
        elif format_ == 'reference':
            lines = format_logs_reference(logs)
        elif format_ == 'extended':
            lines = format_logs_reference(logs, extended=['request_id', 'pipeline_request_id', 'model_name',
                                                          'model_version', 'connector_name', 'pipeline_name',
                                                          'pipeline_object_name'])
        else:
            lines = format_logs_reference(logs)
        click.echo_via_pager(lines)
    elif start_date:
        starting_point = datetime.fromisoformat(start_date).isoformat(' ', 'seconds')
        if date_range > 0:
            end_point = datetime.fromisoformat(start_date) + timedelta(seconds=date_range)
        else:
            end_point = (datetime.fromisoformat(start_date)
                         - timedelta(seconds=abs(date_range))).isoformat(' ', 'seconds')
        click.echo("No logs found between <%s> and <%s>" % (starting_point, end_point))


@commands.command("get")
@LOG_ID
@GET_FORMATS
def logs_list(log_id, format_):
    """
    \b
    Get more details of a log:
    - date
    - model_name
    - model_version
    - connector_name
    - pipeline_name
    - pipeline_object_name
    - request_id
    - pipeline_request_id
    - system (boolean)
    """

    project_name = get_current_project(error=True)
    client = init_client()

    log_filters = api.models.LogsCreate(filters={}, id=log_id, limit=1)
    log = client.projects_log_list(project_name=project_name, data=log_filters)[0]
    print_item(
        log,
        row_attrs=['id', 'date', 'log'],
        required_front=['id', 'date', 'system'],
        optional=['request_id', 'pipeline_request_id', 'model_name', 'model_version', 'connector_name',
                  'pipeline_name', 'pipeline_object_name'],
        required_end=['log'],
        rename={'model_version': 'version_name'}, fmt=format_
    )
