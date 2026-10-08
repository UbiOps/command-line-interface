import click
import ubiops as api

from .helpers.formatting import print_list, print_item
from .helpers import options
from .helpers.environment_helpers import (
    TAG_CREATE_FIELDS,
    TAG_DETAILS,
    TAG_FIELDS_RENAMED,
    TAG_LIST_FIELDS,
    TAG_UPDATE_FIELDS,
    define_environment_tag,
)
from ..utils import get_current_project, init_client, read_yaml, write_blob


@click.group(name=["environment_tags", "tags"], short_help="Manage your environment tags")
def commands():
    """
    Manage your environment tags.
    """

    return


@commands.command(name="list", short_help="List environment tags")
@options.ENVIRONMENT_NAME_OPTION
@options.LIST_FORMATS
def tags_list(environment_name, format_):
    """
    List the tags of an environment.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.environment_tags_list(project_name=project_name, environment_name=environment_name)
    client.api_client.close()

    print_list(items=response, attrs=TAG_LIST_FIELDS, rename_cols=TAG_FIELDS_RENAMED, sorting_col=0, fmt=format_)


@commands.command(name="get", short_help="Get a tag of an environment")
@options.TAG_NAME
@options.ENVIRONMENT_NAME_OPTION
@options.GET_FORMATS
def tags_get(tag_name, environment_name, format_):
    """
    Get a tag of an environment.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    tag = client.environment_tags_get(project_name=project_name, environment_name=environment_name, tag_name=tag_name)
    client.api_client.close()

    tag_type = "Dependencies in package" if tag.base_environment_name else "Docker image"
    setattr(tag, "tag_type", tag_type)

    print_item(
        item=tag,
        row_attrs=TAG_LIST_FIELDS,
        required_front=["id"],
        optional=TAG_DETAILS,
        rename=TAG_FIELDS_RENAMED,
        fmt=format_,
    )


@commands.command(name="create", short_help="Create a tag")
@options.TAG_NAME_OPTIONAL_ARGUMENT
@options.ENVIRONMENT_NAME_OPTIONAL
@options.TAG_SUPPORTS_REQUEST_FORMAT
@options.YAML_FILE
@options.CREATE_FORMATS
def tags_create(yaml_file, format_, **kwargs):
    """
    Create a tag.

    \b
    It is possible to define the parameters using a yaml file.
    For example:
    ```
    tag_name: my-tag-name
    tag_supports_request_format: true
    ```

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and options are given, the
    options defined by `<yaml_file>` will be overwritten by the specified command options.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)
    kwargs = define_environment_tag(kwargs, yaml_content, extra_fields=["environment_name"])

    assert "environment_name" in kwargs and kwargs["environment_name"], (
        "Please, specify the environment name in either the yaml file or as a command option"
    )

    client = init_client()
    tag = client.environment_tags_create(
        project_name=project_name,
        environment_name=kwargs["environment_name"],
        data=api.EnvironmentTagCreate(**{k: kwargs[k] for k in TAG_CREATE_FIELDS if k in kwargs}),
    )
    client.api_client.close()

    print_item(
        item=tag,
        row_attrs=TAG_LIST_FIELDS,
        required_front=["id"],
        optional=TAG_DETAILS,
        rename=TAG_FIELDS_RENAMED,
        fmt=format_,
    )


@commands.command(name="update", short_help="Update a tag")
@options.TAG_NAME
@options.ENVIRONMENT_NAME_OPTION
@options.TAG_SUPPORTS_REQUEST_FORMAT
@options.TAG_STATUS
@options.QUIET
def tags_update(tag_name, environment_name, quiet, **kwargs):
    """
    Update a tag.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    kwargs = define_environment_tag(fields=kwargs, yaml_content={}, extra_fields=["status"])
    client.environment_tags_update(
        project_name=project_name,
        environment_name=environment_name,
        tag_name=tag_name,
        data=api.EnvironmentTagUpdate(
            **{k: kwargs[k] for k in TAG_UPDATE_FIELDS if k in kwargs and kwargs[k] is not None}
        ),
    )
    client.api_client.close()

    if not quiet:
        click.echo("Tag was successfully updated")


@commands.command(name="delete", short_help="Delete an environment")
@options.TAG_NAME
@options.ENVIRONMENT_NAME_OPTION
@options.ASSUME_YES
@options.QUIET
def tags_delete(tag_name, environment_name, assume_yes, quiet):
    """
    Delete a tag.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete tag <{tag_name}> of environment <{environment_name}> "
        f"in project <{project_name}>?"
    ):
        client = init_client()
        client.environment_tags_delete(project_name=project_name, environment_name=environment_name, tag_name=tag_name)
        client.api_client.close()
        if not quiet:
            click.echo("Tag was successfully deleted")


@commands.command(name="build", short_help="Build a tag for an environment")
@options.TAG_NAME
@options.ENVIRONMENT_NAME_OPTION
@options.BASE_ENVIRONMENT_NAME
@options.BASE_ENVIRONMENT_TAG
@options.TAG_ARCHIVE_INPUT
@options.PROGRESS_BAR
@options.QUIET
def tags_build(
    tag_name, environment_name, base_environment_name, base_environment_tag, archive_path, progress_bar, quiet
):
    """
    Build a tag for an environment by uploading an archive file (Docker archive or environment package). Specify which
    base environment and tag should be used for the build.

    Please, specify the environment file `<archive_path>` that should be uploaded.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    client.environment_tags_build(
        project_name=project_name,
        environment_name=environment_name,
        tag_name=tag_name,
        file=archive_path,
        base_environment_name=base_environment_name,
        base_environment_tag=base_environment_tag,
        _progress_bar=progress_bar,
    )
    client.api_client.close()

    if not quiet:
        click.echo("File was successfully uploaded")


@commands.command(name="download", short_help="Download the environment package of an environment tag")
@options.TAG_NAME
@options.ENVIRONMENT_NAME_OPTION
@options.TAG_ARCHIVE_OUTPUT
@options.QUIET
def tags_download(tag_name, environment_name, output_path, quiet):
    """
    Download the environment package of an environment tag. Only relevant for tags that are build via UbiOps.

    The `<output_path>` option will be used as output location of the archive file. If not specified,
    the current directory will be used.
    """

    if not output_path:
        output_path = "."

    project_name = get_current_project(error=True)
    client = init_client()

    tag = client.environment_tags_get(project_name=project_name, environment_name=environment_name, tag_name=tag_name)
    assert tag.built, "It's only possible to download an environment package of a tag that was built by UbiOps."

    with client.environment_tags_download(
        project_name=project_name, environment_name=environment_name, tag_name=tag_name
    ) as response:
        output_path = write_blob(response.read(), output_path, response.getfilename())
    client.api_client.close()

    if not quiet:
        click.echo(f"Archive stored in: {output_path}")
