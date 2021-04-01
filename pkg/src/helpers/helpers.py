
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


def strings_to_dict(input_labels):
    """
    Allow labels input to be formatted like:

    -lb key1:value -lb key2:value
    AND
    -lb key1:value,key2:value

    Output: [{key1:value}, {key2:value}]

    :param list(str) input_labels: list of labels,
        like, ['key1:value1', 'key2:value2'] or ['key1:value1,key2:value2']
    :return list(dict): labels formatted, like,  [{key1:value1}, {key2:value2}]
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
