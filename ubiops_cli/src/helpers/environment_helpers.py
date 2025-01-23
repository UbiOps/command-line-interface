from ubiops_cli.utils import set_dict_default
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


def define_environment(fields, yaml_content, extra_yaml_fields=None):
    """
    Define environment fields

    For each field i in [ENVIRONMENT_INPUT_FIELDS + extra_yaml_fields]:
    - Use value in fields if specified
    - If not; Use value in yaml content if specified

    Rename field-key if the key is in ENVIRONMENT_FIELDS_RENAMED.values(). This is done to
    solve inconsistencies between CLI options/yaml keys and API parameters.

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :param list(str) extra_yaml_fields: additional yaml fields that are not Environment parameters, e.g., ignore_file
    :return dict: a dictionary containing all Environment parameters (+extra yaml fields)
    """

    extra_yaml_fields = [] if extra_yaml_fields is None else extra_yaml_fields

    for k, yaml_key in ENVIRONMENT_FIELDS_RENAMED.items():
        fields[k] = fields.pop(yaml_key, None)

    for k in [k for k, v in ENVIRONMENT_INPUT_FIELDS_TYPE.items() if v == dict]:
        if k in fields and fields[k] is not None:
            fields[k] = strings_to_dict(fields[k])

    if yaml_content:
        for k in [*ENVIRONMENT_INPUT_FIELDS, *extra_yaml_fields]:
            fields[k] = set_dict_default(
                value=fields.get(k, None),
                defaults_dict=yaml_content,
                default_key=ENVIRONMENT_FIELDS_RENAMED.get(k, k),
                set_type=ENVIRONMENT_INPUT_FIELDS_TYPE.get(k, str)
            )

    return fields


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
