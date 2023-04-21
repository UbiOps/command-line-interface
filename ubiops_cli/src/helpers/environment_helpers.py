from ubiops_cli.src.helpers.helpers import strings_to_dict


ENVIRONMENT_REQUIRED_FIELDS = ['name', 'base_environment']
ENVIRONMENT_INPUT_FIELDS = ['name', 'display_name', 'base_environment', 'description', 'labels']
ENVIRONMENT_FIELDS_UPDATE = ['name', 'display_name', 'description', 'labels']
ENVIRONMENT_INPUT_FIELDS_TYPE = {
    'name': str, 'display_name': str, 'base_environment': str, 'description': str, 'labels': dict
}
ENVIRONMENT_OUTPUT_FIELDS = [
    'name', 'display_name', 'project', 'base_environment', 'description', 'labels', 'creation_date', 'last_updated',
    'gpu_required'
]
ENVIRONMENT_FIELDS_RENAMED = {
    'name': 'environment_name', 'display_name': 'environment_display_name', 'description': 'environment_description',
    'labels': 'environment_labels'
}


def define_environment(fields, yaml_content, update=False):
    """
    Define an environment

    :param dict fields: the provided command line fields
    :param dict yaml_content: the content of the yaml
    :param bool update: if the definition is for create or update
    :return dict details of the environment
    """

    environment = {}

    # Iterate through expected input fields and retrieve them from the provided fields and / or yaml content
    for input_field in ENVIRONMENT_INPUT_FIELDS:
        input_field_name = input_field

        if input_field in ENVIRONMENT_FIELDS_RENAMED:
            input_field_name = ENVIRONMENT_FIELDS_RENAMED[input_field]

        # Options provided via the CLI have priority over options provided via YAML file
        if is_defined(fields, input_field_name):
            if ENVIRONMENT_INPUT_FIELDS_TYPE[input_field] == dict:
                environment[input_field] = strings_to_dict(fields[input_field_name])
            else:
                environment[input_field] = fields[input_field_name]

        elif is_defined(yaml_content, input_field_name):
            environment[input_field] = yaml_content[input_field_name]
        elif update:
            continue
        else:
            if ENVIRONMENT_INPUT_FIELDS_TYPE[input_field] == dict:
                environment[input_field] = {}
            elif ENVIRONMENT_INPUT_FIELDS_TYPE == str:
                environment[input_field] = ''
            else:
                environment[input_field] = None

    return environment


def is_defined(fields, field_name):
    """
    Decide if field_name is in fields and has a valid value

    :param dict fields: a dictionary of fields
    :param str field_name: a field
    """

    if field_name not in fields:
        return False

    if isinstance(fields[field_name], str):
        return fields[field_name] is not None
    if isinstance(fields[field_name], tuple):
        return bool(fields[field_name])
    if isinstance(fields[field_name], dict):
        return bool(fields[field_name])

    return False
