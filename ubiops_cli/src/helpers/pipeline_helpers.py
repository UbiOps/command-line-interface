import ubiops as api

from ubiops_cli.utils import set_dict_default, set_object_default
from ubiops_cli.src.helpers.helpers import strings_to_dict

PIPELINE_REQUIRED_FIELDS = ["input_type"]
PIPELINE_FIELDS = ["description", "labels", "input_type", "input_fields", "output_type", "output_fields"]
PIPELINE_FIELDS_RENAMED = {"description": "pipeline_description", "labels": "pipeline_labels"}

PIPELINE_VERSION_FIELDS = [
    "description",
    "labels",
    "request_retention_mode",
    "request_retention_time",
    "objects",
    "attachments",
]
PIPELINE_VERSION_FIELD_TYPES = {
    "description": str,
    "labels": dict,
    "request_retention_mode": str,
    "request_retention_time": int,
    "objects": None,
    "attachments": None,
}
PIPELINE_VERSION_FIELDS_RENAMED = {"description": "version_description", "labels": "version_labels"}

OBJECT_REQUIRED_FIELDS = ["name", "reference_name"]
ATTACHMENT_REQUIRED_FIELDS = ["destination_name", "sources"]
ATTACHMENT_SOURCE_REQUIRED_FIELDS = ["source_name"]
ATTACHMENT_MAPPING_REQUIRED_FIELDS = ["source_field_name", "destination_field_name"]

PIPELINE_VERSION_RESPONSE_FILE = {
    "required_front": [
        "pipeline",
        "input_type",
        "output_type",
        "version",
    ],
    "optional": [
        "description",
        "labels",
        "request_retention_mode",
        "request_retention_time",
        "objects name",
        "objects reference_type",
        "objects reference_name",
        "objects version",
        "objects configuration batch_size",
        "objects configuration error_message",
        "objects configuration expression",
        "objects configuration on_error",
        "objects configuration input_fields name",
        "objects configuration input_fields data_type",
        "objects configuration output_fields name",
        "objects configuration output_fields data_type",
        "objects configuration output_values name",
        "objects configuration output_values value",
        "attachments destination_name",
        "attachments sources source_name",
        "attachments sources mapping",
        "input_fields name",
        "input_fields data_type",
        "output_fields name",
        "output_fields data_type",
    ],
    "rename": {
        "pipeline": "pipeline_name",
        "version": "version_name",
        "objects version": "reference_version",
        **PIPELINE_VERSION_FIELDS_RENAMED,
    },
}
PIPELINE_VERSION_RESPONSE = {
    "required_front": PIPELINE_VERSION_RESPONSE_FILE["required_front"],
    "optional": ["creation_date", "last_updated", *PIPELINE_VERSION_RESPONSE_FILE["optional"]],
    "rename": {
        "creation_date": "version_creation_date",
        "last_updated": "version_last_updated",
        **PIPELINE_VERSION_RESPONSE_FILE["rename"],
    },
}


def define_pipeline(yaml_content, pipeline_name, current_pipeline_name=None):
    """
    Define pipeline by api.PipelineCreate class.
    - Pipeline name:
        - Use pipeline_name if specified
        - If not; Use pipeline_name in yaml content if specified
        - If not; Use current_pipeline_name (this is only used for updating, not creating)
    - Use yaml content for: description, input_type and input_fields

    :param dict yaml_content: the content of the yaml
    :param str/None pipeline_name: the name of the pipeline
    :param str/None current_pipeline_name: the name of the current pipeline if it already exists
    :return dict, dict, dict: the pipeline, and the pipeline input and output parameters
    """

    pipeline_name = set_dict_default(pipeline_name, yaml_content, "pipeline_name")
    if pipeline_name is None and current_pipeline_name:
        pipeline_name = current_pipeline_name

    description = set_dict_default(None, yaml_content, "pipeline_description")

    if "input_fields" in yaml_content and isinstance(yaml_content["input_fields"], list):
        input_fields = [
            api.PipelineInputFieldCreate(name=item["name"], data_type=item["data_type"])
            for item in yaml_content["input_fields"]
        ]

    else:
        input_fields = None

    if "output_fields" in yaml_content and isinstance(yaml_content["output_fields"], list):
        output_fields = [
            api.PipelineOutputFieldCreate(name=item["name"], data_type=item["data_type"])
            for item in yaml_content["output_fields"]
        ]

    else:
        output_fields = None

    if "pipeline_labels" in yaml_content:
        labels = yaml_content["pipeline_labels"]

    else:
        labels = {}

    pipeline_data = {"name": pipeline_name, "description": description, "labels": labels}
    input_data = {"input_type": yaml_content["input_type"], "input_fields": input_fields}
    output_data = {"output_type": yaml_content["output_type"], "output_fields": output_fields}
    return pipeline_data, input_data, output_data


