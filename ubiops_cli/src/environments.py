import os

import click
import ubiops as api

from ubiops_cli.constants import DEFAULT_IGNORE_FILE
from ubiops_cli.src.helpers.environment_helpers import (
    define_environment,
    ENVIRONMENT_CREATE_FIELDS,
    ENVIRONMENT_DETAILS,
    ENVIRONMENT_FIELDS_RENAMED,
    ENVIRONMENT_UPDATE_FIELDS,
)
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers.wait_for import wait_for
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import get_current_project, init_client, read_yaml, set_dict_default, write_yaml, zip_dir

LIST_ITEMS = ["last_updated", "name", "base_environment", "labels"]


@click.group(name=["environments", "envs"], short_help="Manage your environments")
def commands():
    """
    Manage your environments.
    """

    return


@commands.command(name="list", short_help="List environments")
@options.LABELS_FILTER
@options.ENVIRONMENT_TYPE_FILTER
@options.LIST_FORMATS
def environments_list(labels, environment_type, format_):
    """
    List all your environments in your project.

    The `<labels>` option can be used to filter on specific labels.
    """

    project_name = get_current_project(error=True)
    label_filter = get_label_filter(labels)

    client = init_client()
    environments = client.environments_list(
        project_name=project_name, environment_type=environment_type, labels=label_filter
    )
    client.api_client.close()

    print_list(items=environments, attrs=LIST_ITEMS, rename_cols=ENVIRONMENT_FIELDS_RENAMED, sorting_col=1, fmt=format_)


@commands.command(name="get", short_help="Get details of an environment")
@options.ENVIRONMENT_NAME_ARGUMENT
@options.ENVIRONMENT_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
def environments_get(environment_name, output_path, quiet, format_):
    """
    Get the environment details.

    If you specify the `<output_path>` option, this location will be used to store the
    environment settings in a yaml file. You can either specify the `<output_path>` as
    file or directory. If the specified `<output_path>` is a directory, the settings
    will be stored in `environment.yaml`.

    \b
    Example of yaml content:
    ```
    environment_name: custom-environment
    environment_display_name: Custom environment for Python 3.11
    environment_description: Environment created via command line.
    environment_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    base_environment: python3-11
    ```
    """

    project_name = get_current_project(error=True)

    # Show environment details
    client = init_client()
    environment = client.environments_get(project_name=project_name, environment_name=environment_name)
    client.api_client.close()

    if output_path is not None:
        # Store only reusable settings
        dictionary = format_yaml(
            item=environment, optional=ENVIRONMENT_DETAILS, rename=ENVIRONMENT_FIELDS_RENAMED, as_str=False
        )

        yaml_file = write_yaml(output_path, dictionary, default_file_name="environment.yaml")
        if not quiet:
            click.echo(f"Environment file stored in: {yaml_file}")

    else:
        environment_type = "Dependencies in package" if environment.base_environment else "Docker image"
        setattr(environment, "environment_type", environment_type)

        print_item(
            item=environment,
            row_attrs=LIST_ITEMS,
            required_front=["id", "creation_date"],
            optional=ENVIRONMENT_DETAILS,
            required_end=["active_revision", "active_build", "latest_revision", "latest_build"],
            rename=ENVIRONMENT_FIELDS_RENAMED,
            fmt=format_,
        )


