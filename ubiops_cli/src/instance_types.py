import click

from ubiops_cli.src.helpers.formatting import print_list
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import init_client, get_current_project


INSTANCE_TYPE_LIST_FIELDS = [
    "id",
    "name",
    "display_name",
    "time_created",
    "cpu",
    "memory",
    "storage",
    "accelerator",
    "dedicated_node",
    "node_pool cluster type",
]


@click.group(name="instance_types", short_help="Manage your instance types")
def commands():
    """
    Manage your instance types.
    """

    return


@commands.command(name="list", short_help="List the instance types")
@options.INSTANCE_TYPE_GROUP_LIMIT
@options.LIST_FORMATS
def instance_types_list(limit, format_):
    """
    List the instance types in your project.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.instance_types_list(project_name=project_name, limit=limit)
    client.api_client.close()

    print_list(
        items=response.results,
        attrs=INSTANCE_TYPE_LIST_FIELDS,
        sorting_col=0,
        fmt=format_,
    )
