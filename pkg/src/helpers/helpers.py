import ubiops as api
from pkg.utils import set_dict_default, set_object_default, check_required_fields, parse_json
from pkg.constants import ML_MODEL_FILE_NAME_KEY, ML_MODEL_FILE_NAME_VALUE, \
    SYS_DEPLOYMENT_FILE_NAME_KEY, SYS_DEPLOYMENT_FILE_NAME_VALUE


DEPLOYMENT_REQUIRED_FIELDS = ['input_type', 'output_type']
VERSION_FIELDS = ['language', 'memory_allocation', 'minimum_instances', 'maximum_instances',
                  'maximum_idle_time', 'description', 'labels']
VERSION_FIELD_TYPES = {'language': str, 'memory_allocation': int, 'minimum_instances': int, 'maximum_instances': int,
                       'maximum_idle_time': int, 'description': str, 'labels': dict}
VERSION_FIELDS_RENAMED = {'description': 'version_description', 'labels': 'version_labels'}
PIPELINE_REQUIRED_FIELDS = ['input_type']
OBJECT_REQUIRED_FIELDS = ['name', 'reference_name']
ATTACHMENT_REQUIRED_FIELDS = ['source_name', 'destination_name']


def set_version_defaults(fields, yaml_content, existing_version, extra_yaml_fields):
    """
    Define deployment version fields.
    For each field i in [DEPLOYMENT_VERSION_FIELDS + extra_yaml_fields]:
    - Use value in fields if specified
    - If not; Use value in yaml content if specified
    - If not; Use existing version (this is only used for updating, not creating)
    """

    for k, v in VERSION_FIELDS_RENAMED.items():
        fields[k] = fields[v]
        del fields[v]

    for k in [k for k, v in VERSION_FIELD_TYPES.items() if v == dict]:
        if k in fields and fields[k] is not None:
            fields[k] = strings_to_dict(fields[k])

    if yaml_content:
        for p in [*VERSION_FIELDS, *extra_yaml_fields]:
            input_field = VERSION_FIELDS_RENAMED[p] if p in VERSION_FIELDS_RENAMED else p
            value = fields[input_field] if input_field in fields else None
            fields[p] = set_dict_default(value, yaml_content, input_field,
                                         set_type=VERSION_FIELD_TYPES[p] if
                                         p in VERSION_FIELD_TYPES else str)

    if existing_version:
        for p in VERSION_FIELDS:
            fields[p] = set_object_default(fields[p], existing_version, p)
    return fields


def update_deployment_file(client, project, deployment, version, deployment_file):
    """
    If deployment_file is specified:
    - If an environment variable SYS_DEPLOYMENT_FILE_NAME_KEY exists and value is not equal:
        - If on deployment version level: update
        - If inherited: create one on deployment version level
    - If not; create one if it's not the default SYS_DEPLOYMENT_FILE_NAME_VALUE.
    """

    if deployment_file:
        deployment_file = str(deployment_file).strip()
        env_vars = client.version_environment_variables_list(
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
                if current_env_var[0].inheritance_type is None:
                    new_env_var = api.EnvironmentVariableCreate(
                        name=env_var_name, value=deployment_file, secret=current_env_var[0].secret
                    )
                    client.version_environment_variables_update(
                        project_name=project, deployment_name=deployment, version=version,
                        id=current_env_var[0]['id'], data=new_env_var
                    )
                else:
                    # inherited
                    client.version_environment_variables_create(
                        project_name=project, deployment_name=deployment, version=version, data=new_env_var
                    )
        elif (deployment_file != SYS_DEPLOYMENT_FILE_NAME_VALUE
              and deployment_file != "%s.py" % SYS_DEPLOYMENT_FILE_NAME_VALUE
              and deployment_file != ML_MODEL_FILE_NAME_VALUE
              and deployment_file != "%s.py" % ML_MODEL_FILE_NAME_VALUE):
            client.version_environment_variables_create(
                project_name=project, deployment_name=deployment, version=version, data=new_env_var
            )


def check_objects_requirements(yaml_content):
    """
    Check yaml structure for objects.
    """

    object_deployment_names = []
    if 'objects' in yaml_content and yaml_content['objects'] is not None:
        check_required_fields(input_dict=yaml_content, list_name='objects', required_fields=OBJECT_REQUIRED_FIELDS)
        for list_item in yaml_content['objects']:
            assert list_item['name'] not in object_deployment_names, \
                "Object names must be unique"
            assert 'reference_version' in list_item, "No 'reference_version' found for object." \
                                                     "\nFound: %s" % str(list_item)
            object_deployment_names.append(list_item['name'])
    return object_deployment_names


def check_attachments_requirements(yaml_content, object_deployment_names):
    """
    Check yaml structure for attachments.
    """

    if 'attachments' in yaml_content and yaml_content['attachments'] is not None:
        if len(yaml_content['attachments']) > 0:
            assert 'objects' in yaml_content, "Missing field name 'objects' in given file. " \
                                              "Objects are required for attachment creation."
        check_required_fields(input_dict=yaml_content, list_name='attachments',
                              required_fields=ATTACHMENT_REQUIRED_FIELDS)
        for list_item in yaml_content['attachments']:
            assert list_item['source_name'] in ['pipeline_start', *object_deployment_names], \
                "Attachment source_name must be 'pipeline_start' or a specified object name." \
                "\nFound: %s" % list_item['source_name']
            assert list_item['destination_name'] in object_deployment_names, \
                "Attachment destination_name must be a specified object name." \
                "\nFound: %s" % list_item['source_name']


def get_label_filter(input_labels):
    """
    Allow labels input to be formatted like:

    -l key1:value -l key2:value
    AND
    -l key1:value,key2:value

    Output: key1:value,key2:value
    """
    if input_labels is None:
        return []

    label_filter = []
    for label in input_labels:
        sub_labels = [sub_label.strip() for sub_label in label.split(",")]
        label_filter.extend(sub_labels)
    return ",".join(label_filter)


def strings_to_dict(input_labels):
    """
    Allow labels input to be formatted like:

    -l key1:value -l key2:value
    AND
    -l key1:value,key2:value

    Output: [{key1:value}, {key2:value}]
    """
    if input_labels is None:
        return {}

    label_dict = {}
    for label in input_labels:
        for sub_label in label.split(","):
            key_value = [kv.strip() for kv in sub_label.split(":")]
            assert len(key_value) == 2, "Expected format key:value, but found: %s" % str(sub_label)
            label_dict[key_value[0]] = key_value[1]
    return label_dict