def set_pipeline_version_defaults(fields, yaml_content, existing_version=None):
    """
    Define pipeline version fields.
    For each field i in PIPELINE_VERSION_FIELDS:
    - Use value in fields if specified
    - If not; Use value in yaml content if specified
    - If not; Use existing version (this is only used for updating, not creating)

    :param dict fields: the command options
    :param dict yaml_content: the content of the yaml
    :param ubiops.PipelineVersion existing_version: the current pipeline version if exists
    :return dict: a dictionary containing all PipelineVersion parameters
    """

    for k, v in PIPELINE_VERSION_FIELDS_RENAMED.items():
        fields[k] = fields[v]
        del fields[v]

    for k in [k for k, v in PIPELINE_VERSION_FIELD_TYPES.items() if v == dict]:
        if k in fields and fields[k] is not None:
            fields[k] = strings_to_dict(fields[k])

    if yaml_content:
        for k in PIPELINE_VERSION_FIELDS:
            # Rename 'version_{k}' to '{k}'
            input_field = PIPELINE_VERSION_FIELDS_RENAMED[k] if k in PIPELINE_VERSION_FIELDS_RENAMED else k
            value = fields[input_field] if input_field in fields else None
            fields[k] = set_dict_default(
                value,
                yaml_content,
                input_field,
                set_type=PIPELINE_VERSION_FIELD_TYPES[k] if k in PIPELINE_VERSION_FIELD_TYPES else str,
            )

    if existing_version:
        for k in PIPELINE_VERSION_FIELDS:
            value = fields[k] if k in fields else None

            # If objects or attachments are given as an empty list, they will be removed from the pipeline
            if k in ["objects", "attachments"] and value == []:
                continue

            fields[k] = set_object_default(value, existing_version, k)

    return fields


def get_pipeline_and_version_fields_from_yaml(yaml_content):
    """
    Get pipeline and pipeline version fields from the given yaml file. Remove the pipeline_ and version_ prefix so that
    the fields can be used to create/update pipelines and versions.

    :param dict yaml_content: the content of the yaml
    :return dict, dict, dict: a dictionary containing pipeline, pipeline input and pipeline version parameters
    """

    pipeline_fields, input_fields, output_fields = define_pipeline(yaml_content, pipeline_name=None)
    version_fields = {}

    if yaml_content:
        for k in PIPELINE_VERSION_FIELDS:
            # Rename 'version_{k}' to '{k}'
            input_field = PIPELINE_VERSION_FIELDS_RENAMED[k] if k in PIPELINE_VERSION_FIELDS_RENAMED else k
            version_fields[k] = set_dict_default(
                value=None,
                defaults_dict=yaml_content,
                default_key=input_field,
                set_type=PIPELINE_VERSION_FIELD_TYPES[k] if k in PIPELINE_VERSION_FIELD_TYPES else str,
            )

    return pipeline_fields, input_fields, output_fields, version_fields


def rename_pipeline_object_reference_version(content):
    """
    Rename 'reference_version' field to 'version' for each pipeline object in input data

    :param dict content: the pipeline version content
    return dict: updated pipeline version content
    """

    if "objects" in content and isinstance(content["objects"], list):
        objects = []
        for item in content["objects"]:
            if isinstance(item, dict):
                obj = {}
                if "name" in item:
                    obj["name"] = item["name"]
                if "reference_name" in item:
                    obj["reference_name"] = item["reference_name"]
                if "reference_version" in item:
                    obj["version"] = item["reference_version"]
                if "reference_type" in item:
                    obj["reference_type"] = item["reference_type"]
                if "configuration" in item:
                    obj["configuration"] = item["configuration"]
                objects.append(obj)
            else:
                objects.append(item)
        content["objects"] = objects

    return content


def get_changed_pipeline_structure(existing_pipeline, data, is_input=True):
    """
    Get pipeline input/output type and field if pipeline input/output changed

    :param ubiops.PipelineVersion existing_pipeline: the current pipeline version object
    :param dict data: the pipeline input or output data containing:
        str input_type/output_type: e.g. plain
        list(PipelineInputFieldCreate) input_fields/output_fields:
            e.g. [PipelineInputFieldCreate(name=input1, data_type=int)]
    :param bool is_input: whether to use input_ or output_ prefix
    """
    changed_data = {}

    type_key = "input_type" if is_input else "output_type"
    type_fields = "input_fields" if is_input else "output_fields"

    # Input/output type changed
    if type_key in data and getattr(existing_pipeline, type_key) != data[type_key]:
        changed_data[type_key] = data[type_key]
        changed_data[type_fields] = data[type_fields]

    # Input/output fields changed
    elif type_fields in data and isinstance(data[type_fields], list):
        # Shuffle fields to {'field_name1': 'data_type1', 'field_name2': 'data_type2'}
        existing_fields = {field.name: field.data_type for field in getattr(existing_pipeline, type_fields)}
        fields = {field.name: field.data_type for field in data[type_fields]}

        # Check if dicts are equal
        if existing_fields != fields:
            changed_data[type_fields] = data[type_fields]

    return changed_data
