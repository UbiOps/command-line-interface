import json
import ubiops as api

from pkg.utils import get_current_project, init_client, set_dict_default, read_yaml, write_yaml
from pkg.src.helpers.helpers import check_objects_requirements, check_attachments_requirements
from pkg.src.helpers.formatting import print_list, print_item, format_yaml, format_pipeline_requests_reference, \
    format_pipeline_requests_oneline, format_json
from pkg.src.helpers.options import *
from pkg.constants import STRUCTURED_TYPE


LIST_ITEMS = ['id', 'name', 'input_type', 'creation_date']
REQUEST_LIST_ITEMS = ['id', 'status', 'time_created', 'time_last_updated']


def define_pipeline(yaml_content, pipeline_name, current_pipeline_name=None):
    """
    Define pipeline by api.PipelineCreate class.
    - Pipeline name:
        - Use pipeline_name if specified
        - If not; Use pipeline_name in yaml content if specified
        - If not; Use current_pipeline_name (this is only used for updating, not creating)
    - Use yaml content for: description, input_type and input_fields
    """

    pipeline_name = set_dict_default(pipeline_name, yaml_content, 'pipeline_name')
    if pipeline_name is None and current_pipeline_name:
        pipeline_name = current_pipeline_name

    description = set_dict_default(None, yaml_content, 'pipeline_description')

    if 'input_fields' in yaml_content:
        input_fields = [api.PipelineInputFieldCreate(name=item['name'], data_type=item['data_type'])
                        for item in yaml_content['input_fields']]
    else:
        input_fields = None

    pipeline = api.PipelineCreate(name=pipeline_name, description=description,
                                  input_type=yaml_content['input_type'], input_fields=input_fields)
    return pipeline


def create_objects(objects, pipeline_name, project_name):
    """
    Create multiple objects in a pipeline.
    """

    client = init_client()
    for list_item in objects:
        pipeline_object = api.PipelineObjectCreate(name=list_item['name'],
                                                   reference_type=list_item['reference_type'],
                                                   reference_name=list_item['reference_name'],
                                                   version=list_item['reference_version'])
        client.pipeline_objects_create(project_name=project_name, pipeline_name=pipeline_name, data=pipeline_object)


def update_objects(objects, pipeline_name, project_name):
    """
    Update objects:
    - Check for each current object if it's in the new pipeline
        - yes: update
               we don't need to check if anything changes, because the update method
               will not complain if nothing changes.
        - no: delete
    - Check if there are objects in the new pipeline which are not in the current
        - yes: create

    returns:
    - created: list of object names
    - updated: list of object names (this will also included unchanged objects)
    - deleted: list of object names
    """

    client = init_client()
    current_objects = client.pipeline_objects_list(project_name=project_name, pipeline_name=pipeline_name)
    updated = []
    deleted = []
    for item in current_objects:
        new_object = [o for o in objects if o['name'] == item.name]
        if len(new_object) == 1:
            # update object
            ref_version = new_object[0]['reference_version'] if 'reference_version' in new_object[0] else None
            pipeline_object = api.PipelineObjectCreate(name=new_object[0]['name'],
                                                       reference_type=new_object[0]['reference_type'],
                                                       reference_name=new_object[0]['reference_name'],
                                                       version=ref_version)
            client.pipeline_objects_update(project_name=project_name, pipeline_name=pipeline_name,
                                           name=item.name, data=pipeline_object)
            updated.append(item.name)
        else:
            # delete object
            client.pipeline_objects_delete(project_name=project_name, pipeline_name=pipeline_name, name=item.name)
            deleted.append(item.name)

    new_objects = [o for o in objects if o['name'] not in updated]
    create_objects(new_objects, pipeline_name, project_name)
    created = [o['name'] for o in new_objects]
    return created, updated, deleted


