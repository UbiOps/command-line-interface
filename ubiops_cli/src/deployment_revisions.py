import click
import ubiops as api

from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers.wait_for import wait_for
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import init_client, get_current_project, default_version_zip_name, write_blob

LIST_ITEMS = ['creation_date', 'id', 'created_by', 'status']


@click.group(name=["version_revisions", "revisions"], short_help="Manage your deployment version revisions")
def commands():
    """
    Manage your deployment version revisions.
    """

    return


@commands.command(name="list", short_help="List the revisions")
@options.DEPLOYMENT_NAME_OPTION
@options.VERSION_NAME_OPTION
@options.LIST_FORMATS
def revisions_list(deployment_name, version_name, format_):
    """
    List the revisions of a deployment version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.revisions_list(project_name=project_name, deployment_name=deployment_name, version=version_name)
    client.api_client.close()

    print_list(response, LIST_ITEMS, sorting_col=0, fmt=format_)


@commands.command(name="get", short_help="Get a revision of a deployment version")
@options.DEPLOYMENT_NAME_OPTION
@options.VERSION_NAME_OPTION
@options.REVISION_ID
@options.GET_FORMATS
def revisions_get(deployment_name, version_name, revision_id, format_):
    """
    Get a revision of a deployment version.
    """

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


@commands.command(name="download", short_help="Download a revision of a deployment version")
@options.DEPLOYMENT_NAME_OPTION
@options.VERSION_NAME_OPTION
@options.REVISION_ID
@options.ZIP_OUTPUT
@options.QUIET
def revisions_download(deployment_name, version_name, revision_id, output_path, quiet):
    """
    Download a revision of a deployment version.

    The `<output_path>` option will be used as output location of the zip file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the zip will be
    saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    with client.revisions_file_download(
        project_name=project_name, deployment_name=deployment_name, version=version_name, revision_id=revision_id
    ) as response:
        filename = default_version_zip_name(deployment_name, version_name)
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo(f"Zip stored in: {output_path}")


@commands.command(name="upload", short_help="Create a revision of a deployment version")
@options.DEPLOYMENT_NAME_OPTION
@options.VERSION_NAME_OPTION
@options.ZIP_FILE
@options.PROGRESS_BAR
@options.GET_FORMATS
def revisions_upload(deployment_name, version_name, zip_path, progress_bar, format_):
    """
    Create a revision of a deployment version by uploading a ZIP.

    Please, specify the deployment package `<zip_path>` that should be uploaded.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    revision = client.revisions_file_upload(
        project_name=project_name, deployment_name=deployment_name, version=version_name, file=zip_path,
        _progress_bar=progress_bar
    )
    client.api_client.close()

    print_item(revision, row_attrs=['revision', 'build'], fmt=format_)


# pylint: disable=too-many-arguments
@commands.command(name="wait", short_help="Wait for a deployment revision to be ready")
@options.DEPLOYMENT_NAME_OPTION
@options.VERSION_NAME_OPTION
@options.REVISION_ID
@options.TIMEOUT_OPTION
@options.STREAM_LOGS
@options.QUIET
def revisions_wait(deployment_name, version_name, revision_id, timeout, stream_logs, quiet):
    """
    Wait for a deployment revision to be ready.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    wait_for(
        api.utils.wait_for.wait_for_revision,
        client=client.api_client,
        project_name=project_name,
        deployment_name=deployment_name,
        version=version_name,
        revision_id=revision_id,
        timeout=timeout,
        quiet=quiet,
        stream_logs=stream_logs
    )
    client.api_client.close()
