import ubiops as api

from pkg.utils import get_current_project, init_client
from pkg.src.helpers.formatting import print_list, print_item
from pkg.src.helpers.options import *


LIST_ITEMS = ['id', 'name', 'value', 'secret', 'inheritance_type', 'inheritance_name']
WARNING_MSG = "Make sure you provided the right environment variable ID and the right inheritance level."


@click.group("environment_variables")
def commands():
    """Manage your environment variables."""
    pass


@commands.command("list")
@MODEL_NAME_OPTIONAL
@VERSION_NAME_OPTIONAL
@LIST_FORMATS
def env_vars_list(model_name, version_name, format_):
    """
    List environment variables.

    \b
    - When model_name and version_name are provided: the environment variables will be listed on model version level.
    - When a model name is provided, but not a version name: the environment variables will be listed on model level.
    - When no model_name nor a version name is provided: the environment variables will be listed on project level.
    """

    project_name = get_current_project(error=True)

    if version_name and not model_name:
        raise Exception("Missing option <model_name>.")

    client = init_client()
    if version_name:
        response = client.model_version_environment_variables_list(project_name=project_name, model_name=model_name,
                                                                   version=version_name)
    elif model_name:
        response = client.model_environment_variables_list(project_name=project_name, model_name=model_name)
    else:
        response = client.project_environment_variables_list(project_name=project_name)
    print_list(response, LIST_ITEMS, sorting_col=1, fmt=format_)


@commands.command("create")
@ENV_VAR_NAME
@ENV_VAR_VALUE
@ENV_VAR_SECRET
@MODEL_NAME_OPTIONAL
@VERSION_NAME_OPTIONAL
@CREATE_FORMATS
def env_vars_create(env_var_name, env_var_value, secret, model_name, version_name, format_):
    """
    Create an environment variable.

    \b
    - When model_name and version_name are provided: the environment variable will be created on model version level.
    - When a model name is provided, but not a version name: the environment variable will be created on model level.
    - When no model_name nor a version name is provided: the environment variable will be created on project level.
    """

    project_name = get_current_project(error=True)

    if version_name and not model_name:
        raise Exception("Missing option <model_name>.")

    client = init_client()
    new_env_var = api.EnvironmentVariableCreate(name=env_var_name, value=env_var_value, secret=secret)
    if version_name:
        item = client.model_version_environment_variables_create(project_name=project_name, model_name=model_name,
                                                                 version=version_name, data=new_env_var)
    elif model_name:
        item = client.model_environment_variables_create(project_name=project_name, model_name=model_name,
                                                         data=new_env_var)
    else:
        item = client.project_environment_variables_create(project_name=project_name, data=new_env_var)
    print_item(item, LIST_ITEMS, fmt=format_)


@commands.command("get")
@ENV_VAR_ID
@MODEL_NAME_OPTIONAL
@VERSION_NAME_OPTIONAL
@GET_FORMATS
def env_vars_get(env_var_id, model_name, version_name, format_):
    """
    Get an environment variable.

    \b
    - When model_name and version_name are provided: the environment variable will be collected on model version level.
    - When a model name is provided, but not a version name: the environment variable will be collected on model level.
    - When no model_name nor a version name is provided: the environment variable will be collected on project level.
    """

    project_name = get_current_project(error=True)

    if version_name and not model_name:
        raise Exception("Missing option <model_name>.")

    client = init_client()
    try:
        if version_name:
            item = client.model_version_environment_variables_get(project_name=project_name, model_name=model_name,
                                                                  version=version_name, id=env_var_id)
        elif model_name:
            item = client.model_environment_variables_get(project_name=project_name, model_name=model_name,
                                                          id=env_var_id)
        else:
            item = client.project_environment_variables_get(project_name=project_name, id=env_var_id)
    except api.exceptions.ApiException as e:
        if hasattr(e, "status") and e.status == 404:
            click.echo("%s %s" % (click.style('Warning:', fg='yellow'), WARNING_MSG))
        raise e

    print_item(item, LIST_ITEMS, fmt=format_)


