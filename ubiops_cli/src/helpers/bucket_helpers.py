from ubiops_cli.src.helpers.helpers import strings_to_dict, json_to_dict

BUCKET_INPUT_FIELDS = ['name', 'description', 'labels', 'provider', 'credentials', 'configuration', 'ttl']
BUCKET_INPUT_FIELDS_TYPE = {
    'name': str, 'description': str, 'labels': dict, 'provider': str, 'credentials': 'json', 'configuration': 'json',
    'ttl': str
}
BUCKET_OUTPUT_FIELDS = [
    'name', 'project', 'description', 'labels', 'provider', 'configuration', 'ttl', 'creation_date',  'size',
    'size_measurement_date'
]
BUCKET_FIELDS_RENAMED = {'name': 'bucket_name', 'description': 'bucket_description', 'labels': 'bucket_labels'}


def define_bucket(fields, yaml_content, update=False):
    """
    Define bucket
    - Bucket name: use bucket_name if specified or else extract bucket_name from the yaml
    - Use yaml content for: description, configuration and credentials

    :param dict fields: the provided command line fields
    :param dict yaml_content: the content of the yaml
    :param bool update: if the definition is for create or update
    :return dict the bucket
    """

    bucket = {}

    # Iterate through expected input fields and retrieve them from the provider fields and / or yaml content
    for input_field in BUCKET_INPUT_FIELDS:
        input_field_name = BUCKET_FIELDS_RENAMED.get(input_field, input_field)

        # Options provided via the CLI have priority over options provided via YAML file
        if is_defined(fields, input_field_name):
            if BUCKET_INPUT_FIELDS_TYPE[input_field] == 'json':
                bucket[input_field] = json_to_dict(input_string=fields[input_field_name], file_fields=['json_key_file'])
            elif BUCKET_INPUT_FIELDS_TYPE[input_field] == dict:
                bucket[input_field] = strings_to_dict(fields[input_field_name])
            else:
                bucket[input_field] = fields[input_field_name]
        elif is_defined(yaml_content, input_field_name):
            bucket[input_field] = yaml_content[input_field_name]
        elif update:
            continue
        else:
            if BUCKET_INPUT_FIELDS_TYPE[input_field] == 'json' or BUCKET_INPUT_FIELDS_TYPE[input_field] == dict:
                bucket[input_field] = {}
            elif BUCKET_INPUT_FIELDS_TYPE == str:
                bucket[input_field] = ''
            else:
                bucket[input_field] = None

    return bucket


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
