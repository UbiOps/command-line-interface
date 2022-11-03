from os import path

from ubiops.utils.file_operations import upload_file, download_file

from ubiops_cli.utils import get_current_project, init_client
from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers.options import *


LIST_ITEMS = ['file', 'size', 'time_created']


@click.group("files", short_help="Manage your files")
def commands():
    """Manage your files."""
    pass


@commands.group("signedurl", short_help="Manage signedurls for your files")
def signedurl_commands():
    """Manage signedurls for your files."""


@commands.command("list", short_help="List files in bucket")
@BUCKET_NAME_OPTION
@FILE_PREFIX
@FILE_DELIMITER
@FILE_LIMIT
@FILE_CONTINUATION_TOKEN
@LIST_FORMATS
def files_list(bucket_name, prefix, delimiter, limit, continuation_token, format_):
    """List files in a bucket.

    If formatted as table it will only show the file name, size and time_created.

    If formatted as json the response will show the continuation_token and prefixes as well.
    """

    project_name = get_current_project(error=True)

    client = init_client()

    file_detail = client.files_list(
        project_name=project_name,
        bucket_name=bucket_name,
        prefix=prefix,
        delimiter=delimiter,
        limit=limit,
        continuation_token=continuation_token
    )
    client.api_client.close()

    items = file_detail
    if format_ == 'table':
        # If the format is table only the files list is shown
        items = file_detail.files

    print_list(items=items, attrs=LIST_ITEMS, sorting_col=0, fmt=format_)

    # If format is table print prefixes as well
    if format_ == 'table':
        for prefix in file_detail.prefixes:
            click.echo(prefix)


@commands.command("get", short_help="Get a file")
@BUCKET_NAME_OPTION
@FILE_NAME_ARGUMENT
@GET_FORMATS
def files_get(bucket_name, file_name, format_):
    """Get the details of a file in the bucket."""

    project_name = get_current_project(error=True)

    client = init_client()
    file = client.files_get(project_name=project_name, bucket_name=bucket_name, file=file_name)
    client.api_client.close()

    print_item(
        file,
        row_attrs=LIST_ITEMS,
        required_front=['file', 'size', 'time_created'],
        fmt=format_
    )


@signedurl_commands.command("create", short_help="Generate signed url to upload a file")
@BUCKET_NAME_OPTION
@FILE_NAME_ARGUMENT
@GET_FORMATS
def files_signedurl_create(bucket_name, file_name, format_):
    """Generate a signed url to upload a file."""

    project_name = get_current_project(error=True)

    client = init_client()
    file_url = client.files_upload(project_name=project_name, bucket_name=bucket_name, file=file_name, data={})
    client.api_client.close()

    print_item(
        file_url,
        row_attrs=["url", "provider"],
        fmt=format_
    )


@signedurl_commands.command("get", short_help="Generate signed url to download a file")
@BUCKET_NAME_OPTION
@FILE_NAME_ARGUMENT
@GET_FORMATS
def files_signedurl_get(bucket_name, file_name, format_):
    """Generate a signed url to download a file."""

    project_name = get_current_project(error=True)

    client = init_client()
    file_url = client.files_download(project_name=project_name, bucket_name=bucket_name, file=file_name)
    client.api_client.close()

    print_item(
        file_url,
        row_attrs=["url", "provider"],
        fmt=format_
    )


@commands.command("delete", short_help="Delete a file")
@BUCKET_NAME_OPTION
@FILE_NAME_ARGUMENT
@ASSUME_YES
@QUIET
def files_delete(bucket_name, file_name, assume_yes, quiet):
    """Delete a file from a bucket."""

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm("Are you sure you want to delete file <%s> from bucket <%s> "
                                   "of project <%s>?" % (file_name, bucket_name, project_name)):
        client = init_client()
        client.files_delete(project_name=project_name, bucket_name=bucket_name, file=file_name)
        client.api_client.close()

        if not quiet:
            click.echo("File was successfully deleted")


@commands.command("upload", short_help="Upload a file")
@FILE_SOURCE_PATH_OPTION
@BUCKET_NAME_OPTION
@FILE_NAME_OVERRULE
@QUIET
def files_upload(source_file, bucket_name, file_name, quiet):
    """Upload a file to a bucket."""

    project_name = get_current_project(error=True)

    client = init_client()

    file_uri = upload_file(
        client=client.api_client,
        project_name=project_name,
        bucket_name=bucket_name,
        file_path=source_file,
        file_name=file_name,
    )

    client.api_client.close()

    if not quiet:
        click.echo(file_uri)


@commands.command("download", short_help="Download a file")
@BUCKET_NAME_OPTION
@FILE_NAME_OVERRULE
@FILE_URI_OPTION
@FILE_DESTINATION_PATH_OPTION
@QUIET
def files_download(bucket_name, file_name, file_uri, output_path, quiet):
    """
    Download a file from a bucket. Provide either file_name or file_uri (e.g. 'ubiops-file://default/my-file.jpg').
    """

    project_name = get_current_project(error=True)

    assert file_name or file_uri, 'Please, specify the file_name or file_uri to download'

    client = init_client()

    if output_path is None:
        if file_name:
            output_path = path.basename(file_name)
        else:
            output_path = path.basename(file_uri)

    download_file(
        client=client.api_client,
        project_name=project_name,
        bucket_name=bucket_name,
        file_name=file_name,
        file_uri=file_uri,
        output_path=output_path
    )

    client.api_client.close()

    if not quiet:
        click.echo("File was successfully downloaded")
