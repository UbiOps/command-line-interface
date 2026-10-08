from .helpers import define_object


ENVIRONMENT_CREATE_FIELDS = [
    "name",
    "description",
    "labels",
]
ENVIRONMENT_UPDATE_FIELDS = ["name", "description", "labels"]
ENVIRONMENT_DETAILS = [
    "name",
    "project",
    "description",
    "labels",
    "creation_date",
    "last_updated",
]
ENVIRONMENT_FIELD_TYPES = {
    "name": str,
    "description": str,
    "labels": dict,
}
ENVIRONMENT_FIELDS_RENAMED = {
    "name": "environment_name",
    "description": "environment_description",
    "labels": "environment_labels",
}
TAG_CREATE_FIELDS = [
    "name",
    "supports_request_format",
]
TAG_UPDATE_FIELDS = ["supports_request_format", "status"]
TAG_DETAILS = [
    "name",
    "environment_name",
    "supports_request_format",
    "tag_type",
    "base_environment_name",
    "base_environment_tag",
    "status",
    "size",
    "creation_date",
    "last_updated",
]
TAG_FIELD_TYPES = {
    "name": str,
    "supports_request_format": bool,
}
TAG_FIELDS_RENAMED = {
    "name": "tag_name",
    "supports_request_format": "tag_supports_request_format",
}
TAG_LIST_FIELDS = ["creation_date", "id", "name", "status", "size", "supports_request_format"]


def define_environment(fields, yaml_content, extra_yaml_fields=None):
    """
    Define environment fields by combining the given fields and the content of a yaml file. The given fields are
    prioritized over the content of the yaml file; if they are not given the value in the yaml file is used (if
    present).

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :param list(str) extra_yaml_fields: additional yaml fields that are not Environment parameters, e.g., ignore_file
    :return dict: a dictionary containing all Environment parameters (+extra yaml fields)
    """

    extra_yaml_fields = [] if extra_yaml_fields is None else extra_yaml_fields

    return define_object(
        fields=fields,
        yaml_content=yaml_content,
        field_names=[*ENVIRONMENT_CREATE_FIELDS, *extra_yaml_fields],
        rename_field_names=ENVIRONMENT_FIELDS_RENAMED,
        field_types=ENVIRONMENT_FIELD_TYPES,
    )


def define_environment_tag(fields, yaml_content, extra_fields=None):
    """
    Define tag fields by combining the given fields and the content of a yaml file. The given fields are
    prioritized over the content of the yaml file; if they are not given the value in the yaml file is used (if
    present).

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :param list(str) extra_fields: additional fields that are not Tag creation parameters, e.g., ignore_file
    :return dict: a dictionary containing all Tag parameters (+extra fields)
    """

    extra_fields = [] if extra_fields is None else extra_fields

    return define_object(
        fields=fields,
        yaml_content=yaml_content,
        field_names=[*TAG_CREATE_FIELDS, *extra_fields],
        rename_field_names=TAG_FIELDS_RENAMED,
        field_types=TAG_FIELD_TYPES,
    )
