import click
import ubiops as api
from pkg.utils import set_dict_default, set_object_default, check_required_fields
from pkg.src.helpers.helpers import strings_to_dict

PIPELINE_REQUIRED_FIELDS = ['input_type']
PIPELINE_FIELDS = ['description', 'labels', 'input_fields', 'input_type']
PIPELINE_INPUT_FIELDS = ['input_fields', 'input_type']
PIPELINE_FIELDS_RENAMED = {'description': 'pipeline_description', 'labels': 'pipeline_labels'}

PIPELINE_VERSION_FIELDS = ['description', 'labels']
PIPELINE_VERSION_FIELD_TYPES = {
    'description': str,
    'labels': dict
}
PIPELINE_VERSION_FIELDS_RENAMED = {'description': 'version_description', 'labels': 'version_labels'}

OBJECT_REQUIRED_FIELDS = ['name', 'reference_name']
ATTACHMENT_REQUIRED_FIELDS = ['destination_name', 'sources']
ATTACHMENT_SOURCE_REQUIRED_FIELDS = ['source_name']
ATTACHMENT_MAPPING_REQUIRED_FIELDS = ['source_field_name', 'destination_field_name']


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
    :return dict, dict: the pipeline and pipeline input parameters
    """

    pipeline_name = set_dict_default(pipeline_name, yaml_content, 'pipeline_name')
    if pipeline_name is None and current_pipeline_name:
        pipeline_name = current_pipeline_name

    description = set_dict_default(None, yaml_content, 'pipeline_description')

    if 'input_fields' in yaml_content and isinstance(yaml_content['input_fields'], list):
        input_fields = [
            api.PipelineInputFieldCreate(name=item['name'], data_type=item['data_type'])
            for item in yaml_content['input_fields']
        ]

    else:
        input_fields = None

    if 'pipeline_labels' in yaml_content:
        labels = yaml_content['pipeline_labels']

    else:
        labels = {}

    pipeline_data = {
        'name': pipeline_name,
        'description': description,
        'labels': labels
    }
    input_data = {
        'input_type': yaml_content['input_type'],
        'input_fields': input_fields
    }
    return pipeline_data, input_data


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
        for p in PIPELINE_VERSION_FIELDS:
            # Rename 'version_{p}' to '{p}'
            input_field = PIPELINE_VERSION_FIELDS_RENAMED[p] if p in PIPELINE_VERSION_FIELDS_RENAMED else p
            value = fields[input_field] if input_field in fields else None
            fields[p] = set_dict_default(
                value, yaml_content, input_field,
                set_type=PIPELINE_VERSION_FIELD_TYPES[p] if p in PIPELINE_VERSION_FIELD_TYPES else str
            )

    if existing_version:
        for p in PIPELINE_VERSION_FIELDS:
            value = fields[p] if p in fields else None
            fields[p] = set_object_default(value, existing_version, p)

    return fields


def get_pipeline_and_version_fields_from_yaml(yaml_content):
    """
    Get pipeline and pipeline version fields from the given yaml file. Remove the pipeline_ and version_ prefix so that
    the fields can be used to create/update pipelines and versions.

    :param dict yaml_content: the content of the yaml
    :return dict, dict, dict: a dictionary containing pipeline, pipeline input and pipeline version parameters
    """

    pipeline_fields, input_fields = define_pipeline(yaml_content, pipeline_name=None)
    version_fields = dict()

    if yaml_content:
        for p in PIPELINE_VERSION_FIELDS:
            # Rename 'version_{p}' to '{p}'
            input_field = PIPELINE_VERSION_FIELDS_RENAMED[p] if p in PIPELINE_VERSION_FIELDS_RENAMED else p
            version_fields[p] = set_dict_default(
                None, yaml_content, input_field,
                set_type=PIPELINE_VERSION_FIELD_TYPES[p] if p in PIPELINE_VERSION_FIELD_TYPES else str
            )

    return pipeline_fields, input_fields, version_fields


def check_objects_requirements(yaml_content):
    """
    Check yaml structure for objects

    :param dict yaml_content: the content of the yaml
    :return list(str): a list of pipeline object names
    """

    object_names = []

    if 'objects' in yaml_content and yaml_content['objects'] is not None:
        check_required_fields(input_dict=yaml_content, list_name='objects', required_fields=OBJECT_REQUIRED_FIELDS)
        for list_item in yaml_content['objects']:
            assert list_item['name'] not in object_names, "Object names must be unique"

            object_names.append(list_item['name'])

    return object_names


def check_attachments_requirements(yaml_content, object_names):
    """
    Check yaml structure for attachments:
    - Required fields
    - Origin/Destination in object list

    :param dict yaml_content: the content of the yaml
    :param list(str) object_names: the list of pipeline object names
    """

    if 'attachments' in yaml_content and yaml_content['attachments'] is not None:
        if len(yaml_content['attachments']) > 0:
            assert 'objects' in yaml_content, \
                "Missing field name 'objects' in given file. Objects are required for attachment creation."

        check_required_fields(
            input_dict=yaml_content, list_name='attachments', required_fields=ATTACHMENT_REQUIRED_FIELDS
        )

        for list_item in yaml_content['attachments']:
            assert list_item['destination_name'] in object_names, \
                "Attachment destination_name must be a specified object name." \
                "\nFound: %s" % list_item['destination_name']

            check_required_fields(
                input_dict=list_item, list_name='sources',  required_fields=ATTACHMENT_SOURCE_REQUIRED_FIELDS
            )

            assert len(list_item['sources']) > 0, "Attachments must contain at least one source."

            for source in list_item['sources']:
                assert source['source_name'] in ['pipeline_start', *object_names], \
                    "Attachment source_name must be 'pipeline_start' or a specified object name." \
                    "\nFound: %s" % source['source_name']

                if 'mapping' in source and isinstance(source['mapping'], list):
                    check_required_fields(
                        input_dict=source, list_name='mapping', required_fields=ATTACHMENT_MAPPING_REQUIRED_FIELDS
                    )


def create_objects(client, objects, version_name, pipeline_name, project_name):
    """
    Create multiple objects in a pipeline

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param list(dict) objects: the validated content of the 'objects' entry in the yaml
    :param str version_name: the name of the pipeline version
    :param str pipeline_name: the name of the pipeline
    :param str project_name: the name of the project
    """

    for list_item in objects:
        if 'reference_version' in list_item:
            pipeline_object = api.PipelineVersionObjectCreate(
                name=list_item['name'],
                reference_name=list_item['reference_name'],
                version=list_item['reference_version']
            )

        # Create the object from the default version of the reference
        else:
            pipeline_object = api.PipelineVersionObjectCreate(
                name=list_item['name'],
                reference_name=list_item['reference_name']
            )

        client.pipeline_version_objects_create(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name, data=pipeline_object
        )


def update_objects(client, objects, version_name, pipeline_name, project_name):
    """
    Update objects:
    - Check for each current object if it's in the new pipeline
        - yes: update
               we don't need to check if anything changes, because the update method
               will not complain if nothing changes.
        - no: delete
    - Check if there are objects in the new pipeline which are not in the current
        - yes: create

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param list(dict) objects: the validated content of the 'objects' entry in the yaml
    :param str version_name: the name of the pipeline version
    :param str pipeline_name: the name of the pipeline
    :param str project_name: the name of the project
    :return:
        - list(str): the names of the created objects
        - list(str): the names of the updated objects (this will also included unchanged objects)
        - list(str): the names of the deleted objects
    """

    current_objects = client.pipeline_version_objects_list(
        project_name=project_name, pipeline_name=pipeline_name, version=version_name
    )

    updated = []
    deleted = []
    for item in current_objects:
        new_object = [o for o in objects if o['name'] == item.name]
        if len(new_object) == 1:
            # Update object
            ref_version = new_object[0]['reference_version'] if 'reference_version' in new_object[0] else None
            pipeline_object = api.PipelineVersionObjectCreate(
                name=new_object[0]['name'],
                reference_name=new_object[0]['reference_name'],
                version=ref_version
            )
            client.pipeline_version_objects_update(
                project_name=project_name, pipeline_name=pipeline_name, version=version_name, name=item.name,
                data=pipeline_object
            )
            updated.append(item.name)

        else:
            # Delete object
            client.pipeline_version_objects_delete(
                project_name=project_name, pipeline_name=pipeline_name, version=version_name, name=item.name
            )
            deleted.append(item.name)

    new_objects = [o for o in objects if o['name'] not in updated]
    create_objects(
        client=client, objects=new_objects, version_name=version_name,
        pipeline_name=pipeline_name, project_name=project_name
    )
    created = [o['name'] for o in new_objects]
    return created, updated, deleted


def create_attachments(client, attachments, version_name, pipeline_name, project_name):
    """
    Try to create all attachments. Raise a single error at the end if something went wrong.

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param list(dict) attachments: the validated content of the 'attachments' entry in the yaml
    :param str version_name: the name of the pipeline version
    :param str pipeline_name: the name of the pipeline
    :param str project_name: the name of the project
    """

    errors = []
    for list_item in attachments:
        sources = []
        for source in list_item['sources']:
            mapping = None
            if 'mapping' in source and isinstance(source['mapping'], list):
                mapping = [
                    api.AttachmentFieldsCreate(
                        source_field_name=field['source_field_name'],
                        destination_field_name=field['destination_field_name']
                    )
                    for field in source['mapping']
                ]

            sources.append(api.AttachmentSourcesCreate(source_name=source['source_name'], mapping=mapping))

        pipeline_object = api.AttachmentsCreate(destination_name=list_item['destination_name'], sources=sources)
        try:
            client.pipeline_version_object_attachments_create(
                project_name=project_name, pipeline_name=pipeline_name, version=version_name, data=pipeline_object
            )
        except api.exceptions.ApiException:
            errors.append({
                'sources': [i['source_name'] for i in list_item['sources']],
                'destination_name': list_item['destination_name']
            })

    if len(errors) > 0:
        raise Exception("Failed to create the following attachments:\n%s" % str(errors))


def delete_all_attachments(client, version_name, pipeline_name, project_name):
    """
    Delete all attachments of a pipeline version.
    By first deleting all attachments, we are able to change object references.

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param str version_name: the name of the pipeline version
    :param str pipeline_name: the name of the pipeline
    :param str project_name: the name of the project
    """

    attachments = client.pipeline_version_object_attachments_list(
        project_name=project_name, pipeline_name=pipeline_name, version=version_name
    )
    for attachment in attachments:
        client.pipeline_version_object_attachments_delete(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name, attachment_id=attachment.id
        )


def patch_pipeline_version(client, yaml_content, version_name, pipeline_name, project_name,
                           pipeline_data=None, version_data=None, quiet=False):
    """
    Update the content of a pipeline version
    - Delete all attachments
    - Update the pipeline objects
    - [Optional] Update the pipeline input
    - Create all attachments
    - [Optional] Update the pipeline version parameters

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param dict yaml_content: the content of the yaml
    :param str version_name: the name of the pipeline version
    :param str pipeline_name: the name of the pipeline
    :param str project_name: the name of the project
    :param dict/None pipeline_data: the content of the pipeline to update to
    :param dict/None version_data: the content of the pipeline version to update to
    :param bool quiet: whether to print the names of the changed objects or not
    """

    do_attachments_update = 'attachments' in yaml_content and yaml_content['attachments'] is not None
    do_objects_update = 'objects' in yaml_content and yaml_content['objects'] is not None

    if do_attachments_update or do_objects_update or pipeline_data:
        # Delete attachments
        delete_all_attachments(
            client=client, version_name=version_name, pipeline_name=pipeline_name, project_name=project_name
        )

        # Create/update objects
        if 'objects' in yaml_content:
            created, updated, deleted = update_objects(
                client=client,
                objects=yaml_content['objects'],
                pipeline_name=pipeline_name,
                project_name=project_name,
                version_name=version_name
            )

            if not quiet:
                click.echo('Created objects: %s' % created)
                click.echo('Updated/Unchanged objects: %s' % updated)
                click.echo('Deleted objects: %s' % deleted)

        # Update the pipeline
        if pipeline_data:
            pipeline_data = api.PipelineUpdate(**pipeline_data)
            client.pipelines_update(project_name=project_name, pipeline_name=pipeline_name, data=pipeline_data)

        # Create attachments
        if 'attachments' in yaml_content:
            create_attachments(
                client=client,
                attachments=yaml_content['attachments'],
                version_name=version_name,
                pipeline_name=pipeline_name,
                project_name=project_name
            )

    # Update the pipeline version
    if version_data:
        version_data = api.PipelineVersionUpdate(**version_data)
        client.pipeline_versions_update(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name,
            data=version_data
        )


def create_objects_and_attachments(client, yaml_content, version_name, pipeline_name, project_name):
    """
    Create pipeline objects and attachments

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param dict yaml_content: the content of the yaml
    :param str version_name: the name of the pipeline version
    :param str pipeline_name: the name of the pipeline
    :param str project_name: the name of the project
    """

    # Create objects if given
    if 'objects' in yaml_content and yaml_content['objects'] is not None:
        create_objects(
            client=client,
            objects=yaml_content['objects'],
            version_name=version_name,
            pipeline_name=pipeline_name,
            project_name=project_name
        )

    # Create attachments if given
    if 'attachments' in yaml_content and yaml_content['attachments'] is not None:
        create_attachments(
            client=client,
            attachments=yaml_content['attachments'],
            version_name=version_name,
            pipeline_name=pipeline_name,
            project_name=project_name
        )


def get_pipeline_if_exists(client, pipeline_name, project_name):
    """
    Get pipeline if it exists, otherwise return None

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param str pipeline_name: the name of the pipeline
    :param str project_name: the name of the project
    :return dict: pipeline object or None
    """

    try:
        return client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)
    except api.exceptions.ApiException:
        # Pipeline with the given name does not exist
        pass


def pipeline_version_exists(client, version_name, pipeline_name, project_name):
    """
    Check if pipeline exists

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param str version_name: the name of the pipeline version
    :param str pipeline_name: the name of the pipeline
    :param str project_name: the name of the project
    :return bool: whether the pipeline version exists or not
    """

    try:
        client.pipeline_versions_get(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name
        )
    except api.exceptions.ApiException:
        # Pipeline version with the given name does not exist
        return False
    return True


def check_pipeline_can_be_updated(client, version_name, pipeline_name, project_name, input_data):
    """
    Check if pipeline can be updated:
    - If desired input is changed; check if other versions exists (besides current version)

    :param ubiops.CoreApi client: the core API client to make requests to the API
    :param str version_name: the name of the pipeline version
    :param str pipeline_name: the name of the pipeline
    :param str project_name: the name of the project
    :param dict input_data: the pipeline input data to update to
    """

    if input_data:

        versions = client.pipeline_versions_list(project_name=project_name, pipeline_name=pipeline_name)
        if versions and len(versions) > 0 and (len(versions) > 1 or versions[0].version != version_name):
            raise Exception(
                "It is not possible to update the input fields/type of the pipeline because it contains "
                "multiple versions"
            )


def get_changed_pipeline_input_data(existing_pipeline, input_data):
    """
    Get pipeline input type and field if pipeline input changed

    :param ubiops.PipelineVersion existing_pipeline: the current pipeline version object
    :param dict input_data: the pipeline input data containing:
        str input_type: e.g. plain
        list(PipelineInputFieldCreate) input_fields: e.g. [PipelineInputFieldCreate(name=input1, data_type=int)]
    """
    changed_input_data = dict()

    # Input type changed
    if 'input_type' in input_data and existing_pipeline.input_type != input_data['input_type']:
        changed_input_data['input_type'] = input_data['input_type']
        changed_input_data['input_fields'] = input_data['input_fields']

    # Input fields changed
    elif 'input_fields' in input_data and isinstance(input_data['input_fields'], list):
        # Shuffle fields to {'field_name1': 'data_type1', 'field_name2': 'data_type2'}
        existing_fields = {field.name: field.data_type for field in existing_pipeline.input_fields}
        input_fields = {field.name: field.data_type for field in input_data['input_fields']}

        # Check if dicts are equal
        if existing_fields != input_fields:
            changed_input_data['input_fields'] = input_data['input_fields']

    return changed_input_data
