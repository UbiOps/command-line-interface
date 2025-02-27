import json

from ubiops_cli.utils import set_dict_default


def define_object(fields, yaml_content, field_names, rename_field_names, field_types):
    """
    Define an object by combining the given fields and the content of a yaml file for the given field names. The given
    fields are prioritized over the content of the yaml file; if they are not given the value in the yaml file is used
    (if present).

    Fields can be renamed using rename_field_names. This is done to solve inconsistencies between CLI options/yaml keys
    and API parameters.

    Use field_types to ensure the fields have the correct type.

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :param list(str) field_names: the field names to read from the command options and yaml file
    :param dict rename_field_names: for each field name, the CLI option/yaml key name
    :param dict field_types: for each field name, the correct type
    :return dict: a dictionary containing all object parameters
    """

    for k, yaml_key in rename_field_names.items():
        fields[k] = fields.pop(yaml_key, None)

    for k in [k for k, v in field_types.items() if v == dict]:
        if k in fields and fields[k] is not None:
            fields[k] = strings_to_dict(fields[k])

    if yaml_content:
        for k in field_names:
            fields[k] = set_dict_default(
                value=fields.get(k, None),
                defaults_dict=yaml_content,
                default_key=rename_field_names.get(k, k),
                set_type=field_types.get(k, str),
            )

    return fields


def get_label_filter(input_labels):
    """
    Allow labels input to be formatted like:

    -lb key1:value -lb key2:value
    AND
    -lb key1:value,key2:value

    Output: key1:value,key2:value

    :param list(str) input_labels: list of labels,
        like, ['key1:value1', 'key2:value2'] or ['key1:value1,key2:value2']
    :return str: labels formatted, like,  'key1:value1,key2:value2'
    """

    if input_labels is None:
        return []

    label_filter = []
    for label in input_labels:
        sub_labels = [sub_label.strip() for sub_label in label.split(",")]
        label_filter.extend(sub_labels)
    return ",".join(label_filter)


def strings_to_dict(input_dict):
    """
    Allow dictionaries input to be formatted like:

    key1:value
    AND
    key1:value,key2:value

    Output: [{key1:value}, {key2:value}]

    :param list(str) input_dict: list of dicts,
        like, ['key1:value1', 'key2:value2'] or ['key1:value1,key2:value2']
    :return list(dict): dict formatted, like,  [{key1:value1}, {key2:value2}]
    """

    if not input_dict:
        return None

    return_dict = {}
    for key in input_dict:
        # Make it possible to remove dict items by passing an empty string
        if key == "":
            continue

        for key_value_pair in key.split(","):
            key_value = [kv.strip() for kv in key_value_pair.split(":")]
            assert len(key_value) == 2, f"Expected format key:value, but found: {key_value_pair}"
            return_dict[key_value[0]] = key_value[1]
    return return_dict


def json_to_dict(input_string, file_fields):
    """
    Allow strings input to be formatted as json:

    :param str input_string: json formatted string
    :param list[str] file_fields: fields that require reading a file from disk
    :return dict|list parsed json
    """

    try:
        return_dict = json.loads(input_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse json parameter {input_string}: {e}")

    if file_fields:
        for file_field in file_fields:
            if file_field in return_dict:
                try:
                    with open(return_dict[file_field], encoding="utf-8") as f:
                        return_dict[file_field] = f.read()
                except FileNotFoundError as e:
                    raise FileNotFoundError(f"Failed to read file for '{file_field}': {e}")
    return return_dict
