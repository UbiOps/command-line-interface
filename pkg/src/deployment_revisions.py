import ubiops as api
from pkg.utils import init_client, get_current_project, default_version_zip_name, write_blob
from pkg.src.helpers.formatting import print_list, print_item
from pkg.src.helpers.options import *


LIST_ITEMS = ['id', 'creation_date', 'created_by']


@click.group(["version_revisions", "revisions"], short_help="Manage your deployment version revisions")
def commands():
    """Manage your deployment version revisions."""
    pass


@commands.command("list", short_help="List the revisions")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_OPTION
@LIST_FORMATS
def revisions_list(deployment_name, version_name, format_):
    """
    List the revisions of a deployment version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.revisions_list(project_name=project_name, deployment_name=deployment_name, version=version_name)
    client.api_client.close()

    print_list(response, LIST_ITEMS, sorting_col=1, fmt=format_)


@commands.command("get", short_help="Get a revision of a deployment version")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_OPTION
@REVISION_ID
@GET_FORMATS
def revisions_get(deployment_name, version_name, revision_id, format_):
    """Get a revision of a deployment version."""

    project_name = get_current_project(error=True)

    client = init_client()
    revision = client.revisions_get(
        project_name=project_name,
        deployment_name=deployment_name,
        version=version_name,
        revision_id=revision_id
    )
    client.api_client.close()

    print_item(revision, row_attrs=LIST_ITEMS, fmt=format_)

@commands.command("download", short_help="Download a revision of a deployment version")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_OPTION
@REVISION_ID
@ZIP_OUTPUT
@QUIET
def revisions_download(deployment_name, version_name, revision_id, output_path, quiet):
    """Download a revision of a deployment version.

    The `<output_path>` option will be used as output location of the zip file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the zip will be
    saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    with client.revisions_file_download(project_name=project_name, deployment_name=deployment_name,
                                        version=version_name, revision_id=revision_id) as response:
        filename = default_version_zip_name(deployment_name, version_name)
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo("Zip stored in: %s" % output_path)

@commands.command("upload", short_help="Create a revision of a deployment version")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_OPTION
@ZIP_FILE
@GET_FORMATS
def revisions_upload(deployment_name, version_name, zip_path, format_):
    """Create a revision of a deployment version by uploading a ZIP.

    Please, specify the deployment package `<zip_path>` that should be uploaded.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    revision = client.revisions_file_upload(project_name=project_name, deployment_name=deployment_name,
                                            version=version_name, file=zip_path)
    client.api_client.close()

    print_item(revision, row_attrs=['revision', 'build'], fmt=format_)
