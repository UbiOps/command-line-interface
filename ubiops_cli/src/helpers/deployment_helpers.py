import ubiops as api
from ubiops_cli.utils import set_dict_default
from ubiops_cli.constants import ML_MODEL_FILE_NAME_KEY, ML_MODEL_FILE_NAME_VALUE, SYS_DEPLOYMENT_FILE_NAME_KEY, \
    SYS_DEPLOYMENT_FILE_NAME_VALUE
from ubiops_cli.src.helpers.helpers import strings_to_dict


DEPLOYMENT_REQUIRED_FIELDS = ['input_type', 'output_type']
DEPLOYMENT_VERSION_CREATE_FIELDS = [
    'description', 'labels', 'language', 'environment', 'instance_type', 'minimum_instances', 'maximum_instances',
    'maximum_idle_time', 'request_retention_mode', 'request_retention_time', 'maximum_queue_size_express',
    'maximum_queue_size_batch', 'static_ip'
]
DEPLOYMENT_VERSION_GET_FIELDS = [
    'description', 'labels', 'environment', 'instance_type', 'minimum_instances', 'maximum_instances',
    'maximum_idle_time', 'request_retention_mode', 'request_retention_time', 'maximum_queue_size_express',
    'maximum_queue_size_batch', 'has_request_method', 'has_requests_method', 'static_ip'
]
DEPLOYMENT_VERSION_FIELDS_UPDATE = [
    'version', 'description', 'labels', 'environment', 'instance_type', 'minimum_instances', 'maximum_instances',
    'maximum_idle_time', 'request_retention_mode', 'request_retention_time', 'maximum_queue_size_express',
    'maximum_queue_size_batch', 'static_ip'
]
DEPLOYMENT_VERSION_FIELDS_WAIT = ['instance_type', 'minimum_instances', 'maximum_instances', 'maximum_idle_time']
DEPLOYMENT_VERSION_FIELD_TYPES = {
    'language': str,
    'environment': str,
    'instance_type': str,
    'minimum_instances': int,
    'maximum_instances': int,
    'maximum_idle_time': int,
    'description': str,
    'labels': dict,
    'request_retention_mode': str,
    'request_retention_time': int,
    'maximum_queue_size_express': int,
    'maximum_queue_size_batch': int,
    'has_request_method': bool,
    'has_requests_method': bool,
    'static_ip': bool
}
DEPLOYMENT_VERSION_FIELDS_RENAMED = {
    'version': 'version_name', 'description': 'version_description', 'labels': 'version_labels'
}


def define_deployment_version(fields, yaml_content, extra_yaml_fields):
    """
    Define deployment version fields

    For each field i in [DEPLOYMENT_VERSION_FIELDS + extra_yaml_fields]:
    - Use value in fields if specified
    - If not; Use value in yaml content if specified
    - If not; Use existing version (this is only used for updating, not creating)

    Rename field-key if the key is in DEPLOYMENT_VERSION_FIELDS_RENAMED.values(). This is done to
    solve inconsistencies between CLI options/yaml keys and API parameters.

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :param list(str) extra_yaml_fields: additional yaml fields that are not DeploymentVersion parameters,
        e.g., deployment_file
    :return dict: a dictionary containing all DeploymentVersion parameters (+extra yaml fields)
    """

    for k, yaml_key in DEPLOYMENT_VERSION_FIELDS_RENAMED.items():
        fields[k] = fields.pop(yaml_key, None)

    for k in [k for k, v in DEPLOYMENT_VERSION_FIELD_TYPES.items() if v == dict]:
        if k in fields and fields[k] is not None:
            fields[k] = strings_to_dict(fields[k])

    if yaml_content:
        for k in [*DEPLOYMENT_VERSION_CREATE_FIELDS, *extra_yaml_fields]:
            fields[k] = set_dict_default(
                value=fields.get(k, None),
                defaults_dict=yaml_content,
                default_key=DEPLOYMENT_VERSION_FIELDS_RENAMED.get(k, k),
                set_type=DEPLOYMENT_VERSION_FIELD_TYPES.get(k, str)
            )

    return fields


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
                        project_name=project, deployment_name=deployment, version=version,
                        id=current_env_var[0].id, data=new_env_var
                    )
                else:
                    # Overwrite inherited environment variable
                    client.deployment_version_environment_variables_create(
                        project_name=project, deployment_name=deployment, version=version, data=new_env_var
                    )
        elif deployment_file not in [
            SYS_DEPLOYMENT_FILE_NAME_VALUE, ML_MODEL_FILE_NAME_VALUE, f"{SYS_DEPLOYMENT_FILE_NAME_VALUE}.py",
            f"{ML_MODEL_FILE_NAME_VALUE}.py", f"{SYS_DEPLOYMENT_FILE_NAME_VALUE}.R", f"{ML_MODEL_FILE_NAME_VALUE}.R"
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
