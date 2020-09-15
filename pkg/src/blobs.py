from pkg.utils import get_current_project, init_client, write_blob, abs_path
from pkg.src.helpers.formatting import print_list, print_item
from pkg.src.helpers.options import *


LIST_ITEMS = ['id', 'filename', 'size', 'ttl', 'creation_date']


@click.group("blobs")
def commands():
    """Manage your blobs."""
    pass


@commands.command("list")
@LIST_FORMATS
def blobs_list(format_):
    """List blobs in project."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.blobs_list(project_name=project_name)
    print_list(response, LIST_ITEMS, rename_cols={'ttl': 'time_to_live'}, sorting_col=1, fmt=format_)


@commands.command("create")
@BLOB_PATH
@BLOB_TTL
@CREATE_FORMATS
def blobs_create(input_path, ttl, format_):
    """Upload a new blob."""

    project_name = get_current_project(error=True)
    input_path = abs_path(input_path)

    client = init_client()
    response = client.blobs_create(project_name=project_name, file=input_path, blob_ttl=ttl)
    print_item(response, LIST_ITEMS, rename={'ttl': 'time_to_live'}, fmt=format_)


@commands.command("get")
@BLOB_ID
@BLOB_OUTPUT
@QUIET
def blobs_get(blob_id, output_path, quiet):
    """Download an existing blob."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.blobs_get(project_name=project_name, blob_id=blob_id)
    header = response.headers["Content-Disposition"]
    filename = header.lstrip('attachment; filename=').replace('"', '').strip()
    output_path = write_blob(response.read(), output_path, filename)
    if not quiet:
        click.echo("Blob stored in: %s" % output_path)


@commands.command("delete")
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

        if not quiet:
            click.echo("Blob was successfully deleted.")
