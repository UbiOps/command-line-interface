import click
import ubiops as api

from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.utils import get_current_project, init_client, read_yaml, check_required_fields_in_list
from ubiops_cli.src.helpers.formatting import print_list, print_item
from ubiops_cli.src.helpers import options


LIST_ITEMS = ['id', 'name', 'value', 'secret', 'inheritance_type', 'inheritance_name']
WARNING_MSG = "Make sure you provided the right environment variable ID and the right inheritance level."


# pylint: disable=too-many-arguments
def create_env_var(project_name, deployment_name, version_name, env_var_name, env_var_value, secret=False):
    """
    Create an environment variable either on project level, deployment level or deployment version level

    :param str project_name: name of the project
    :param str|None deployment_name: name of the deployment
    :param str|None version_name: version of the deployment
    :param str env_var_name: name of the environment variable
    :param str env_var_value: value of the environment variable
    :param bool secret: whether to store the environment variable as secret
    """

    client = init_client()
    new_env_var = api.EnvironmentVariableCreate(name=env_var_name, value=env_var_value, secret=secret)
    if version_name:
        item = client.deployment_version_environment_variables_create(
            project_name=project_name, deployment_name=deployment_name, version=version_name, data=new_env_var
        )
    elif deployment_name:
        item = client.deployment_environment_variables_create(
            project_name=project_name, deployment_name=deployment_name, data=new_env_var
        )
    else:
        item = client.project_environment_variables_create(project_name=project_name, data=new_env_var)
    client.api_client.close()
    return item


@click.group(name=["environment_variables", "env"], short_help="Manage your environment variables")
def commands():
    """Manage your environment variables."""

    return


@commands.command(name="list", short_help="List environment variables")
@options.DEPLOYMENT_NAME_OPTIONAL
@options.VERSION_NAME_OPTIONAL
@options.LIST_FORMATS
def env_vars_list(deployment_name, version_name, format_):
    """
    List environment variables.

    \b
    - When deployment_name and version_name are provided: the environment variables will be listed on deployment
    version level.
    - When a deployment name is provided, but not a version name: the environment variables will be listed on
    deployment level.
    - When no deployment_name nor a version name is provided: the environment variables will be listed on project level.
    """

    project_name = get_current_project(error=True)

    if version_name and not deployment_name:
        raise UbiOpsException("Missing option <deployment_name>")

    client = init_client()
    if version_name:
        response = client.deployment_version_environment_variables_list(
            project_name=project_name, deployment_name=deployment_name, version=version_name
        )
    elif deployment_name:
        response = client.deployment_environment_variables_list(
            project_name=project_name, deployment_name=deployment_name
        )
    else:
        response = client.project_environment_variables_list(project_name=project_name)
    client.api_client.close()

    print_list(response, LIST_ITEMS, sorting_col=1, fmt=format_)


# pylint: disable=too-many-arguments
@commands.command(name="create", short_help="Create an environment variable")
@options.ENV_VAR_NAME
@options.ENV_VAR_VALUE
@options.ENV_VAR_SECRET
@options.DEPLOYMENT_NAME_OPTIONAL
@options.VERSION_NAME_OPTIONAL
@options.ENV_VAR_YAML_FILE
@options.CREATE_FORMATS
def env_vars_create(env_var_name, env_var_value, secret, deployment_name, version_name, yaml_file, format_):
    """
    Create an environment variable.

    \b
    - When deployment_name and version_name are provided: the environment variable will be created on deployment
    version level.
    - When a deployment name is provided, but not a version name: the environment variable will be created on
    deployment level.
    - When no deployment_name nor a version name is provided: the environment variable will be created on project level.

    \b
    It is possible to create multiple environment variables at ones by passing a yaml file.
    The structure of this file is assumed to look like:
    ```
    environment_variables:
      - name: env_var_1
        value: value_1
      - name: env_var_2
        value: value_2
        secret: true
      - name: env_var_3
        value: value_3
        secret: true
    ```
    The 'secret' parameter is optional, and is `false` by default.
    """

    project_name = get_current_project(error=True)

    if not yaml_file and not env_var_name:
        raise UbiOpsException("Please, specify the environment variable in either a yaml file or as a command argument")
    if yaml_file and (env_var_name or env_var_value or secret):
        raise UbiOpsException("Please, use either a yaml file or command options, not both")
    if version_name and not deployment_name:
        raise UbiOpsException("Missing option <deployment_name>")

    if yaml_file:
        yaml_content = read_yaml(yaml_file, required_fields=['environment_variables'])
        check_required_fields_in_list(
            input_dict=yaml_content, list_name='environment_variables', required_fields=['name', 'value']
        )

        items = []
        for env_var in yaml_content['environment_variables']:
            secret = env_var['secret'] if 'secret' in env_var else False
            item = create_env_var(project_name, deployment_name, version_name,
                                  env_var['name'], env_var['value'], secret)
            items.append(item)
        print_list(items, LIST_ITEMS, fmt=format_)
    else:
        item = create_env_var(project_name, deployment_name, version_name, env_var_name, env_var_value, secret)
        print_item(item, LIST_ITEMS, fmt=format_)


