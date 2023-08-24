import click
import ubiops as api

from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.constants import STRUCTURED_TYPE
from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import get_current_project, init_client, parse_json


LIST_ITEMS = ['id', 'name', 'schedule', 'enabled']
RENAME_COLUMNS = {'schedule': 'schedule (in UTC)'}


def get_schedule_object(client, project_name, object_type, object_name):
    """
    Get deployment or pipeline details for the scheduled object

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param str project_name: name of the project
    :param str object_type: either 'deployment' or 'pipeline'
    :param str object_name: name of the deployment or pipeline
    """

    if object_type == 'deployment':
        return client.deployments_get(project_name=project_name, deployment_name=object_name)
    if object_type == 'pipeline':
        return client.pipelines_get(project_name=project_name, pipeline_name=object_name)
    raise UbiOpsException("Object type must be 'deployment' or 'pipeline'")


@click.group(name="schedules", short_help="Manage your request schedules")
def commands():
    """
    Manage your request schedules.
    """

    return


@commands.command(name="list", short_help="List schedules")
@options.LIST_FORMATS
@options.LABELS_FILTER
def schedules_list(labels, format_):
    """
    List request schedules in project.
    """

    label_filter = get_label_filter(labels)
    project_name = get_current_project(error=True)

    client = init_client()
    response = client.request_schedules_list(project_name=project_name, labels=label_filter)
    client.api_client.close()

    print_list(response, LIST_ITEMS, rename_cols=RENAME_COLUMNS, sorting_col=1, fmt=format_)


# pylint: disable=too-many-arguments
@commands.command(name="create", short_help="Create a schedule")
@options.SCHEDULE_NAME
@options.OBJECT_TYPE
@options.OBJECT_NAME
@options.OBJECT_VERSION
@options.REQUEST_DATA
@options.SCHEDULE
@options.REQUEST_TIMEOUT
@options.IS_ENABLED
@options.CREATE_FORMATS
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

    schedule = api.ScheduleCreate(
        name=schedule_name, object_type=object_type, object_name=object_name,
        version=object_version, request_data=data, **kwargs
    )
    response = client.request_schedules_create(project_name=project_name, data=schedule)
    client.api_client.close()

    print_item(response, LIST_ITEMS, rename=RENAME_COLUMNS, fmt=format_)


@commands.command(name="update", short_help="Update a schedule")
@options.SCHEDULE_NAME
@options.SCHEDULE_NAME_UPDATE
@options.REQUEST_DATA_UPDATE
@options.SCHEDULE_UPDATE
@options.REQUEST_TIMEOUT
@options.IS_ENABLED_UPDATE
@options.CREATE_FORMATS
def schedules_update(schedule_name, new_name, data, format_, **kwargs):
    """
    Update a request schedule.
    """

    project_name = get_current_project(error=True)

    client = init_client()

    if data is not None:
        schedule = client.request_schedules_get(project_name=project_name, schedule_name=schedule_name)
        obj = get_schedule_object(client, project_name, schedule.object_type, schedule.object_name)
        if obj.input_type == STRUCTURED_TYPE:
            data = parse_json(data)

    new_schedule = api.ScheduleUpdate(
        name=new_name, request_data=data, **{k: v for k, v in kwargs.items() if v is not None}
    )
    response = client.request_schedules_update(
        project_name=project_name, schedule_name=schedule_name, data=new_schedule
    )
    client.api_client.close()

    print_item(response, LIST_ITEMS, rename=RENAME_COLUMNS, fmt=format_)


@commands.command(name="get", short_help="Get a schedule")
@options.SCHEDULE_NAME
@options.GET_FORMATS
def schedules_get(schedule_name, format_):
    """
    Get a request schedule.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.request_schedules_get(project_name=project_name, schedule_name=schedule_name)
    client.api_client.close()

    print_item(response, row_attrs=LIST_ITEMS, rename=RENAME_COLUMNS, fmt=format_)


@commands.command(name="delete", short_help="Delete a schedule")
@options.SCHEDULE_NAME
@options.ASSUME_YES
@options.QUIET
def schedules_delete(schedule_name, assume_yes, quiet):
    """
    Delete a request schedule.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete request schedule <{schedule_name}> of project <{project_name}>?"
    ):
        client = init_client()
        client.request_schedules_delete(project_name=project_name, schedule_name=schedule_name)
        client.api_client.close()

        if not quiet:
            click.echo("Request schedule was successfully deleted")
