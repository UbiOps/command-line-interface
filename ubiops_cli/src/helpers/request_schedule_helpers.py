from .helpers import define_object

SCHEDULE_CREATE_FIELDS = [
    "name",
    "object_type",
    "object_name",
    "version",
    "schedule",
    "request_data",
    "timeout",
    "enabled",
    "description",
    "labels",
]
SCHEDULE_UPDATE_FIELDS = [
    "name",
    "schedule",
    "request_data",
    "timeout",
    "enabled",
    "description",
    "labels",
]
SCHEDULE_DETAILS = [
    "id",
    "name",
    "object_type",
    "object_name",
    "version",
    "schedule",
    "request_data",
    "timeout",
    "enabled",
    "description",
    "labels",
    "creation_date",
]
SCHEDULE_FIELDS_RENAMED = {
    "name": "request_schedule_name",
    "version": "object_version",
    "description": "request_schedule_description",
    "labels": "request_schedule_labels",
}
SCHEDULE_FIELD_TYPES = {
    "name": str,
    "object_type": str,
    "object_name": str,
    "version": str,
    "schedule": str,
    "request_data": str,
    "timeout": int,
    "enabled": bool,
    "description": str,
    "labels": dict,
}


def define_request_schedule(fields, yaml_content):
    """
    Define request schedule fields by combining the given fields and the content of a yaml file. The given fields are
    prioritized over the content of the yaml file; if they are not given the value in the yaml file is used (if
    present).

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :return dict: a dictionary containing all request schedule parameters
    """

    return define_object(
        fields=fields,
        yaml_content=yaml_content,
        field_names=SCHEDULE_CREATE_FIELDS,
        rename_field_names=SCHEDULE_FIELDS_RENAMED,
        field_types=SCHEDULE_FIELD_TYPES,
    )
