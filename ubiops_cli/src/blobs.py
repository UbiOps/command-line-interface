import click

from ubiops_cli.utils import get_current_project, init_client, write_blob, abs_path
from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers import options


LIST_ITEMS = ['last_updated', 'id', 'filename', 'size', 'ttl']


@click.group(name="blobs", short_help="Manage your blobs")
def commands():
    """
    Manage your blobs.
    """

    return


@commands.command(name="list", short_help="List blobs in project")
@options.LIST_FORMATS
def blobs_list(format_):
    """
    List blobs in project.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.blobs_list(project_name=project_name)
    client.api_client.close()

    print_list(response, LIST_ITEMS, rename_cols={'ttl': 'time_to_live'}, sorting_col=2, fmt=format_)


@commands.command(name="create", short_help="Upload a new blob")
@options.BLOB_PATH
@options.BLOB_TTL
@options.PROGRESS_BAR
@options.CREATE_FORMATS
def blobs_create(input_path, ttl, progress_bar, format_):
    """
    Upload a new blob.
    """

    project_name = get_current_project(error=True)
    input_path = abs_path(input_path)

    client = init_client()
    response = client.blobs_create(
        project_name=project_name, file=input_path, blob_ttl=ttl,
        _progress_bar=progress_bar
    )
    client.api_client.close()

    print_item(response, LIST_ITEMS, rename={'ttl': 'time_to_live'}, fmt=format_)


@commands.command(name="get", short_help="Download an existing blob")
@options.BLOB_ID
@options.BLOB_OUTPUT
@options.QUIET
def blobs_get(blob_id, output_path, quiet):
    """
    Download an existing blob.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    with client.blobs_get(project_name=project_name, blob_id=blob_id) as response:
        filename = response.getfilename()
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo(f"Blob stored in: {output_path}")


@commands.command(name="update", short_help="Overwrite an existing blob")
@options.BLOB_ID
@options.BLOB_PATH
@options.BLOB_TTL
@options.PROGRESS_BAR
@options.QUIET
def blobs_update(blob_id, input_path, ttl, progress_bar, quiet):
    """
    Update an existing blob by uploading a new file.
    """

    project_name = get_current_project(error=True)
    input_path = abs_path(input_path)

    client = init_client()
    client.blobs_update(
        project_name=project_name, blob_id=blob_id, file=input_path, blob_ttl=ttl, _progress_bar=progress_bar
    )
    client.api_client.close()

    if not quiet:
        click.echo("Blob was successfully updated")


@commands.command(name="delete", short_help="Delete a blob")
@options.BLOB_ID
@options.ASSUME_YES
@options.QUIET
def blobs_delete(blob_id, assume_yes, quiet):
    """
    Delete a blob.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(f"Are you sure you want to delete blob <{blob_id}> of project <{project_name}>?"):
        client = init_client()
        client.blobs_delete(project_name=project_name, blob_id=blob_id)
        client.api_client.close()

        if not quiet:
            click.echo("Blob was successfully deleted")
