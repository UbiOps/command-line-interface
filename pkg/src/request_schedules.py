import ubiops as api

from pkg.utils import get_current_project, init_client, parse_json
from pkg.src.helpers.formatting import print_list, print_item
from pkg.src.helpers.options import *
from pkg.constants import STRUCTURED_TYPE


LIST_ITEMS = ['id', 'name', 'schedule', 'enabled']
RENAME_COLUMNS = {'schedule': 'schedule (in UTC)'}


def get_schedule_object(client, project_name, object_type, object_name):
    if object_type == 'deployment':
        return client.deployments_get(project_name=project_name, deployment_name=object_name)
    elif object_type == 'pipeline':
        return client.pipelines_get(project_name=project_name, pipeline_name=object_name)
    else:
        raise Exception("Object type must be 'deployment' or 'pipeline'")


@click.group("schedules", short_help="Manage your request schedules")
def commands():
    """Manage your request schedules."""
    pass


@commands.command("list", short_help="List schedules")
@LIST_FORMATS
def schedules_list(format_):
    """List request schedules in project."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.request_schedules_list(project_name=project_name)
    client.api_client.close()

    print_list(response, LIST_ITEMS, project_name=project_name, rename_cols=RENAME_COLUMNS, sorting_col=1, fmt=format_)


@commands.command("create", short_help="Create a schedule")
@SCHEDULE_NAME
@OBJECT_TYPE
@OBJECT_NAME
@OBJECT_VERSION
@REQUEST_DATA
@SCHEDULE
@IS_BATCH_REQUEST
@SCHEDULE_TIMEOUT
@IS_ENABLED
@CREATE_FORMATS
def schedules_create(schedule_name, object_type, object_name, object_version, data, format_, **kwargs):
    """Create a new request schedule."""

    project_name = get_current_project(error=True)

    client = init_client()
    obj = get_schedule_object(client, project_name, object_type, object_name)

    if obj.input_type == STRUCTURED_TYPE:
        data = parse_json(data)

    schedule = api.ScheduleCreate(name=schedule_name, object_type=object_type, object_name=object_name,
                                  version=object_version, request_data=data, **kwargs)
    response = client.request_schedules_create(project_name=project_name, data=schedule)
    client.api_client.close()

    print_item(response, LIST_ITEMS, project_name=project_name, rename=RENAME_COLUMNS, fmt=format_)


@commands.command("update", short_help="Update a schedule")
@SCHEDULE_NAME
@SCHEDULE_NAME_UPDATE
@REQUEST_DATA_UPDATE
@SCHEDULE_UPDATE
@IS_BATCH_REQUEST_UPDATE
@SCHEDULE_TIMEOUT_UPDATE
@IS_ENABLED_UPDATE
@CREATE_FORMATS
def schedules_update(schedule_name, new_name, data, format_, **kwargs):
    """Update a request schedule."""

    project_name = get_current_project(error=True)

    client = init_client()

    if data is not None:
        schedule = client.request_schedules_get(project_name=project_name, schedule_name=schedule_name)
        obj = get_schedule_object(client, project_name, schedule.object_type, schedule.object_name)
        if obj.input_type == STRUCTURED_TYPE:
            data = parse_json(data)

    new_schedule = api.ScheduleUpdate(name=new_name, request_data=data,
                                      **{k: v for k, v in kwargs.items() if v is not None})
    response = client.request_schedules_update(project_name=project_name, schedule_name=schedule_name,
                                               data=new_schedule)
    client.api_client.close()

    print_item(response, LIST_ITEMS, project_name=project_name, rename=RENAME_COLUMNS, fmt=format_)


@commands.command("get", short_help="Get a schedule")
@SCHEDULE_NAME
@GET_FORMATS
def schedules_get(schedule_name, format_):
    """Get a request schedule."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.request_schedules_get(project_name=project_name, schedule_name=schedule_name)
    client.api_client.close()

    print_item(response, row_attrs=LIST_ITEMS, project_name=project_name, rename=RENAME_COLUMNS, fmt=format_)


@commands.command("delete", short_help="Delete a schedule")
@SCHEDULE_NAME
@ASSUME_YES
@QUIET
def schedules_delete(schedule_name, assume_yes, quiet):
    """Delete a request schedule."""

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm("Are you sure you want to delete request schedule <%s> "
                                   "of project <%s>?" % (schedule_name, project_name)):
        client = init_client()
        client.request_schedules_delete(project_name=project_name, schedule_name=schedule_name)
        client.api_client.close()

        if not quiet:
            click.echo("Request schedule was successfully deleted")
