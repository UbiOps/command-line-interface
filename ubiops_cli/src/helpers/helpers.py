import json


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
            assert len(key_value) == 2, "Expected format key:value, but found: %s" % str(key_value_pair)
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
        raise Exception("Failed to parse json parameter %s: %s" % (input_string, e))

    if file_fields:
        for file_field in file_fields:
            if file_field in return_dict:
                try:
                    with open(return_dict[file_field]) as f:
                        return_dict[file_field] = f.read()
                except FileNotFoundError as e:
                    raise Exception("Failed to read file for '%s': %s" % (file_field, e))
    return return_dict
