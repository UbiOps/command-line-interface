import ubiops as api
from pkg.utils import set_dict_default, set_object_default
from pkg.constants import ML_MODEL_FILE_NAME_KEY, ML_MODEL_FILE_NAME_VALUE, SYS_DEPLOYMENT_FILE_NAME_KEY, \
    SYS_DEPLOYMENT_FILE_NAME_VALUE
from pkg.src.helpers.helpers import strings_to_dict


DEPLOYMENT_REQUIRED_FIELDS = ['input_type', 'output_type']
DEPLOYMENT_VERSION_FIELDS = [
    'description', 'labels', 'language', 'memory_allocation', 'minimum_instances', 'maximum_instances',
    'maximum_idle_time'
]
DEPLOYMENT_VERSION_FIELDS_UPDATE = [
    'description', 'labels', 'memory_allocation', 'minimum_instances', 'maximum_instances', 'maximum_idle_time'
]
DEPLOYMENT_VERSION_FIELDS_WAIT = ['memory_allocation', 'minimum_instances', 'maximum_instances', 'maximum_idle_time']
DEPLOYMENT_VERSION_FIELD_TYPES = {
    'language': str,
    'memory_allocation': int,
    'minimum_instances': int,
    'maximum_instances': int,
    'maximum_idle_time': int,
    'description': str,
    'labels': dict
}
DEPLOYMENT_VERSION_FIELDS_RENAMED = {'description': 'version_description', 'labels': 'version_labels'}


def set_deployment_version_defaults(fields, yaml_content, existing_version, extra_yaml_fields):
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
    :param ubiops.DeploymentVersion existing_version: the current deployment version if exists
    :param list(str) extra_yaml_fields: additional yaml fields that are not DeploymentVersion parameters,
        e.g., deployment_file
    :return dict: a dictionary containing all DeploymentVersion parameters (+extra yaml fields)
    """

    for k, v in DEPLOYMENT_VERSION_FIELDS_RENAMED.items():
        fields[k] = fields[v]
        del fields[v]

    for k in [k for k, v in DEPLOYMENT_VERSION_FIELD_TYPES.items() if v == dict]:
        if k in fields and fields[k] is not None:
            fields[k] = strings_to_dict(fields[k])

    if yaml_content:
        for p in [*DEPLOYMENT_VERSION_FIELDS, *extra_yaml_fields]:
            input_field = DEPLOYMENT_VERSION_FIELDS_RENAMED[p] if p in DEPLOYMENT_VERSION_FIELDS_RENAMED else p
            value = fields[input_field] if input_field in fields else None
            fields[p] = set_dict_default(
                value, yaml_content, input_field,
                set_type=DEPLOYMENT_VERSION_FIELD_TYPES[p] if p in DEPLOYMENT_VERSION_FIELD_TYPES else str
            )

    if existing_version:
        for p in DEPLOYMENT_VERSION_FIELDS:
            value = fields[p] if p in fields else None
            fields[p] = set_object_default(value, existing_version, p)

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
        elif (deployment_file != SYS_DEPLOYMENT_FILE_NAME_VALUE
              and deployment_file != "%s.py" % SYS_DEPLOYMENT_FILE_NAME_VALUE
              and deployment_file != ML_MODEL_FILE_NAME_VALUE
              and deployment_file != "%s.py" % ML_MODEL_FILE_NAME_VALUE):
            # Create environment variable
            has_changed_env_vars = True
            client.deployment_version_environment_variables_create(
                project_name=project, deployment_name=deployment, version=version, data=new_env_var
            )
    return has_changed_env_vars


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
    version = api.DeploymentVersionUpdate(
        version=version_name, **{k: kwargs[k] for k in DEPLOYMENT_VERSION_FIELDS_UPDATE}
    )

    if (hasattr(existing_version, 'language') and 'language' in kwargs
            and existing_version.language != kwargs['language']):
        raise Exception("The programming language of an existing version cannot be changed")

    has_changed_fields = False
    for field in DEPLOYMENT_VERSION_FIELDS_WAIT:
        if (hasattr(existing_version, field) and hasattr(version, field)
                and getattr(existing_version, field) != getattr(version, field)):
            has_changed_fields = True

    client.deployment_versions_update(
        project_name=project_name, deployment_name=deployment_name, version=version_name, data=version
    )
    return has_changed_fields
