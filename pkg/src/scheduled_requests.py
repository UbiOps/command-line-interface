import ubiops as api
import json

from pkg.utils import get_current_project, init_client
from pkg.src.helpers.formatting import print_list, print_item
from pkg.src.helpers.options import *
from pkg.constants import STRUCTURED_TYPE


LIST_ITEMS = ['id', 'name', 'schedule', 'enabled']
RENAME_COLUMNS = {'schedule': 'schedule (in UTC)'}


def get_schedule_object(client, project_name, object_type, object_name):
    if object_type == 'model':
        return client.models_get(project_name=project_name, model_name=object_name)
    elif object_type == 'pipeline':
        return client.pipelines_get(project_name=project_name, pipeline_name=object_name)
    else:
        raise Exception("Object type must be 'model' or 'pipeline'.")


@click.group("schedules")
def commands():
    """Manage your request schedules."""
    pass


@commands.command("list")
@LIST_FORMATS
def scheduled_requests_list(format_):
    """List request schedules in project."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.scheduled_requests_list(project_name=project_name)
    print_list(response, LIST_ITEMS, project_name=project_name, rename_cols=RENAME_COLUMNS, sorting_col=1, fmt=format_)


@commands.command("create")
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
def scheduled_requests_create(schedule_name, object_type, object_name, object_version, data, format_, **kwargs):
    """Create a new request schedule."""

    project_name = get_current_project(error=True)

    client = init_client()
    obj = get_schedule_object(client, project_name, object_type, object_name)
    if obj.input_type == STRUCTURED_TYPE:
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            raise Exception("Failed to parse request data. JSON format expected.")

    schedule = api.ScheduleCreate(name=schedule_name, object_type=object_type, object_name=object_name,
                                  version=object_version, request_data=data, **kwargs)
    response = client.scheduled_requests_create(project_name=project_name, data=schedule)
    print_item(response, LIST_ITEMS, project_name=project_name, rename=RENAME_COLUMNS, fmt=format_)


@commands.command("update")
@SCHEDULE_NAME
@SCHEDULE_NAME_UPDATE
@REQUEST_DATA_UPDATE
@SCHEDULE_UPDATE
@IS_BATCH_REQUEST_UPDATE
@SCHEDULE_TIMEOUT_UPDATE
@IS_ENABLED_UPDATE
@CREATE_FORMATS
def scheduled_requests_update(schedule_name, new_name, data, format_, **kwargs):
    """Update a request schedule."""

    project_name = get_current_project(error=True)

    client = init_client()

    if data is not None:
        schedule = client.scheduled_requests_get(project_name=project_name, schedule_name=schedule_name)
        obj = get_schedule_object(client, project_name, schedule.object_type, schedule.object_name)
        if obj.input_type == STRUCTURED_TYPE:
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise Exception("Failed to parse request data. JSON format expected.")

    new_schedule = api.ScheduleUpdate(name=new_name, request_data=data,
                                      **{k: v for k, v in kwargs.items() if v is not None})
    response = client.scheduled_requests_update(project_name=project_name, schedule_name=schedule_name,
                                                data=new_schedule)
    print_item(response, LIST_ITEMS, project_name=project_name, rename=RENAME_COLUMNS, fmt=format_)


@commands.command("get")
@SCHEDULE_NAME
@GET_FORMATS
def scheduled_requests_get(schedule_name, format_):
    """Get a request schedule."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.scheduled_requests_get(project_name=project_name, schedule_name=schedule_name)
    print_item(response, row_attrs=LIST_ITEMS, project_name=project_name, rename=RENAME_COLUMNS, fmt=format_)


@commands.command("delete")
@SCHEDULE_NAME
@ASSUME_YES
@QUIET
def scheduled_requests_delete(schedule_name, assume_yes, quiet):
    """Delete a request schedule."""

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm("Are you sure you want to delete request schedule <%s> "
                                   "of project <%s>?" % (schedule_name, project_name)):
        client = init_client()
        client.scheduled_requests_delete(project_name=project_name, schedule_name=schedule_name)

        if not quiet:
            click.echo("Request schedule was successfully deleted.")
