import click

from ubiops_cli.src.helpers.instance_helpers import (
    PROJECT_INSTANCE_LIST_FIELDS_TABLE,
    PROJECT_INSTANCE_LIST_FIELDS_JSON,
    INSTANCE_RESPONSE,
)

from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import init_client, get_current_project


@click.group(name="project_instances", short_help="Manage your instances")
def commands():
    """
    Manage all your instances in your project.
    """

    return


@commands.command(name="list", short_help="List the project instances")
@options.PROJECT_INSTANCE_LIMIT
@options.LIST_FORMATS
def project_instances_list(limit, format_):
    """
    List all the instances running in your project.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.project_instances_list(project_name=project_name, limit=limit)
    client.api_client.close()

    attrs = PROJECT_INSTANCE_LIST_FIELDS_TABLE if format_ == "table" else PROJECT_INSTANCE_LIST_FIELDS_JSON
    print_list(items=response.results, attrs=attrs, sorting_col=0, fmt=format_)


@commands.command(name="get", short_help="Get a project instance")
@options.INSTANCE_ID_ARGUMENT
@options.GET_FORMATS
def project_instances_get(instance_id, format_):
    """
    Get the details of a single instance running in your project.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.project_instances_get(project_name=project_name, instance_id=instance_id)
    client.api_client.close()

    attrs = PROJECT_INSTANCE_LIST_FIELDS_TABLE if format_ == "row" else PROJECT_INSTANCE_LIST_FIELDS_JSON
    print_item(
        item=response,
        row_attrs=attrs,
        fmt=format_,
        required_front=INSTANCE_RESPONSE["required_front"],
        optional=INSTANCE_RESPONSE["optional"],
    )
