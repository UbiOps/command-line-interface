import json
import click
import ubiops as api

from .helpers.formatting import format_yaml, print_list, print_item
from .helpers.helpers import get_label_filter
from .helpers.request_schedule_helpers import (
    define_request_schedule,
    SCHEDULE_CREATE_FIELDS,
    SCHEDULE_DETAILS,
    SCHEDULE_FIELDS_RENAMED,
    SCHEDULE_UPDATE_FIELDS,
)
from .helpers import options
from ..constants import STRUCTURED_TYPE
from ..exceptions import UbiOpsException
from ..utils import get_current_project, init_client, parse_json, read_yaml, write_yaml


LIST_ITEMS = ["id", "name", "schedule", "enabled", "labels"]
RENAME_COLUMNS = {"schedule": "schedule (in UTC)"}


def get_schedule_object(client, project_name, object_type, object_name):
    """
    Get deployment or pipeline details for the scheduled object

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param str project_name: name of the project
    :param str object_type: either 'deployment' or 'pipeline'
    :param str object_name: name of the deployment or pipeline
    """

    if object_type == "deployment":
        return client.deployments_get(project_name=project_name, deployment_name=object_name)
    if object_type == "pipeline":
        return client.pipelines_get(project_name=project_name, pipeline_name=object_name)
    raise UbiOpsException("Object type must be 'deployment' or 'pipeline'")


@click.group(name=["request_schedules", "schedules"], short_help="Manage your request schedules")
def commands():
    """
    Manage your request schedules.
    """

    return


@commands.command(name="list", short_help="List schedules")
@options.LABELS_FILTER
@options.LIST_FORMATS
def schedules_list(labels, format_):
    """
    List request schedules in project.

    The `<labels>` option can be used to filter on specific labels.
    """

    label_filter = get_label_filter(labels)
    project_name = get_current_project(error=True)

    client = init_client()
    response = client.request_schedules_list(project_name=project_name, labels=label_filter)
    client.api_client.close()

    print_list(
        items=response,
        attrs=LIST_ITEMS,
        rename_cols=RENAME_COLUMNS,
        sorting_col=1,
        fmt=format_,
    )


@commands.command(name="get", short_help="Get a schedule")
@options.SCHEDULE_NAME
@options.SCHEDULE_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
def schedules_get(request_schedule_name, output_path, quiet, format_):
    """
    Get a request schedule.

    If you specify the `<output_path>` option, this location will be used to store the
    request schedule settings in a yaml file. You can either specify the `<output_path>` as
    file or directory. If the specified `<output_path>` is a directory, the settings
    will be stored in `request_schedule.yaml`.

    \b
    Example of yaml content:
    ```
    request_schedule_name: my-schedule
    object_type: deployment
    object_name: my-deployment
    object_version: my-version
    schedule: 0 8 * * 1
    request_data: '{"input": "1"}'
    timeout: 14400
    enabled: true
    request_schedule_description: Request schedule created via command line.
    request_schedule_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    ```
    """

    project_name = get_current_project(error=True)

    client = init_client()
    schedule = client.request_schedules_get(project_name=project_name, schedule_name=request_schedule_name)

    # Convert request data dicts to JSON strings
    obj = get_schedule_object(client, project_name, schedule.object_type, schedule.object_name)
    if obj.input_type == STRUCTURED_TYPE and schedule.request_data is not None:
        schedule.request_data = json.dumps(schedule.request_data)

    client.api_client.close()

    if output_path is not None:
        # Store only reusable settings
        dictionary = format_yaml(
            item=schedule, optional=SCHEDULE_CREATE_FIELDS, rename=SCHEDULE_FIELDS_RENAMED, as_str=False
        )

        yaml_file = write_yaml(output_path, dictionary, default_file_name="request_schedule.yaml")
        if not quiet:
            click.echo(f"Request schedule file stored in: {yaml_file}")

    else:
        print_item(
            item=schedule,
            row_attrs=LIST_ITEMS,
            optional=SCHEDULE_DETAILS,
            rename={**SCHEDULE_FIELDS_RENAMED, **RENAME_COLUMNS},
            fmt=format_,
        )


