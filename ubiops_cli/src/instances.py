import click

from ubiops_cli.src.helpers.instance_helpers import (
    INSTANCE_LIST_FIELDS_TABLE,
    INSTANCE_LIST_FIELDS_JSON,
    INSTANCE_RESPONSE,
    INSTANCE_EVENT_LIST_FIELDS,
)
from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import init_client, get_current_project


@click.group(name="instances", short_help="Manage your instances for deployments")
def commands():
    """
    Manage your instances for deployments.
    """

    return


@commands.command(name="list", short_help="List the deployment version instances")
@options.DEPLOYMENT_NAME_OPTION
@options.VERSION_NAME_OPTION
@options.INSTANCE_LIMIT
@options.LIST_FORMATS
def instances_list(deployment_name, version_name, limit, format_):
    """
    List the instances running for a deployment version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.instances_list(
        project_name=project_name, deployment_name=deployment_name, version=version_name, limit=limit
    )
    client.api_client.close()

    attrs = INSTANCE_LIST_FIELDS_TABLE if format_ == "table" else INSTANCE_LIST_FIELDS_JSON
    print_list(items=response.results, attrs=attrs, sorting_col=0, fmt=format_)


@commands.command(name="get", short_help="Get an instance")
@options.DEPLOYMENT_NAME_OPTION
@options.VERSION_NAME_OPTION
@options.INSTANCE_ID_ARGUMENT
@options.GET_FORMATS
def instances_get(deployment_name, version_name, instance_id, format_):
    """
    Get the details of a single instance running for a deployment version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.instances_get(
        project_name=project_name, deployment_name=deployment_name, version=version_name, instance_id=instance_id
    )
    client.api_client.close()

    attrs = INSTANCE_LIST_FIELDS_TABLE if format_ == "row" else INSTANCE_LIST_FIELDS_JSON
    print_item(
        item=response,
        row_attrs=attrs,
        fmt=format_,
        required_front=INSTANCE_RESPONSE["required_front"],
        optional=INSTANCE_RESPONSE["optional"],
    )


@commands.command(name="events", short_help="List instance events")
@options.DEPLOYMENT_NAME_OPTION
@options.VERSION_NAME_OPTION
@options.INSTANCE_ID_ARGUMENT
@options.INSTANCE_LIMIT
@options.LIST_FORMATS
def instances_events(deployment_name, version_name, instance_id, limit, format_):
    """
    List the events of an instance running for a deployment version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.instance_events_list(
        project_name=project_name,
        deployment_name=deployment_name,
        version=version_name,
        instance_id=instance_id,
        limit=limit,
    )
    client.api_client.close()

    print_list(items=response.results, attrs=INSTANCE_EVENT_LIST_FIELDS, sorting_col=0, fmt=format_)
