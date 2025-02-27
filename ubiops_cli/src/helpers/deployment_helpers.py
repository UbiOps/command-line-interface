import ubiops as api
from ubiops_cli.constants import (
    ML_MODEL_FILE_NAME_KEY,
    ML_MODEL_FILE_NAME_VALUE,
    SYS_DEPLOYMENT_FILE_NAME_KEY,
    SYS_DEPLOYMENT_FILE_NAME_VALUE,
)
from ubiops_cli.src.helpers.helpers import define_object


DEPLOYMENT_DETAILS = ["name", "project", "description", "labels", "supports_request_format"]
DEPLOYMENT_DETAILS_OPTIONAL = [
    "input_type",
    "output_type",
    "input_fields name",
    "input_fields data_type",
    "output_fields name",
    "output_fields data_type",
]
DEPLOYMENT_FIELDS_RENAMED = {
    "name": "deployment_name",
    "description": "deployment_description",
    "labels": "deployment_labels",
    "supports_request_format": "deployment_supports_request_format",
}
DEPLOYMENT_CREATE_FIELDS = [
    "name",
    "description",
    "labels",
    "supports_request_format",
    "input_type",
    "output_type",
    "input_fields",
    "output_fields",
]
DEPLOYMENT_UPDATE_FIELDS = [
    "name",
    "description",
    "labels",
    "input_type",
    "output_type",
    "input_fields",
    "output_fields",
    "default_version",
]
DEPLOYMENT_FIELD_TYPES = {
    "name": str,
    "description": str,
    "labels": dict,
    "supports_request_format": bool,
    "input_type": str,
    "output_type": str,
    "input_fields": None,
    "output_fields": None,
}

DEPLOYMENT_VERSION_CREATE_FIELDS = [
    "description",
    "labels",
    "environment",
    "instance_type",
    "instance_type_group_id",
    "instance_type_group_name",
    "scaling_strategy",
    "minimum_instances",
    "maximum_instances",
    "instance_processes",
    "maximum_idle_time",
    "request_retention_mode",
    "request_retention_time",
    "maximum_queue_size_express",
    "maximum_queue_size_batch",
    "static_ip",
    "ports",
]
DEPLOYMENT_VERSION_DETAILS = [
    "description",
    "labels",
    "environment",
    "instance_type",
    "instance_type_group_id",
    "instance_type_group_name",
    "static_ip",
    "ports",
    "minimum_instances",
    "maximum_instances",
]
SUPPORTS_REQUEST_FORMAT_DETAILS = [
    "instance_processes",
    "maximum_idle_time",
    "scaling_strategy",
    "request_retention_mode",
    "request_retention_time",
    "maximum_queue_size_express",
    "maximum_queue_size_batch",
    "has_request_method",
    "has_requests_method",
]
DEPLOYMENT_VERSION_FIELDS_UPDATE = ["version"] + DEPLOYMENT_VERSION_CREATE_FIELDS
DEPLOYMENT_VERSION_FIELDS_WAIT = [
    "instance_type",
    "instance_type_group_id",
    "instance_type_group_name",
    "minimum_instances",
    "maximum_instances",
    "maximum_idle_time",
]
DEPLOYMENT_VERSION_FIELD_TYPES = {
    "environment": str,
    "instance_type": str,
    "instance_type_group_id": str,
    "instance_type_group_name": str,
    "scaling_strategy": str,
    "minimum_instances": int,
    "maximum_instances": int,
    "instance_processes": int,
    "maximum_idle_time": int,
    "description": str,
    "labels": dict,
    "request_retention_mode": str,
    "request_retention_time": int,
    "maximum_queue_size_express": int,
    "maximum_queue_size_batch": int,
    "has_request_method": bool,
    "has_requests_method": bool,
    "static_ip": bool,
    "ports": None,
}
DEPLOYMENT_VERSION_FIELDS_RENAMED = {
    "version": "version_name",
    "description": "version_description",
    "labels": "version_labels",
}


def define_deployment(fields, yaml_content, extra_yaml_fields=None):
    """
    Define deployment fields by combining the given fields and the content of a yaml file. The given fields are
    prioritized over the content of the yaml file; if they are not given the value in the yaml file is used (if
    present).

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :param list(str) extra_yaml_fields: additional yaml fields that are not Deployment create parameters,
        e.g., default_version
    :return dict: a dictionary containing all Deployment parameters
    """

    extra_yaml_fields = [] if extra_yaml_fields is None else extra_yaml_fields

    return define_object(
        fields=fields,
        yaml_content=yaml_content,
        field_names=[*DEPLOYMENT_CREATE_FIELDS, *extra_yaml_fields],
        rename_field_names=DEPLOYMENT_FIELDS_RENAMED,
        field_types=DEPLOYMENT_FIELD_TYPES,
    )


def define_deployment_version(fields, yaml_content, extra_yaml_fields):
    """
    Define deployment version fields by combining the given fields and the content of a yaml file. The given fields are
    prioritized over the content of the yaml file; if they are not given the value in the yaml file is used (if
    present).

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :param list(str) extra_yaml_fields: additional yaml fields that are not DeploymentVersion parameters,
        e.g., deployment_file
    :return dict: a dictionary containing all DeploymentVersion parameters (+extra yaml fields)
    """

    return define_object(
        fields=fields,
        yaml_content=yaml_content,
        field_names=[*DEPLOYMENT_VERSION_CREATE_FIELDS, *extra_yaml_fields],
        rename_field_names=DEPLOYMENT_VERSION_FIELDS_RENAMED,
        field_types=DEPLOYMENT_VERSION_FIELD_TYPES,
    )