@commands.command(name="create", short_help="Create an environment")
@options.ENVIRONMENT_NAME_OVERRULE
@options.BASE_ENVIRONMENT
@options.ENVIRONMENT_SUPPORTS_REQUEST_FORMAT
@options.ENVIRONMENT_DISPLAY_NAME
@options.ENVIRONMENT_DESCRIPTION
@options.ENVIRONMENT_LABELS
@options.ENVIRONMENT_YAML_FILE
@options.CREATE_FORMATS
def environments_create(yaml_file, format_, **kwargs):
    """
    Create an environment.

    \b
    It is possible to define the parameters using a yaml file.
    For example:
    ```
    environment_name: my-environment-name
    environment_display_name: Custom environment for Python 3.11
    environment_description: Environment created via command line.
    environment_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    environment_supports_request_format: true
    base_environment: python3-11
    ```

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
    options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
    The environment name can either be passed as command argument or specified inside the yaml file using
    `<environment_name>`.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=[])

    assert (
        "environment_name" in yaml_content or "environment_name" in kwargs
    ), "Please, specify the environment name in either the yaml file or as a command argument"

    kwargs = define_environment(kwargs, yaml_content, extra_yaml_fields=[])
    environment = api.EnvironmentCreate(
        **{k: kwargs[k] for k in ENVIRONMENT_CREATE_FIELDS if k in kwargs and kwargs[k] is not None}
    )

    client = init_client()
    environment_response = client.environments_create(project_name=project_name, data=environment)
    client.api_client.close()

    print_item(
        item=environment_response,
        row_attrs=LIST_ITEMS,
        required_front=["id", "name"],
        optional=ENVIRONMENT_DETAILS,
        required_end=["active_revision", "active_build", "latest_revision", "latest_build"],
        rename=ENVIRONMENT_FIELDS_RENAMED,
        fmt=format_,
    )


@commands.command(name="update", short_help="Update an environment")
@options.ENVIRONMENT_NAME_ARGUMENT
@options.ENVIRONMENT_NAME_UPDATE
@options.ENVIRONMENT_DISPLAY_NAME
@options.ENVIRONMENT_DESCRIPTION
@options.ENVIRONMENT_LABELS
@options.ENVIRONMENT_YAML_FILE
@options.QUIET
def environments_update(environment_name, new_name, yaml_file, quiet, **kwargs):
    """
    Update an environment.

    \b
    It is possible to define the parameters using a yaml file or passing the options as command options.
    For example:
    ```

    environment_name: my-environment-name
    environment_display_name: Custom environment for Python 3.9
    environment_description: Environment created via command line.
    environment_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    ```

    If both a `<yaml_file>` is set and options are given, the options defined by `<yaml_file>` will be overwritten by
    the specified command options.
    """

    project_name = get_current_project(error=True)

    client = init_client()

    yaml_content = read_yaml(yaml_file, required_fields=[])

    kwargs = define_environment(kwargs, yaml_content, extra_yaml_fields=[])
    kwargs["name"] = new_name
    environment = api.EnvironmentUpdate(
        **{k: kwargs[k] for k in ENVIRONMENT_UPDATE_FIELDS if k in kwargs and kwargs[k] is not None}
    )

    client.environments_update(project_name=project_name, environment_name=environment_name, data=environment)
    client.api_client.close()

    if not quiet:
        click.echo("Environment was successfully updated")


@commands.command(name="delete", short_help="Delete an environment")
@options.ENVIRONMENT_NAME_ARGUMENT
@options.ASSUME_YES
@options.QUIET
def environments_delete(environment_name, assume_yes, quiet):
    """
    Delete an environment.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete environment <{environment_name}> in project <{project_name}>?"
    ):
        client = init_client()
        client.environments_delete(project_name=project_name, environment_name=environment_name)
        client.api_client.close()
        if not quiet:
            click.echo("Environment was successfully deleted")


