import ubiops as api
from pkg.utils import set_dict_default, set_object_default, check_required_fields
from pkg.constants import ML_MODEL_FILE_NAME_KEY, ML_MODEL_FILE_NAME_VALUE


MODEL_REQUIRED_FIELDS = ['input_type', 'output_type']
MODEL_VERSION_FIELDS = ['language', 'memory_allocation', 'minimum_instances',
                        'maximum_instances', 'maximum_idle_time']
MODEL_VERSION_FIELD_TYPES = {'language': str, 'memory_allocation': int, 'minimum_instances': int,
                             'maximum_instances': int, 'maximum_idle_time': int}
PIPELINE_REQUIRED_FIELDS = ['input_type']
OBJECT_REQUIRED_FIELDS = ['name', 'reference_type', 'reference_name']
ATTACHMENT_REQUIRED_FIELDS = ['source_name', 'destination_name']


def set_version_defaults(fields, yaml_content, existing_version, extra_yaml_fields):
    """
    Define model version fields.
    For each field i in [MODEL_VERSION_FIELDS + extra_yaml_fields]:
    - Use value in fields if specified
    - If not; Use value in yaml content if specified
    - If not; Use existing version (this is only used for updating, not creating)
    """

    if yaml_content:
        for p in [*MODEL_VERSION_FIELDS, *extra_yaml_fields]:
            value = fields[p] if p in fields else None
            fields[p] = set_dict_default(value, yaml_content, p,
                                         set_type=MODEL_VERSION_FIELD_TYPES[p] if
                                         p in MODEL_VERSION_FIELD_TYPES else str)

    if existing_version:
        for p in MODEL_VERSION_FIELDS:
            fields[p] = set_object_default(fields[p], existing_version, p)
    return fields


def update_model_file(client, project, model, version, model_file):
    """
    If model_file is specified:
    - If an environment variable ML_MODEL_FILE_NAME_KEY exists and value is not equal:
        - If on model version level: update
        - If inherited: create one on model version level
    - If not; create one if it's not the default ML_MODEL_FILE_NAME_VALUE.
    """

    if model_file:
        if model_file.endswith('.py'):
            model_file = "".join(model_file.split('.py')[:-1])

        env_vars = client.model_version_environment_variables_list(project_name=project, model_name=model,
                                                                   version=version)

        current_env_var = [i for i in env_vars if i.name == ML_MODEL_FILE_NAME_KEY]
        new_env_var = api.EnvironmentVariableCreate(name=ML_MODEL_FILE_NAME_KEY, value=model_file, secret=False)
        if len(current_env_var) > 0:
            if current_env_var[0].value != str(model_file).strip():
                if current_env_var[0].inheritance_type is None:
                    new_env_var = api.EnvironmentVariableCreate(name=ML_MODEL_FILE_NAME_KEY, value=model_file,
                                                                secret=current_env_var[0].secret)
                    client.model_version_environment_variables_update(project_name=project, model_name=model,
                                                                      version=version, id=current_env_var[0]['id'],
                                                                      data=new_env_var)
                else:
                    # inherited
                    client.model_version_environment_variables_create(project_name=project, model_name=model,
                                                                      version=version, data=new_env_var)
        elif str(model_file).strip() != ML_MODEL_FILE_NAME_VALUE:
            client.model_version_environment_variables_create(project_name=project, model_name=model,
                                                              version=version, data=new_env_var)


def check_objects_requirements(yaml_content):
    """
    Check yaml structure for objects.
    """

    object_model_names = []
    object_connector_names = []
    if 'objects' in yaml_content and yaml_content['objects'] is not None:
        check_required_fields(input_dict=yaml_content, list_name='objects', required_fields=OBJECT_REQUIRED_FIELDS)
        for list_item in yaml_content['objects']:
            assert list_item['name'] not in [*object_model_names, *object_connector_names], \
                "Object names must be unique."
            if list_item['reference_type'] == 'model':
                assert 'reference_version' in list_item, "No 'reference_version' found for object with " \
                                                         "'reference_type'='model'.\nFound: %s" % str(list_item)
                object_model_names.append(list_item['name'])
            else:
                object_connector_names.append(list_item['name'])
    return object_model_names, object_connector_names


def check_attachments_requirements(yaml_content, object_model_names, object_connector_names):
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
            assert list_item['source_name'] in ['pipeline_start', *object_model_names], \
                "Attachment source_name must be 'pipeline_start' or a specified object name with reference_type " \
                "'model'.\nFound: %s" % list_item['source_name']
            assert list_item['destination_name'] in [*object_model_names, *object_connector_names], \
                "Attachment destination_name must be a specified object name." \
                "\nFound: %s" % list_item['source_name']
