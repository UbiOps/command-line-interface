import click

from ubiops_cli.utils import init_client, get_current_project
from ubiops_cli.src.helpers.formatting import print_item
from ubiops_cli.src.helpers import options


LIST_ITEMS = ['creation_date', 'id', 'revision', 'status']


@click.group(name=["version_builds", "builds"], short_help="Manage your deployment version builds")
def commands():
    """
    Manage your deployment version builds.
    """

    return


@commands.command(name="get", short_help="[DEPRECATED] Get the builds of a deployment version")
@options.DEPLOYMENT_NAME_OPTION
@options.VERSION_NAME_OPTION
@options.BUILD_ID
@options.GET_FORMATS
def builds_get(deployment_name, version_name, build_id, format_):
    """
    [DEPRECATED] Get the build of a deployment version.
    """

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