def create_attachments(attachments, pipeline_name, project_name):
    """
    Try to create all attachments. Raise a single error at the end if something went wrong.
    """

    client = init_client()
    errors = []
    for list_item in attachments:
        if 'mapping' in list_item:
            mapping = [api.AttachmentFieldsCreate(source_field_name=field['source_field_name'],
                                                  destination_field_name=field['destination_field_name'])
                       for field in list_item['mapping']]
        else:
            mapping = None
        pipeline_object = api.AttachmentsCreate(source_name=list_item['source_name'],
                                                destination_name=list_item['destination_name'],
                                                mapping=mapping)
        try:
            client.pipeline_object_attachments_create(project_name=project_name, pipeline_name=pipeline_name,
                                                      data=pipeline_object)
        except api.exceptions.ApiException:
            errors.append({'source_name': list_item['source_name'],
                           'destination_name': list_item['destination_name']})
    if len(errors) > 0:
        raise Exception("Failed to create the following attachments:\n%s" % str(errors))


def delete_all_attachments(pipeline_name, project_name):
    """
    Delete all attachments of a pipeline.
    By first deleting all attachments, we are able to change object references.
    """

    client = init_client()
    attachments = client.pipeline_object_attachments_list(project_name=project_name, pipeline_name=pipeline_name)
    for attachment in attachments:
        client.pipeline_object_attachments_delete(project_name=project_name, pipeline_name=pipeline_name,
                                                  source_name=attachment.source_name,
                                                  destination_name=attachment.destination_name)


@click.group("pipelines")
def commands():
    """Manage your pipelines."""
    pass


@commands.command("list")
@LIST_FORMATS
def pipelines_list(format_):
    """List pipelines in project."""

    project_name = get_current_project(error=True)
    if project_name:
        client = init_client()
        pipelines = client.pipelines_list(project_name=project_name)
        print_list(pipelines, LIST_ITEMS, project_name=project_name, sorting_col=1, fmt=format_)


@commands.command("get")
@PIPELINE_NAME
@PIPELINE_YAML_OUTPUT
@QUIET
@GET_FORMATS
def pipelines_get(pipeline_name, output_path, quiet, format_):
    """Get the pipeline structure: input_type, objects and connections between the objects (attachments).

    If you specify the <output_path> option, this location will be used to store the
    pipeline structure in a yaml file. You can either specify the <output_path> as file or
    directory. If the specified <output_path> is a directory, the settings will be
    stored in `pipeline.yaml`."""

    project_name = get_current_project(error=True)

    client = init_client()
    pipeline = client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)
    objects = client.pipeline_objects_list(project_name=project_name, pipeline_name=pipeline_name)
    attachments = client.pipeline_object_attachments_list(project_name=project_name, pipeline_name=pipeline_name)

    setattr(pipeline, 'objects', objects)
    setattr(pipeline, 'attachments', attachments)

    if output_path is not None:
        dictionary = format_yaml(pipeline, required_front=['name', 'description', 'input_type'],
                                 optional=['input_fields', 'objects name', 'objects reference_type',
                                           'objects reference_name', 'objects version', 'attachments source_name',
                                           'attachments destination_name', 'attachments mapping'],
                                 rename={'name': 'pipeline_name', 'description': 'pipeline_description',
                                         'objects version': 'reference_version'}, as_str=False)
        yaml_file = write_yaml(output_path, dictionary, default_file_name="pipeline.yaml")
        if not quiet:
            click.echo('Pipeline file is stored in: %s' % yaml_file)
    else:
        print_item(pipeline, row_attrs=LIST_ITEMS, project_name=project_name,
                   rename={'name': 'pipeline_name', 'description': 'pipeline_description'}, fmt=format_)


