import click
import ubiops as api

from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.utils import get_current_project, init_client, read_yaml, check_required_fields_in_list
from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers import options


LIST_ITEMS = ["id", "name", "value"]


def create_env_secret(project_name, environment_name, env_secret_name, env_secret_value, overwrite=False):
    """
    Create an environment variable either on project level, deployment level or deployment version level

    :param str project_name: name of the project
    :param str environment_name: name of the environment
    :param str env_secret_name: name of the environment secret
    :param str env_secret_value: value of the environment secret
    :param bool overwrite: whether to allow overwriting an existing environment secret
    """

    client = init_client()
    existing_env_secret = None
    if overwrite:
        try:
            existing_env_secret = client.environment_secrets_get(
                project_name=project_name, environment_name=environment_name, id=env_secret_name
            )
        except api.exceptions.ApiException:
            # Do nothing if env secret doesn't exist
            pass

    data = api.EnvironmentVariableCreate(name=env_secret_name, value=env_secret_value, secret=True)
    if existing_env_secret:
        item = client.environment_secrets_update(
            project_name=project_name, environment_name=environment_name, id=data.name, data=data
        )
    else:
        item = client.environment_secrets_create(
            project_name=project_name, environment_name=environment_name, data=data
        )

    client.api_client.close()
    return item


@click.group(name=["environment_secrets", "secrets"], short_help="Manage your environment secrets")
def commands():
    """
    Manage your environment secrets.
    """

    return


# pylint: disable=too-many-arguments
@commands.command(name="create", short_help="Create an environment secret")
@options.ENVIRONMENT_NAME_OPTION
@options.ENV_SECRET_NAME
@options.ENV_SECRET_VALUE
@options.ENV_SECRET_YAML_FILE
@options.OVERWRITE
@options.CREATE_FORMATS
def env_secrets_create(environment_name, env_secret_name, env_secret_value, yaml_file, overwrite, format_):
    """
    Create an environment secret.

    Use `--overwrite` flag to update the environment secret if it already exists.

    \b
    It is possible to create multiple environment secrets at once by passing a yaml file.
    The structure of this file is assumed to look like:
    ```
    environment_secrets:
      - name: env_secret_1
        value: value_1
      - name: env_secret_2
        value: value_2
      - name: env_secret_3
        value: value_3
    ```
    """

    project_name = get_current_project(error=True)

    if not yaml_file and not env_secret_name:
        raise UbiOpsException("Please, specify the environment secret in either a yaml file or as a command argument")
    if yaml_file and (env_secret_name or env_secret_value):
        raise UbiOpsException("Please, use either a yaml file or command options, not both")

    if yaml_file:
        yaml_content = read_yaml(yaml_file, required_fields=["environment_secrets"])
        check_required_fields_in_list(
            input_dict=yaml_content, list_name="environment_secrets", required_fields=["name", "value"]
        )

        items = []
        for env_secret in yaml_content["environment_secrets"]:
            item = create_env_secret(
                project_name=project_name,
                environment_name=environment_name,
                env_secret_name=env_secret["name"],
                env_secret_value=env_secret["value"],
                overwrite=overwrite,
            )
            items.append(item)
        print_list(items, LIST_ITEMS, fmt=format_)
    else:
        item = create_env_secret(
            project_name=project_name,
            environment_name=environment_name,
            env_secret_name=env_secret_name,
            env_secret_value=env_secret_value,
            overwrite=overwrite,
        )
        print_item(item, LIST_ITEMS, fmt=format_)


@commands.command(name="list", short_help="List environment secrets")
@options.ENVIRONMENT_NAME_OPTION
@options.LIST_FORMATS
def env_secrets_list(environment_name, format_):
    """
    List environment secrets.
    """

    client = init_client()
    response = client.environment_secrets_list(
        project_name=get_current_project(error=True), environment_name=environment_name
    )
    client.api_client.close()

    print_list(response, LIST_ITEMS, sorting_col=1, fmt=format_)


@commands.command(name="get", short_help="Get an environment secret")
@options.ENVIRONMENT_NAME_OPTION
@options.ENV_SECRET_ID
@options.ENV_SECRET_NAME
@options.GET_FORMATS
def env_secrets_get(environment_name, env_secret_id, env_secret_name, format_):
    """
    Get an environment secret.
    """

    if env_secret_id and env_secret_name:
        raise UbiOpsException("Please use either the environment secret ID or name, not both")

    if not env_secret_id and not env_secret_name:
        raise UbiOpsException("Please provide either the environment secret ID or name")

    project_name = get_current_project(error=True)

    client = init_client()
    item = client.environment_secrets_get(
        project_name=project_name,
        environment_name=environment_name,
        id=env_secret_id if env_secret_id else env_secret_name,
    )
    client.api_client.close()
    print_item(item, LIST_ITEMS, fmt=format_)


@commands.command(name="update", short_help="Update an environment secret")
@options.ENVIRONMENT_NAME_OPTION
@options.ENV_SECRET_ID_REQUIRED
@options.ENV_SECRET_NAME
@options.ENV_SECRET_VALUE
@options.QUIET
def env_secrets_update(environment_name, env_secret_id, env_secret_name, env_secret_value, quiet):
    """
    Update an environment secret.
    """

    project_name = get_current_project(error=True)

    client = init_client()

    current = client.environment_secrets_get(
        project_name=project_name, environment_name=environment_name, id=env_secret_id
    )
    data = api.EnvironmentVariableCreate(
        name=env_secret_name if env_secret_name else current.name, value=env_secret_value, secret=True
    )
    client.environment_secrets_update(
        project_name=project_name, environment_name=environment_name, id=env_secret_id, data=data
    )
    client.api_client.close()

    if not quiet:
        click.echo("Environment secret was successfully updated")


@commands.command(name="delete", short_help="Delete an environment secret")
@options.ENVIRONMENT_NAME_OPTION
@options.ENV_SECRET_ID_REQUIRED
@options.ASSUME_YES
@options.QUIET
def env_secrets_delete(environment_name, env_secret_id, assume_yes, quiet):
    """
    Delete an environment secret.
    """

    client = init_client()
    confirm_message = "Are you sure you want to delete the environment secret "
    if assume_yes or click.confirm(confirm_message):
        client.environment_secrets_delete(
            project_name=get_current_project(error=True), environment_name=environment_name, id=env_secret_id
        )

    client.api_client.close()

    if not quiet:
        click.echo("Environment secret was successfully deleted")


@commands.command(name="copy", short_help="Copy environment secrets from one environment to another")
@options.ENV_SECRETS_COPY_SOURCE_NAME
@options.ENV_SECRETS_COPY_TARGET_NAME
@options.LIST_FORMATS
def env_secrets_copy(source_name, target_name, format_):
    """
    Copy all environment secrets from one environment to another.
    """

    client = init_client()

    source = api.EnvironmentSecretCopy(source_environment=source_name)
    items = client.environment_secrets_copy(
        project_name=get_current_project(error=True), environment_name=target_name, data=source
    )

    client.api_client.close()

    print_list(items, LIST_ITEMS, fmt=format_)
