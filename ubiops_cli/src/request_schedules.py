import ubiops as api

from ubiops_cli.utils import get_current_project, init_client, parse_json
from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers.options import *
from ubiops_cli.constants import STRUCTURED_TYPE


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
@LABELS_FILTER
def schedules_list(labels, format_):
    """List request schedules in project."""

    label_filter = get_label_filter(labels)
    project_name = get_current_project(error=True)

    client = init_client()
    response = client.request_schedules_list(project_name=project_name, labels=label_filter)
    client.api_client.close()

    print_list(response, LIST_ITEMS, rename_cols=RENAME_COLUMNS, sorting_col=1, fmt=format_)


@commands.command("create", short_help="Create a schedule")
@SCHEDULE_NAME
@OBJECT_TYPE
@OBJECT_NAME
@OBJECT_VERSION
@REQUEST_DATA
@SCHEDULE
@REQUEST_TIMEOUT
@IS_ENABLED
@CREATE_FORMATS
def schedules_create(schedule_name, object_type, object_name, object_version, data, format_, **kwargs):
    """
    Create a new request schedule.
    A batch request will be created to your deployment/pipeline according to the defined schedule.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    obj = get_schedule_object(client, project_name, object_type, object_name)

    if obj.input_type == STRUCTURED_TYPE:
        data = parse_json(data)

    schedule = api.ScheduleCreate(name=schedule_name, object_type=object_type, object_name=object_name,
                                  version=object_version, request_data=data, **kwargs)
    response = client.request_schedules_create(project_name=project_name, data=schedule)
    client.api_client.close()

    print_item(response, LIST_ITEMS, rename=RENAME_COLUMNS, fmt=format_)


@commands.command("update", short_help="Update a schedule")
@SCHEDULE_NAME
@SCHEDULE_NAME_UPDATE
@REQUEST_DATA_UPDATE
@SCHEDULE_UPDATE
@REQUEST_TIMEOUT
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

    print_item(response, LIST_ITEMS, rename=RENAME_COLUMNS, fmt=format_)


@commands.command("get", short_help="Get a schedule")
@SCHEDULE_NAME
@GET_FORMATS
def schedules_get(schedule_name, format_):
    """Get a request schedule."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.request_schedules_get(project_name=project_name, schedule_name=schedule_name)
    client.api_client.close()

    print_item(response, row_attrs=LIST_ITEMS, rename=RENAME_COLUMNS, fmt=format_)


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