@commands.command("create")
@PIPELINE_NAME_OVERRULE
@PIPELINE_YAML_FILE
@CREATE_FORMATS
def pipelines_create(pipeline_name, yaml_file, format_):
    """Create a new pipeline.

    \b
    Define the pipeline parameters using a yaml file.
    For example:
    ```
    pipeline_name: my-pipeline-name
    pipeline_description: Pipeline created via command line.
    input_type: structured
    input_fields:
      - name: my-pipeline-param1
        data_type: int
    objects:
      - name: object1
        reference_type: model
        reference_name: my-model-name
        reference_version: my-model-version
    attachments:
      - source_name: pipeline_start
        destination_name: object1
        mapping:
        - source_field_name: my-pipeline-param1
          destination_field_name: my-model-param1
    ```

    Possible input/output types: [structured, plain]. Possible data_types: [blob, int, string, double,
    bool, array_string, array_int, array_double].

    All object references must exist. Connect the objects in the pipeline using attachments.
    Please, connect the start of the pipeline to your first object. You can do this by creating an attachment with
    'source_name: pipeline_start' and the name of your first object as destination 'destination_name: ...'.
    """

    client = init_client()
    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=PIPELINE_REQUIRED_FIELDS)
    assert 'pipeline_name' in yaml_content or pipeline_name, 'Please, specify the pipeline name in either the yaml ' \
                                                             'file or as a command argument.'

    object_model_names, object_connector_names = check_objects_requirements(yaml_content)
    check_attachments_requirements(yaml_content, object_model_names, object_connector_names)

    pipeline = define_pipeline(yaml_content, pipeline_name)
    pipeline_response = client.pipelines_create(project_name=project_name, data=pipeline)

    if 'objects' in yaml_content and yaml_content['objects'] is not None:
        create_objects(yaml_content['objects'], pipeline.name, project_name)
    if 'attachments' in yaml_content and yaml_content['attachments'] is not None:
        create_attachments(yaml_content['attachments'], pipeline.name, project_name)

    print_item(pipeline_response, row_attrs=LIST_ITEMS, project_name=project_name,
               rename={'name': 'pipeline_name', 'description': 'pipeline_description'}, fmt=format_)


@commands.command("update")
@PIPELINE_NAME
@PIPELINE_NAME_UPDATE
@PIPELINE_YAML_FILE_UPDATE
@QUIET
def pipelines_update(pipeline_name, new_name, yaml_file, quiet):
    """Update a pipeline.

    If you only want to update the name of the pipeline, use the new_name option.
    If you want to update anything else (and the pipeline name), please use a yaml file to define the new pipeline.
    """

    client = init_client()
    project_name = get_current_project(error=True)

    # check if pipeline exists
    client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)

    if yaml_file:
        yaml_content = read_yaml(yaml_file, required_fields=PIPELINE_REQUIRED_FIELDS)
        object_model_names, object_connector_names = check_objects_requirements(yaml_content)
        check_attachments_requirements(yaml_content, object_model_names, object_connector_names)

        pipeline = define_pipeline(yaml_content, new_name, current_pipeline_name=pipeline_name)
        if pipeline.name != pipeline_name:
            # pipeline will be renamed
            try:
                client.pipelines_get(project_name=project_name, pipeline_name=pipeline.name)
                raise Exception("Trying to rename pipeline '%s' to '%s', but a pipeline with the new name "
                                "already exists." % (pipeline_name, pipeline.name))
            except api.exceptions.ApiException:
                pass

        delete_all_attachments(pipeline_name, project_name)

        if 'objects' in yaml_content:
            created, updated, deleted = update_objects(yaml_content['objects'], pipeline_name, project_name)
            if not quiet:
                click.echo('Created objects: %s' % created)
                click.echo('Updated/Unchanged objects: %s' % updated)
                click.echo('Deleted objects: %s' % deleted)

        client = init_client()
        client.pipelines_update(project_name=project_name, pipeline_name=pipeline_name, data=pipeline)

        create_attachments(yaml_content['attachments'], pipeline.name, project_name)

        if not quiet:
            click.echo("Pipeline was successfully updated.")

    elif new_name and new_name != pipeline_name:
        # pipeline will be renamed

        client = init_client()
        try:
            client.pipelines_get(project_name=project_name, pipeline_name=new_name)
            raise Exception("Trying to rename pipeline '%s' to '%s', but a pipeline with the new name "
                            "already exists." % (pipeline_name, new_name))
        except api.exceptions.ApiException:
            pass
        client.pipelines_update(project_name=project_name, pipeline_name=pipeline_name,
                                data={'name': new_name})
        if not quiet:
            click.echo("Pipeline was successfully renamed.")

    else:
        if not quiet:
            click.echo("Nothing to update.")


