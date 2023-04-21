from ubiops_cli.utils import init_client, get_current_project
from ubiops_cli.src.helpers.formatting import print_item, print_list
from ubiops_cli.src.helpers.options import *


LIST_ITEMS = ['creation_date', 'id', 'revision', 'status']


@click.group(["environment_builds", "env_builds"], short_help="Manage your environment builds")
def commands():
    """Manage your environment builds."""
    pass


@commands.command("list", short_help="List environment builds")
@ENVIRONMENT_NAME_OPTION
@ENVIRONMENT_REVISION_ID_OPTION
@LIST_FORMATS
def builds_list(environment_name, revision_id, format_):
    """
    List the builds of an environment.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.environment_builds_list(
        project_name=project_name, environment_name=environment_name, revision_id=revision_id
    )
    client.api_client.close()

    print_list(response, LIST_ITEMS, sorting_col=0, fmt=format_)


@commands.command("get", short_help="Get the build of an environment")
@ENVIRONMENT_NAME_OPTION
@ENVIRONMENT_REVISION_ID_OPTION
@ENVIRONMENT_BUILD_ID
@GET_FORMATS
def builds_get(environment_name, revision_id, build_id, format_):
    """
    Get the build of an environment.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    build = client.environment_builds_get(
        project_name=project_name,
        environment_name=environment_name,
        revision_id=revision_id,
        build_id=build_id
    )
    client.api_client.close()

    print_item(build, row_attrs=LIST_ITEMS, fmt=format_)
