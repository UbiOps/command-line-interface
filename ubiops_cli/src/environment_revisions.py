import click

from ubiops_cli.utils import init_client, get_current_project, environment_revision_zip_name, write_blob
from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers import options


LIST_ITEMS = ['creation_date', 'id', 'created_by']
GET_ITEMS = ['creation_date', 'id', 'created_by', 'expired']


@click.group(name=["environment_revisions", "env_revisions"], short_help="Manage your environment revisions")
def commands():
    """
    Manage your environment revisions.
    """

    return


@commands.command(name="list", short_help="List environment revisions")
@options.ENVIRONMENT_NAME_OPTION
@options.LIST_FORMATS
def revisions_list(environment_name, format_):
    """
    List the revisions of an environment.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.environment_revisions_list(project_name=project_name, environment_name=environment_name)
    client.api_client.close()

    print_list(response, LIST_ITEMS, sorting_col=0, fmt=format_)


@commands.command(name="get", short_help="Get a revision of an environment")
@options.ENVIRONMENT_NAME_OPTION
@options.ENVIRONMENT_REVISION_ID
@options.GET_FORMATS
def revisions_get(environment_name, revision_id, format_):
    """
    Get a revision of an environment.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    revision = client.environment_revisions_get(
        project_name=project_name,
        environment_name=environment_name,
        revision_id=revision_id
    )
    client.api_client.close()

    print_item(revision, row_attrs=GET_ITEMS, fmt=format_)


@commands.command(name="download", short_help="Download a revision of an environment")
@options.ENVIRONMENT_NAME_OPTION
@options.ENVIRONMENT_REVISION_ID
@options.ENVIRONMENT_ZIP_OUTPUT
@options.QUIET
def revisions_download(environment_name, revision_id, output_path, quiet):
    """
    Download a revision of an environment.

    The `<output_path>` option will be used as output location of the zip file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the zip will be
    saved in `[environment_name]_[datetime.now()].zip`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    with client.environment_revisions_file_download(
        project_name=project_name, environment_name=environment_name, revision_id=revision_id
    ) as response:
        filename = environment_revision_zip_name(environment_name=environment_name)
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo(f"Zip stored in: {output_path}")


@commands.command(name="upload", short_help="Create a revision of an environment")
@options.ENVIRONMENT_NAME_OPTION
@options.ENVIRONMENT_ZIP_FILE
@options.PROGRESS_BAR
@options.GET_FORMATS
def revisions_upload(environment_name, zip_path, progress_bar, format_):
    """
    Create a revision of an environment by uploading a ZIP.

    Please, specify the deployment package `<zip_path>` that should be uploaded.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    revision = client.environment_revisions_file_upload(
        project_name=project_name, environment_name=environment_name, file=zip_path, _progress_bar=progress_bar
    )
    client.api_client.close()

    print_item(revision, row_attrs=['revision', 'build'], fmt=format_)