@commands.command(name="get", short_help="Get an environment variable")
@options.ENV_VAR_ID
@options.DEPLOYMENT_NAME_OPTIONAL
@options.VERSION_NAME_OPTIONAL
@options.GET_FORMATS
def env_vars_get(env_var_id, deployment_name, version_name, format_):
    """
    Get an environment variable.

    \b
    - When deployment_name and version_name are provided: the environment variable will be collected on deployment
    version level.
    - When a deployment name is provided, but not a version name: the environment variable will be collected on
    deployment level.
    - When no deployment_name nor a version name is provided: the environment variable will be collected on
    project level.
    """

    project_name = get_current_project(error=True)

    if version_name and not deployment_name:
        raise UbiOpsException("Missing option <deployment_name>")

    client = init_client()
    try:
        if version_name:
            item = client.deployment_version_environment_variables_get(
                project_name=project_name, deployment_name=deployment_name, version=version_name, id=env_var_id
            )
        elif deployment_name:
            item = client.deployment_environment_variables_get(
                project_name=project_name, deployment_name=deployment_name, id=env_var_id
            )
        else:
            item = client.project_environment_variables_get(project_name=project_name, id=env_var_id)
    except api.exceptions.ApiException as e:
        if hasattr(e, "status") and e.status == 404:
            click.echo(f"{click.style(text='Warning:', fg='yellow')} {WARNING_MSG}")
        raise e

    client.api_client.close()
    print_item(item, LIST_ITEMS, fmt=format_)


@commands.command(name="copy", short_help="Copy environment variables")
@options.FROM_DEPLOYMENT_NAME
@options.FROM_VERSION_NAME
@options.TO_DEPLOYMENT_NAME
@options.TO_VERSION_NAME
@options.ASSUME_YES
def env_vars_copy(from_deployment, from_version, to_deployment, to_version, assume_yes):
    """
    Copy environment variables from one deployment (version) to another deployment (version).
    """
    project_name = get_current_project(error=True)
    client = init_client()

    if from_version is None:
        data = api.EnvironmentVariableCopy(source_deployment=from_deployment)
        env_vars = client.deployment_environment_variables_list(project_name=project_name,
                                                                deployment_name=from_deployment)
    else:
        data = api.EnvironmentVariableCopy(source_deployment=from_deployment, source_version=from_version)
        env_vars = client.deployment_version_environment_variables_list(
            project_name=project_name, deployment_name=from_deployment, version=from_version
        )

    if not assume_yes:
        env_vars = [env for env in env_vars if env.inheritance_type is None]
        print_list(items=env_vars, attrs=['id', 'name', 'value', 'secret'], sorting_col=1, fmt='table')
        click.secho("All destination variables with the same name will be overwritten by this action\n", fg='yellow')

    confirm_message = f"Are you sure you want to copy {click.style(text='ALL', fg='red')} these environment variables?"

    if assume_yes or click.confirm(confirm_message):
        if to_version is None:
            client.deployment_environment_variables_copy(
                project_name=project_name, deployment_name=to_deployment, data=data
            )
        else:
            client.deployment_version_environment_variables_copy(
                project_name=project_name, deployment_name=to_deployment, version=to_version, data=data
            )
    client.api_client.close()