def update_deployment_file(client, project, deployment, version, deployment_file):
    """
    If deployment_file is specified:
    - If an environment variable SYS_DEPLOYMENT_FILE_NAME_KEY exists and value is not equal:
        - If on deployment version level: update
        - If inherited: create one on deployment version level
    - If not; create one if it's not the default SYS_DEPLOYMENT_FILE_NAME_VALUE.

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param str project: the name of the project
    :param str deployment: the name of the deployment
    :param str version: the name of the deployment version
    :param str deployment_file: the name of the deployment file in the user code, defaults to 'deployment.py'
    :return boolean: whether the environment variables were changed or not
    """

    has_changed_env_vars = False
    if deployment_file:
        deployment_file = str(deployment_file).strip()
        env_vars = client.deployment_version_environment_variables_list(
            project_name=project, deployment_name=deployment, version=version
        )

        env_var_name = SYS_DEPLOYMENT_FILE_NAME_KEY
        current_env_var = [i for i in env_vars if i.name == env_var_name]
        current_env_var_old = [i for i in env_vars if i.name == ML_MODEL_FILE_NAME_KEY]
        if len(current_env_var) == 0 and len(current_env_var_old) > 0:
            # For backward compatibility
            env_var_name = ML_MODEL_FILE_NAME_KEY

        new_env_var = api.EnvironmentVariableCreate(name=env_var_name, value=deployment_file, secret=False)
        if len(current_env_var) > 0:
            # Environment variable already exists
            if current_env_var[0].value != deployment_file:
                has_changed_env_vars = True
                if current_env_var[0].inheritance_type is None:
                    # Update environment variable
                    new_env_var = api.EnvironmentVariableCreate(
                        name=env_var_name, value=deployment_file, secret=current_env_var[0].secret
                    )
                    client.deployment_version_environment_variables_update(
                        project_name=project,
                        deployment_name=deployment,
                        version=version,
                        id=current_env_var[0].id,
                        data=new_env_var,
                    )
                else:
                    # Overwrite inherited environment variable
                    client.deployment_version_environment_variables_create(
                        project_name=project, deployment_name=deployment, version=version, data=new_env_var
                    )
        elif deployment_file not in [
            SYS_DEPLOYMENT_FILE_NAME_VALUE,
            ML_MODEL_FILE_NAME_VALUE,
            f"{SYS_DEPLOYMENT_FILE_NAME_VALUE}.py",
            f"{ML_MODEL_FILE_NAME_VALUE}.py",
            f"{SYS_DEPLOYMENT_FILE_NAME_VALUE}.R",
            f"{ML_MODEL_FILE_NAME_VALUE}.R",
        ]:
            # Create environment variable
            has_changed_env_vars = True
            client.deployment_version_environment_variables_create(
                project_name=project, deployment_name=deployment, version=version, data=new_env_var
            )
    return has_changed_env_vars


# pylint: disable=too-many-arguments
def update_existing_deployment_version(client, project_name, deployment_name, version_name, existing_version, kwargs):
    """
    If deployment_file is specified:
    - If an environment variable SYS_DEPLOYMENT_FILE_NAME_KEY exists and value is not equal:
        - If on deployment version level: update
        - If inherited: create one on deployment version level
    - If not; create one if it's not the default SYS_DEPLOYMENT_FILE_NAME_VALUE.

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param str project_name: the name of the project
    :param str deployment_name: the name of the deployment
    :param str version_name: the name of the deployment version
    :param ubiops.DeploymentVersion existing_version: the current deployment version
    :param dict kwargs: the deployment version content to update to
    :return boolean: whether deployment version fields were changed or not
    """

    update_fields = {k: kwargs[k] for k in kwargs if kwargs[k] is not None}

    version = api.DeploymentVersionUpdate(
        **{k: update_fields[k] for k in DEPLOYMENT_VERSION_FIELDS_UPDATE if k in update_fields}
    )

    has_changed_fields = False
    for field in DEPLOYMENT_VERSION_FIELDS_WAIT:
        has_field = hasattr(existing_version, field) and field in update_fields
        if has_field and getattr(existing_version, field) != update_fields[field]:
            has_changed_fields = True

    client.deployment_versions_update(
        project_name=project_name, deployment_name=deployment_name, version=version_name, data=version
    )
    return has_changed_fields


def set_default_scaling_parameters(details, supports_request_format, update=False):
    """
    Set the default scaling parameters 'minimum_instances' and 'maximum_instances' based on whether the deployment
    supports request format

    :param dict details: the details for version creation
    :param bool supports_request_format: whether the deployment supports request format
    :param bool update: whether the default is set for updating the deployment version instead of creation
    """

    if not supports_request_format:
        # Auto-scaling is only supported for request format, use static 1 instead
        if details.get("minimum_instances", None) is None:
            if not update:
                details["minimum_instances"] = 1
                details["maximum_instances"] = 1
        else:
            details["maximum_instances"] = details["minimum_instances"]

    return details
