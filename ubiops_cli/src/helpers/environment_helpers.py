from ubiops_cli.src.helpers.helpers import define_object


ENVIRONMENT_CREATE_FIELDS = [
    "name",
    "display_name",
    "supports_request_format",
    "base_environment",
    "description",
    "labels",
]
ENVIRONMENT_UPDATE_FIELDS = ["name", "display_name", "description", "labels"]
ENVIRONMENT_DETAILS = [
    "name",
    "display_name",
    "project",
    "supports_request_format",
    "environment_type",
    "base_environment",
    "description",
    "labels",
    "creation_date",
    "last_updated",
    "gpu_required",
]
ENVIRONMENT_FIELD_TYPES = {
    "name": str,
    "display_name": str,
    "supports_request_format": bool,
    "base_environment": str,
    "description": str,
    "labels": dict,
}
ENVIRONMENT_FIELDS_RENAMED = {
    "name": "environment_name",
    "display_name": "environment_display_name",
    "description": "environment_description",
    "labels": "environment_labels",
    "supports_request_format": "environment_supports_request_format",
}


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