@commands.command(name="wait", short_help="Wait for an environment to be ready")
@options.ENVIRONMENT_NAME_ARGUMENT
@options.TIMEOUT_OPTION
@options.STREAM_LOGS
@options.QUIET
def environments_wait(environment_name, timeout, stream_logs, quiet):
    """
    Wait for an environment to be ready.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    wait_for(
        api.utils.wait_for.wait_for_environment,
        client=client.api_client,
        project_name=project_name,
        environment_name=environment_name,
        timeout=timeout,
        quiet=quiet,
        stream_logs=stream_logs,
    )
    client.api_client.close()


# pylint: disable=too-many-arguments
@commands.command(name="package", short_help="Package environment code")
@options.ENVIRONMENT_NAME_ZIP
@options.ENVIRONMENT_PACKAGE_DIR
@options.ENVIRONMENT_ARCHIVE_OUTPUT
@options.IGNORE_FILE
@options.ASSUME_YES
@options.QUIET
def environments_package(environment_name, directory, output_path, ignore_file, assume_yes, quiet):
    """
    Package code to archive file which is ready to be deployed.

    Please, specify the code `<directory>` that should be deployed. The files in this directory will be zipped.
    Subdirectories and files that shouldn't be contained in the archive can be specified in an ignore file, which is by
    default '.ubiops-ignore'. The structure of this file is assumed to be equal to the well-known .gitignore file.

    Use the `<output_path>` option to specify the output location of the archive file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the archive will be saved as
    `[environment_name]_[datetime.now()].zip`. Use the `<assume_yes>` option to overwrite without confirmation if file
    specified in `<output_path>` already exists.
    """

    if output_path is None:
        output_path = "."

    ignore_file = DEFAULT_IGNORE_FILE if ignore_file is None else ignore_file
    archive_path, _ = zip_dir(
        directory=directory,
        output_path=output_path,
        ignore_filename=ignore_file,
        prefix=environment_name,
        force=assume_yes,
        package_directory="environment_package",
    )
    if not quiet:
        click.echo(f"Created archive: {archive_path}")


# pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-statements
@commands.command(name="deploy", short_help="Deploy an environment")
@options.ENVIRONMENT_NAME_OVERRULE
@options.ENVIRONMENT_PACKAGE_DIR_OPTIONAL
@options.ENVIRONMENT_ARCHIVE_INPUT_OPTIONAL
@options.IGNORE_FILE
@options.ENVIRONMENT_ARCHIVE_OUTPUT
@options.ENVIRONMENT_YAML_FILE
@options.BASE_ENVIRONMENT
@options.ENVIRONMENT_SUPPORTS_REQUEST_FORMAT
@options.ENVIRONMENT_DISPLAY_NAME
@options.ENVIRONMENT_DESCRIPTION
@options.ENVIRONMENT_LABELS
@options.OVERWRITE
@options.ASSUME_YES
@options.PROGRESS_BAR
@options.QUIET
def environments_deploy(
    environment_name,
    directory,
    archive_path,
    output_path,
    yaml_file,
    overwrite,
    assume_yes,
    progress_bar,
    quiet,
    **kwargs,
):
    """
    Deploy an environment.

    Please, either specify an `<archive_file>` or a code `<directory>` that should be deployed. If a directory is
    used, the files in the directory will be zipped and uploaded. Subdirectories and files that shouldn't be contained
    in the archive can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this file
    is assumed to be equal to the well-known '.gitignore' file.

    If you want to store a local copy of the uploaded archive file, please use the `<output_path>` option.
    The `<output_path>` option will be used as output location of the file. If the `<output_path>` is a directory, the
    archive will be saved as `[environment_name]_[datetime.now()].zip`. Use the `<assume_yes>` option to overwrite
    without confirmation if file specified in `<output_path>` already exists.

    It's not possible to update the base environment of an existing environment.

    \b
    It is possible to define the parameters using a yaml file.
    For example:
    ```
    environment_name: my-environment-name
    environment_display_name: Custom environment for Python 3.11
    environment_description: Environment created via command line.
    environment_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    environment_supports_request_format: true
    base_environment: python3-11
    ```

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and options are given,
    the options defined by `<yaml_file>` will be overwritten by the specified command options. The environment name can
    either be passed as command argument or specified inside the yaml file using `<environment_name>`.
    """

    if output_path is None:
        store_archive = False
        output_path = "."
    else:
        store_archive = True

    project_name = get_current_project(error=True)
    client = init_client()
    yaml_content = read_yaml(yaml_file, required_fields=[])

    assert "environment_name" in yaml_content or environment_name, (
        "Please, specify the environment name in either " "the yaml file or as a command argument"
    )
    assert directory or archive_path, (
        "Please, specify either a directory or an archive file for the environment " "package"
    )
    assert not (directory and archive_path), (
        "Please, specify either a directory or an archive file for the " "environment package, not both"
    )
    assert not (archive_path and store_archive), "The output path option is only used in combination with a directory"

    environment_name = set_dict_default(environment_name, yaml_content, "environment_name")
    kwargs["environment_name"] = environment_name

    existing_environment = None
    if overwrite:
        try:
            existing_environment = client.environments_get(project_name=project_name, environment_name=environment_name)
        except api.exceptions.ApiException:
            # Do nothing if the environment doesn't exist
            pass

    kwargs = define_environment(kwargs, yaml_content, extra_yaml_fields=["ignore_file"])
    kwargs["ignore_file"] = DEFAULT_IGNORE_FILE if kwargs["ignore_file"] is None else kwargs["ignore_file"]

    if directory:
        archive_path, _ = zip_dir(
            directory=directory,
            output_path=output_path,
            ignore_filename=kwargs["ignore_file"],
            prefix=environment_name,
            force=assume_yes,
            package_directory="environment_package",
        )

    try:
        if not (overwrite and existing_environment):
            environment = api.EnvironmentCreate(**{k: kwargs[k] for k in ENVIRONMENT_CREATE_FIELDS if k in kwargs})
            client.environments_create(project_name=project_name, data=environment)

        if overwrite and existing_environment:
            environment = api.EnvironmentUpdate(
                **{k: kwargs[k] for k in ENVIRONMENT_UPDATE_FIELDS if kwargs.get(k, None) is not None}
            )
            client.environments_update(project_name=project_name, environment_name=environment_name, data=environment)

        client.environment_revisions_file_upload(
            project_name=project_name, environment_name=environment_name, file=archive_path, _progress_bar=progress_bar
        )
        client.api_client.close()
    except Exception as e:
        if directory and os.path.isfile(archive_path) and not store_archive:
            os.remove(archive_path)
        client.api_client.close()
        raise e

    if directory and os.path.isfile(archive_path):
        if store_archive:
            if not quiet:
                click.echo(f"Created archive: {archive_path}")
        else:
            os.remove(archive_path)

    if not quiet:
        click.echo("Environment was successfully deployed")
