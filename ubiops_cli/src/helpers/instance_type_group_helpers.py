INSTANCE_TYPE_GROUP_LIST_FIELDS = ["id", "name", "time_created", "time_updated"]
INSTANCE_TYPE_GROUP_REQUIRED_FIELDS = ["name", "instance_types"]

INSTANCE_TYPE_GROUP_RESPONSE_FILE = {
    "required_front": [
        "name",
        "instance_types id",
        "instance_types priority",
        "instance_types schedule_timeout",
    ],
}
INSTANCE_TYPE_GROUP_RESPONSE = {
    "required_front": [
        "id",
        "name",
        "time_created",
        "time_updated",
        "instance_types id",
        "instance_types name",
        "instance_types display_name",
        "instance_types cpu",
        "instance_types memory",
        "instance_types storage",
        "instance_types accelerator",
        "instance_types dedicated_node",
        "instance_types node_pool cluster type",
        "instance_types priority",
        "instance_types schedule_timeout",
    ],
    "optional": ["instance_types time_created"],
}
