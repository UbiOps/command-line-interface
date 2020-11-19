from pkg.utils import get_current_project, init_client, write_blob, abs_path
from pkg.src.helpers.formatting import print_list, print_item
from pkg.src.helpers.options import *


LIST_ITEMS = ['id', 'filename', 'size', 'ttl', 'creation_date']


@click.group("blobs", short_help="Manage your blobs")
def commands():
    """Manage your blobs."""
    pass


@commands.command("list", short_help="List blobs in project")
@LIST_FORMATS
def blobs_list(format_):
    """List blobs in project."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.blobs_list(project_name=project_name)
    client.api_client.close()

    print_list(response, LIST_ITEMS, rename_cols={'ttl': 'time_to_live'}, sorting_col=1, fmt=format_)


@commands.command("create", short_help="Upload a new blob")
@BLOB_PATH
@BLOB_TTL
@CREATE_FORMATS
def blobs_create(input_path, ttl, format_):
    """Upload a new blob."""

    project_name = get_current_project(error=True)
    input_path = abs_path(input_path)

    client = init_client()
    response = client.blobs_create(project_name=project_name, file=input_path, blob_ttl=ttl)
    client.api_client.close()

    print_item(response, LIST_ITEMS, rename={'ttl': 'time_to_live'}, fmt=format_)


@commands.command("get", short_help="Download an existing blob")
@BLOB_ID
@BLOB_OUTPUT
@QUIET
def blobs_get(blob_id, output_path, quiet):
    """Download an existing blob."""

    project_name = get_current_project(error=True)

    client = init_client()
    with client.blobs_get(project_name=project_name, blob_id=blob_id) as response:
        filename = response.getfilename()
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo("Blob stored in: %s" % output_path)


@commands.command("delete", short_help="Delete a blob")
@BLOB_ID
@ASSUME_YES
@QUIET
def blobs_delete(blob_id, assume_yes, quiet):
    """Delete a blob."""

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm("Are you sure you want to delete blob <%s> "
                                   "of project <%s>?" % (blob_id, project_name)):
        client = init_client()
        client.blobs_delete(project_name=project_name, blob_id=blob_id)
        client.api_client.close()

        if not quiet:
            click.echo("Blob was successfully deleted")
