from .helpers import define_object


SERVICE_COMMON_FIELDS = [
    "name",
    "deployment",
    "version",
    "port",
    "description",
    "labels",
    "authentication_required",
    "authentication_method_token_enabled",
    "request_logging_excluded_paths",
    "request_logging_excluded_extensions",
    "concurrency_limit",
    "concurrency_limit_user_default",
    "rate_limit",
    "rate_limit_user_default",
]
SERVICE_CREATE_FIELDS = SERVICE_COMMON_FIELDS
SERVICE_UPDATE_FIELDS = SERVICE_CREATE_FIELDS
SERVICE_DETAILS = [
    *SERVICE_COMMON_FIELDS,
    "time_created",
    "time_updated",
    "endpoint",
]
SERVICE_FIELD_TYPES = {
    "name": str,
    "deployment": str,
    "version": str,
    "port": int,
    "description": str,
    "labels": dict,
    "authentication_required": bool,
    "authentication_method_token_enabled": bool,
    "request_logging_excluded_paths": str,
    "request_logging_excluded_extensions": list,
    "concurrency_limit": int,
    "concurrency_limit_user_default": int,
    "rate_limit": int,
    "rate_limit_user_default": int,
}
SERVICE_FIELDS_RENAMED = {
    "name": "service_name",
    "deployment": "service_deployment",
    "version": "service_version",
    "description": "service_description",
    "labels": "service_labels",
}


def define_service(fields, yaml_content):
    """
    Define service fields by combining the given fields and the content of a yaml file. The given fields are
    prioritized over the content of the yaml file; if they are not given the value in the yaml file is used (if
    present).

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :return dict: a dictionary containing all Service parameters
    """

    return define_object(
        fields=fields,
        yaml_content=yaml_content,
        field_names=SERVICE_CREATE_FIELDS,
        rename_field_names=SERVICE_FIELDS_RENAMED,
        field_types=SERVICE_FIELD_TYPES,
    )