@commands.command("delete")
@PIPELINE_NAME
@ASSUME_YES
@QUIET
def pipelines_delete(pipeline_name, assume_yes, quiet):
    """Delete a pipeline."""

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm("Are you sure you want to delete pipeline <%s> "
                                   "of project <%s>?" % (pipeline_name, project_name)):
        client = init_client()
        client.pipelines_delete(project_name=project_name, pipeline_name=pipeline_name)

        if not quiet:
            click.echo("Pipeline was successfully deleted.")


@commands.command("request")
@PIPELINE_NAME
@REQUEST_DATA
@REQUESTS_FORMATS
def pipelines_request(pipeline_name, data, format_):
    """Create a pipeline request and retrieve the result.

    For structured input, specify the data as JSON formatted string. For example:
    `ubiops pipelines request <my-model> -v <my-version> -d "{\"param1\": 1, \"param2\": \"two\"}"`
    """

    project_name = get_current_project(error=True)

    client = init_client()
    pipeline = client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)

    if pipeline.input_type == STRUCTURED_TYPE:
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            raise Exception("Failed to parse data. JSON format expected.")

    response = client.pipelines_request(project_name=project_name, pipeline_name=pipeline_name, data=data)
    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference([response]))
    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline([response]))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_pipeline_requests_reference([response]))


@commands.group("batch_requests")
def batch_requests():
    """Manage your pipeline batch requests."""
    pass


@batch_requests.command("create")
@PIPELINE_NAME
@REQUEST_DATA_MULTI
@REQUESTS_FORMATS
def batch_requests_create(pipeline_name, data, format_):
    """Create a pipeline batch request and retrieve request IDs to collect the results later.

    Multiple data inputs can be specified at ones by using the '-d' options multiple times:
    `ubiops pipelines batch_requests create <my-pipeline> -d <input-1> -d <input-2> -d <input-3>`

    For structured input, specify each data input as JSON formatted string. For example:
    `ubiops pipelines batch_requests create <my-pipeline> -d "{\"param1\": 1, \"param2\": \"two\"}"`
    """

    data = list(data)

    project_name = get_current_project(error=True)

    client = init_client()
    pipeline = client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)

    if pipeline.input_type == STRUCTURED_TYPE:
        input_data = []
        for d in data:
            try:
                input_data.append(json.loads(d))
            except json.JSONDecodeError:
                raise Exception("Failed to parse data. JSON format expected. Input: %s" % d)
    else:
        input_data = data

    response = client.batch_pipeline_requests_create(
        project_name=project_name, pipeline_name=pipeline_name, data=input_data
    )

    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_pipeline_requests_reference(response))


@batch_requests.command("get")
@PIPELINE_NAME
@REQUEST_ID_MULTI
@REQUESTS_FORMATS
def batch_requests_get(pipeline_name, request_id, format_):
    """Get the results of one or more pipeline batch requests.

    Multiple request ids can be specified at ones by using the '-id' options multiple times:
    `xenia pipelines batch_requests get <my-pipeline> -id <id-1> -id <id-2> -id <id-3>`
    """

    request_ids = list(request_id)

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.batch_pipeline_requests_batch_collect(
        project_name=project_name, pipeline_name=pipeline_name, data=request_ids
    )
    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_pipeline_requests_reference(response))


@batch_requests.command("list")
@PIPELINE_NAME
@OFFSET
@REQUEST_LIMIT
@LIST_FORMATS
def batch_requests_list(pipeline_name, offset, limit, format_):
    """List pipeline batch requests."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.batch_pipeline_requests_list(project_name=project_name, pipeline_name=pipeline_name,
                                                   limit=limit, offset=offset)
    print_list(response, REQUEST_LIST_ITEMS, fmt=format_)
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more.)")
