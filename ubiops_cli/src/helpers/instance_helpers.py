INSTANCE_LIST_FIELDS_TABLE = ["id", "status", "time_created", "time_updated"]
INSTANCE_LIST_FIELDS_JSON = INSTANCE_LIST_FIELDS_TABLE + ["instance_type"]

PROJECT_INSTANCE_LIST_FIELDS_TABLE = INSTANCE_LIST_FIELDS_TABLE + ["deployment", "version"]
PROJECT_INSTANCE_LIST_FIELDS_JSON = PROJECT_INSTANCE_LIST_FIELDS_TABLE + ["instance_type"]

INSTANCE_EVENT_LIST_FIELDS = ["id", "time_created", "description"]

INSTANCE_RESPONSE = {
    "required_front": [
        "id",
        "status",
        "time_created",
        "time_updated",
        "node ipv4_address",
        "node ipv6_address",
    ],
    "optional": [
        "instance_type id",
        "instance_type name",
        "instance_type display_name",
        "node_pool cluster type",
    ],
}
