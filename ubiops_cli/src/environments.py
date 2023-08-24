import click
import ubiops as api

from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.src.helpers.environment_helpers import define_environment, ENVIRONMENT_OUTPUT_FIELDS, \
    ENVIRONMENT_FIELDS_RENAMED, ENVIRONMENT_REQUIRED_FIELDS, ENVIRONMENT_FIELDS_UPDATE
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers.wait_for import wait_for
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import init_client, read_yaml, write_yaml, get_current_project

LIST_ITEMS = ['last_updated', 'name', 'base_environment', 'labels']


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

    print_list(
        items=environments,
        attrs=LIST_ITEMS,
        rename_cols=ENVIRONMENT_FIELDS_RENAMED,
        sorting_col=1,
        fmt=format_
    )


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
    environment_display_name: Custom environment for Python 3.9
    environment_description: Environment created via command line.
    environment_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    base_environment: python3-9
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
            item=environment,
            required_front=["name", "display_name"],
            optional=["description", "labels"],
            required_end=["base_environment"],
            rename=ENVIRONMENT_FIELDS_RENAMED,
            as_str=False
        )

        yaml_file = write_yaml(output_path, dictionary, default_file_name="environment.yaml")
        if not quiet:
            click.echo(f"Environment file stored in: {yaml_file}")

    else:
        print_item(
            item=environment,
            row_attrs=LIST_ITEMS,
            required_front=['id', 'creation_date', 'name'],
            optional=ENVIRONMENT_OUTPUT_FIELDS,
            required_end=["active_revision", "active_build", "latest_revision", "latest_build"],
            rename=ENVIRONMENT_FIELDS_RENAMED,
            fmt=format_
        )


@commands.command(name="create", short_help="Create an environment")
@options.ENVIRONMENT_NAME_OVERRULE
@options.BASE_ENVIRONMENT
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
    environment_display_name: Custom environment for Python 3.9
    environment_description: Environment created via command line.
    environment_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    base_environment: python3-9
    ```

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
    options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
    The environment name can either be passed as command argument or specified inside the yaml file using
    `<environment_name>`.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=[])

    assert 'environment_name' in yaml_content or 'environment_name' in kwargs, \
        'Please, specify the environment name in either the yaml file or as a command argument'

    environment = define_environment(fields=kwargs, yaml_content=yaml_content, update=True)

    if any(field not in environment for field in ENVIRONMENT_REQUIRED_FIELDS):
        raise UbiOpsException(
            f"Please provide all required fields for environment creation: {', '.join(ENVIRONMENT_REQUIRED_FIELDS)}"
        )

    client = init_client()
    environment_response = client.environments_create(project_name=project_name, data=environment)
    client.api_client.close()

    print_item(
        item=environment_response,
        row_attrs=LIST_ITEMS,
        required_front=['id', 'name'],
        optional=ENVIRONMENT_OUTPUT_FIELDS,
        required_end=["active_revision", "active_build", "latest_revision", "latest_build"],
        rename=ENVIRONMENT_FIELDS_RENAMED,
        fmt=format_
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

    kwargs['environment_name'] = new_name
    kwargs = define_environment(fields=kwargs, yaml_content=yaml_content, update=True)
    environment = api.EnvironmentUpdate(
        **{k: kwargs[k] for k in ENVIRONMENT_FIELDS_UPDATE if k in kwargs and kwargs[k] is not None}
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
        stream_logs=stream_logs
    )
    client.api_client.close()
