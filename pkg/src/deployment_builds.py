import ubiops as api
from pkg.utils import init_client, get_current_project
from pkg.src.helpers.formatting import print_list, print_item
from pkg.src.helpers.options import *


LIST_ITEMS = ['id','creation_date', 'revision', 'status']


@click.group(["version_builds", "builds"], short_help="Manage your deployment version builds")
def commands():
    """Manage your deployment version builds."""
    pass


@commands.command("list", short_help="List the builds")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_OPTION
@LIST_FORMATS
def builds_list(deployment_name, version_name, format_):
    """
    List the builds of a deployment version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.builds_list(project_name=project_name, deployment_name=deployment_name, version=version_name)
    client.api_client.close()

    print_list(response, LIST_ITEMS, sorting_col=1, fmt=format_)


@commands.command("get", short_help="Get the builds of a deployment version")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_OPTION
@BUILD_ID
@GET_FORMATS
def builds_get(deployment_name, version_name, build_id, format_):
    """Get the build of a deployment version."""

    project_name = get_current_project(error=True)

    client = init_client()
    build = client.builds_get(
        project_name=project_name,
        deployment_name=deployment_name,
        version=version_name,
        build_id=build_id
    )
    client.api_client.close()

    print_item(build, row_attrs=LIST_ITEMS, fmt=format_)