@commands.command("update")
@ENV_VAR_ID
@ENV_VAR_NAME_UPDATE
@ENV_VAR_VALUE
@ENV_VAR_SECRET
@MODEL_NAME_OPTIONAL
@VERSION_NAME_OPTIONAL
@QUIET
def env_vars_update(env_var_id, new_name, env_var_value, secret, model_name, version_name, quiet):
    """
    Update an environment variable.

    \b
    - When model_name and version_name are provided: the environment variable will be updated on model version level.
    - When a model name is provided, but not a version name: the environment variable will be updated on model level.
    - When no model_name nor a version name is provided: the environment variable will be updated on project level.
    """

    def define_env_var(current_name, new_name, new_value, new_secret):
        new_name = new_name if new_name else current_name
        return api.EnvironmentVariableCreate(name=new_name, value=new_value, secret=new_secret)

    project_name = get_current_project(error=True)

    if version_name and not model_name:
        raise Exception("Missing option <model_name>.")

    client = init_client()
    try:
        if version_name:
            current = client.model_version_environment_variables_get(project_name=project_name, model_name=model_name,
                                                                     version=version_name, id=env_var_id)
            new_env_var = define_env_var(current.name, new_name, env_var_value, secret)
            client.model_version_environment_variables_update(project_name=project_name, model_name=model_name,
                                                              version=version_name, id=env_var_id, data=new_env_var)
        elif model_name:
            current = client.model_environment_variables_get(project_name=project_name, model_name=model_name,
                                                             id=env_var_id)
            new_env_var = define_env_var(current.name, new_name, env_var_value, secret)
            client.model_environment_variables_update(project_name=project_name, model_name=model_name, id=env_var_id,
                                                      data=new_env_var)
        else:
            current = client.project_environment_variables_get(project_name=project_name, id=env_var_id)
            new_env_var = define_env_var(current.name, new_name, env_var_value, secret)
            client.project_environment_variables_update(project_name=project_name, id=env_var_id, data=new_env_var)
    except api.exceptions.ApiException as e:
        if hasattr(e, "status") and e.status == 404:
            click.echo("%s %s" % (click.style('Warning:', fg='yellow'), WARNING_MSG))
        raise e

    if not quiet:
        click.echo("Environment variable was successfully updated.")


@commands.command("delete")
@ENV_VAR_ID
@MODEL_NAME_OPTIONAL
@VERSION_NAME_OPTIONAL
@ASSUME_YES
@QUIET
def env_vars_delete(env_var_id, model_name, version_name, assume_yes, quiet):
    """
    Delete an environment variable.

    \b
    - When model_name and version_name are provided: the environment variable will be deleted on model version level.
    - When a model name is provided, but not a version name: the environment variable will be deleted on model level.
    - When no model_name nor a version name is provided: the environment variable will be deleted on project level.
    """

    project_name = get_current_project(error=True)

    if version_name and not model_name:
        raise Exception("Missing option <model_name>.")

    client = init_client()
    confirm_message = "Are you sure you want to delete environment variable "
    try:
        if version_name:
            response = client.model_version_environment_variables_get(project_name=project_name, model_name=model_name,
                                                                      version=version_name, id=env_var_id)
            if assume_yes or click.confirm(confirm_message + "<%s> of model <%s> version <%s> in project <%s>?"
                                           % (response.name, model_name, version_name, project_name)):
                client.model_version_environment_variables_delete(project_name=project_name, model_name=model_name,
                                                                  version=version_name, id=env_var_id)
        elif model_name:
            response = client.model_environment_variables_get(project_name=project_name, model_name=model_name,
                                                              id=env_var_id)
            if assume_yes or click.confirm(confirm_message + "<%s> of model  <%s> in project <%s>?"
                                           % (response.name, model_name, project_name)):
                client.model_environment_variables_delete(project_name=project_name, model_name=model_name,
                                                          id=env_var_id)
        else:
            response = client.project_environment_variables_get(project_name=project_name, id=env_var_id)
            if assume_yes or click.confirm(confirm_message + "<%s> of project <%s>?" % (response.name, project_name)):
                client.project_environment_variables_delete(project_name=project_name, id=env_var_id)
    except api.exceptions.ApiException as e:
        if hasattr(e, "status") and e.status == 404:
            click.echo("%s %s" % (click.style('Warning:', fg='yellow'), WARNING_MSG))
        raise e

    if not quiet:
        click.echo("Environment variable was successfully deleted.")