# pylint: disable=too-many-arguments
@commands.command(name="create", short_help="Create a schedule")
@options.SCHEDULE_NAME_OVERRULE
@options.OBJECT_TYPE
@options.OBJECT_NAME
@options.OBJECT_VERSION
@options.REQUEST_DATA
@options.SCHEDULE
@options.REQUEST_TIMEOUT
@options.IS_ENABLED
@options.SCHEDULE_LABELS
@options.SCHEDULE_DESCRIPTION
@options.SCHEDULE_YAML_FILE
@options.CREATE_FORMATS
def schedules_create(yaml_file, format_, **kwargs):
    """
    Create a request schedule. The request schedule will create a batch request to your deployment/pipeline according to
    the defined schedule.

    \b
    It is possible to define the parameters using a yaml file.
    For example:
    ```
    request_schedule_name: my-schedule
    object_type: deployment
    object_name: my-deployment
    object_version: my-version
    schedule: 0 8 * * 1
    request_data: '{"input": "1"}'
    timeout: 14400
    enabled: true
    request_schedule_description: Request schedule created via command line.
    request_schedule_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    ```

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
    options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
    The request schedule name can either be passed as command argument or specified inside the yaml file using
    `<request_schedule_name>`.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)
    kwargs = define_request_schedule(fields=kwargs, yaml_content=yaml_content)

    # Handle default values
    if "object_type" not in kwargs or not kwargs["object_type"]:
        kwargs["object_type"] = "deployment"
    if "enabled" not in kwargs or kwargs["enabled"] is None:
        kwargs["enabled"] = True

    # Handle request data
    client = init_client()
    obj = get_schedule_object(client, project_name, kwargs.get("object_type", ""), kwargs.get("object_name", ""))
    if obj.input_type == STRUCTURED_TYPE:
        kwargs["request_data"] = parse_json(kwargs.get("request_data", {}))

    schedule = api.ScheduleCreate(
        **{k: kwargs[k] for k in SCHEDULE_CREATE_FIELDS if k in kwargs and kwargs[k] is not None}
    )
    response = client.request_schedules_create(project_name=project_name, data=schedule)
    client.api_client.close()

    print_item(
        item=response,
        row_attrs=LIST_ITEMS,
        optional=SCHEDULE_DETAILS,
        rename={**SCHEDULE_FIELDS_RENAMED, **RENAME_COLUMNS},
        fmt=format_,
    )


@commands.command(name="update", short_help="Update a schedule")
@options.SCHEDULE_NAME
@options.SCHEDULE_NAME_UPDATE
@options.REQUEST_DATA
@options.SCHEDULE
@options.REQUEST_TIMEOUT
@options.IS_ENABLED_UPDATE
@options.SCHEDULE_LABELS
@options.SCHEDULE_DESCRIPTION
@options.SCHEDULE_YAML_FILE
@options.QUIET
def schedules_update(request_schedule_name, new_name, yaml_file, quiet, **kwargs):
    """
    Update a request schedule.

    \b
    It is possible to define the parameters using a yaml file or passing the options as command options.
    For example:
    ```
    request_schedule_name: my-schedule
    object_type: deployment
    object_name: my-deployment
    object_version: my-version
    schedule: 0 8 * * 1
    request_data: '{"input": "1"}'
    timeout: 14400
    enabled: true
    request_schedule_description: Request schedule created via command line.
    request_schedule_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    ```

    If both a `<yaml_file>` is set and options are given, the options defined by `<yaml_file>` will be overwritten by
    the specified command options.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)
    kwargs = define_request_schedule(fields=kwargs, yaml_content=yaml_content)
    kwargs["name"] = new_name

    client = init_client()

    if kwargs.get("request_data", None) is not None:
        schedule = client.request_schedules_get(project_name=project_name, schedule_name=request_schedule_name)
        obj = get_schedule_object(client, project_name, schedule.object_type, schedule.object_name)
        if obj.input_type == STRUCTURED_TYPE:
            kwargs["request_data"] = parse_json(kwargs["request_data"])

    new_schedule = api.ScheduleUpdate(
        **{k: kwargs[k] for k in SCHEDULE_UPDATE_FIELDS if k in kwargs and kwargs[k] is not None}
    )

    client.request_schedules_update(project_name=project_name, schedule_name=request_schedule_name, data=new_schedule)
    client.api_client.close()

    if not quiet:
        click.echo("Request schedule was successfully updated")


@commands.command(name="delete", short_help="Delete a schedule")
@options.SCHEDULE_NAME
@options.ASSUME_YES
@options.QUIET
def schedules_delete(request_schedule_name, assume_yes, quiet):
    """
    Delete a request schedule.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete request schedule <{request_schedule_name}> of project <{project_name}>?"
    ):
        client = init_client()
        client.request_schedules_delete(project_name=project_name, schedule_name=request_schedule_name)
        client.api_client.close()

        if not quiet:
            click.echo("Request schedule was successfully deleted")