# pylint: disable=too-many-arguments
@commands.command(name="update", short_help="Update an environment variable")
@options.ENV_VAR_ID
@options.ENV_VAR_NAME_UPDATE
@options.ENV_VAR_VALUE
@options.ENV_VAR_SECRET
@options.DEPLOYMENT_NAME_OPTIONAL
@options.VERSION_NAME_OPTIONAL
@options.QUIET
def env_vars_update(env_var_id, new_name, env_var_value, secret, deployment_name, version_name, quiet):
    """
    Update an environment variable.

    \b
    - When deployment_name and version_name are provided: the environment variable will be updated on deployment
    version level.
    - When a deployment name is provided, but not a version name: the environment variable will be updated on
    deployment level.
    - When no deployment_name nor a version name is provided: the environment variable will be updated on
    project level.
    """

    def define_env_var(current_name, new_env_var_name, new_env_var_value, new_secret):
        new_env_var_name = new_env_var_name if new_env_var_name else current_name
        return api.EnvironmentVariableCreate(name=new_env_var_name, value=new_env_var_value, secret=new_secret)

    project_name = get_current_project(error=True)

    if version_name and not deployment_name:
        raise UbiOpsException("Missing option <deployment_name>")

    client = init_client()
    try:
        if version_name:
            current = client.deployment_version_environment_variables_get(
                project_name=project_name, deployment_name=deployment_name, version=version_name, id=env_var_id
            )
            new_env_var = define_env_var(current.name, new_name, env_var_value, secret)
            client.deployment_version_environment_variables_update(
                project_name=project_name, deployment_name=deployment_name, version=version_name,
                id=env_var_id, data=new_env_var
            )
        elif deployment_name:
            current = client.deployment_environment_variables_get(
                project_name=project_name, deployment_name=deployment_name, id=env_var_id
            )
            new_env_var = define_env_var(current.name, new_name, env_var_value, secret)
            client.deployment_environment_variables_update(
                project_name=project_name, deployment_name=deployment_name, id=env_var_id, data=new_env_var
            )
        else:
            current = client.project_environment_variables_get(project_name=project_name, id=env_var_id)
            new_env_var = define_env_var(current.name, new_name, env_var_value, secret)
            client.project_environment_variables_update(project_name=project_name, id=env_var_id, data=new_env_var)
    except api.exceptions.ApiException as e:
        if hasattr(e, "status") and e.status == 404:
            click.echo(f"{click.style(text='Warning:', fg='yellow')} {WARNING_MSG}")
        raise e
    client.api_client.close()

    if not quiet:
        click.echo("Environment variable was successfully updated")


@commands.command(name="delete", short_help="Delete an environment variable")
@options.ENV_VAR_ID
@options.DEPLOYMENT_NAME_OPTIONAL
@options.VERSION_NAME_OPTIONAL
@options.ASSUME_YES
@options.QUIET
def env_vars_delete(env_var_id, deployment_name, version_name, assume_yes, quiet):
    """
    Delete an environment variable.

    \b
    - When deployment_name and version_name are provided: the environment variable will be deleted on deployment
    version level.
    - When a deployment name is provided, but not a version name: the environment variable will be deleted on
    deployment level.
    - When no deployment_name nor a version name is provided: the environment variable will be deleted on
    project level.
    """

    project_name = get_current_project(error=True)

    if version_name and not deployment_name:
        raise UbiOpsException("Missing option <deployment_name>")

    client = init_client()
    confirm_message = "Are you sure you want to delete environment variable "
    try:
        if version_name:
            response = client.deployment_version_environment_variables_get(
                project_name=project_name, deployment_name=deployment_name, version=version_name, id=env_var_id
            )
            if assume_yes or click.confirm(f"{confirm_message}<{response.name}> of deployment <{deployment_name}>"
                                           f" version <{version_name}> in project <{project_name}>?"):
                client.deployment_version_environment_variables_delete(
                    project_name=project_name, deployment_name=deployment_name, version=version_name, id=env_var_id
                )
        elif deployment_name:
            response = client.deployment_environment_variables_get(
                project_name=project_name, deployment_name=deployment_name, id=env_var_id
            )
            if assume_yes or click.confirm(f"{confirm_message}<{response.name}> of deployment  <{deployment_name}>"
                                           f" in project <{project_name}>?"):
                client.deployment_environment_variables_delete(
                    project_name=project_name, deployment_name=deployment_name, id=env_var_id
                )
        else:
            response = client.project_environment_variables_get(project_name=project_name, id=env_var_id)
            if assume_yes or click.confirm(f"{confirm_message}<{response.name}> of project <{project_name}>?"):
                client.project_environment_variables_delete(project_name=project_name, id=env_var_id)
    except api.exceptions.ApiException as e:
        if hasattr(e, "status") and e.status == 404:
            click.echo(f"{click.style('Warning:', fg='yellow')} {WARNING_MSG}")
        raise e
    client.api_client.close()

    if not quiet:
        click.echo("Environment variable was successfully deleted")
