import ubiops as api

from pkg.utils import get_current_project, init_client, set_dict_default, read_yaml, write_yaml, parse_json
from pkg.src.helpers.pipeline_helpers import check_objects_requirements, check_attachments_requirements, \
    get_pipeline_and_version_fields_from_yaml, pipeline_version_exists, get_pipeline_if_exists, \
    check_pipeline_can_be_updated, patch_pipeline_version, define_pipeline, \
    create_objects_and_attachments, get_changed_pipeline_input_data
from pkg.src.helpers.helpers import get_label_filter
from pkg.src.helpers.formatting import print_list, print_item, format_yaml, format_pipeline_requests_reference, \
    format_pipeline_requests_oneline, format_json
from pkg.src.helpers.options import *
from pkg.constants import STRUCTURED_TYPE


LIST_ITEMS = ['last_updated', 'name', 'labels']
REQUEST_LIST_ITEMS = ['time_created', 'version', 'status', 'success']


@click.group(["pipelines", "ppl"], short_help="Manage your pipelines")
def commands():
    """
    Manage your pipelines.
    """

    pass


@commands.command("list", short_help="List pipelines")
@LABELS_FILTER
@LIST_FORMATS
def pipelines_list(labels, format_):
    """
    List pipelines in project.

    The <labels> option can be used to filter on specific labels.
    """

    label_filter = get_label_filter(labels)

    project_name = get_current_project(error=True)
    if project_name:
        client = init_client()
        pipelines = client.pipelines_list(project_name=project_name, labels=label_filter)
        print_list(pipelines, LIST_ITEMS, sorting_col=1, fmt=format_)
        client.api_client.close()


@commands.command("get", short_help="Get a pipeline")
@PIPELINE_NAME_ARGUMENT
@PIPELINE_YAML_OUTPUT
@QUIET
@GET_FORMATS
def pipelines_get(pipeline_name, output_path, quiet, format_):
    """
    Get the pipeline settings, like, input_type and input_fields.

    If you specify the <output_path> option, this location will be used to store the
    pipeline structure in a yaml file. You can either specify the <output_path> as file or
    directory. If the specified <output_path> is a directory, the settings will be
    stored in `pipeline.yaml`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    pipeline = client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)
    client.api_client.close()

    if output_path is not None:
        dictionary = format_yaml(
            pipeline,
            required_front=['name', 'description', 'input_type'],
            optional=['input_fields'],
            rename={
                'name': 'pipeline_name',
                'description': 'pipeline_description'
            },
            as_str=False
        )

        yaml_file = write_yaml(output_path, dictionary, default_file_name="pipeline.yaml")
        if not quiet:
            click.echo('Pipeline file is stored in: %s' % yaml_file)

    else:
        print_item(
            pipeline,
            row_attrs=LIST_ITEMS,
            required_front=['name', 'description', 'input_type'],
            optional=['input_fields', 'creation_date', 'last_updated', 'default_version'],
            rename={
                'name': 'pipeline_name',
                'description': 'pipeline_description'
            },
            fmt=format_
        )


@commands.command("create", short_help="Create a pipeline")
@PIPELINE_NAME_OVERRULE
@PIPELINE_YAML_FILE
@CREATE_FORMATS
def pipelines_create(pipeline_name, yaml_file, format_):
    """
    Create a new pipeline.

    \b
    Define the pipeline parameters using a yaml file.
    For example:
    ```
    pipeline_name: my-pipeline-name
    pipeline_description: Pipeline created via command line.
    pipeline_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    input_type: structured
    input_fields:
      - name: my-pipeline-param1
        data_type: int
    ```

    Possible input/output types: [structured, plain].
    Possible data_types: [blob, int, string, double, bool, array_string, array_int, array_double].
    """

    client = init_client()
    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=PIPELINE_REQUIRED_FIELDS)
    assert 'pipeline_name' in yaml_content or pipeline_name, \
        'Please, specify the pipeline name in either the yaml file or as a command argument'

    pipeline_fields, input_fields = define_pipeline(yaml_content, pipeline_name)
    pipeline_data = api.PipelineCreate(**pipeline_fields, **input_fields)
    pipeline_response = client.pipelines_create(project_name=project_name, data=pipeline_data)
    client.api_client.close()

    print_item(
        pipeline_response,
        row_attrs=LIST_ITEMS,
        rename={'name': 'pipeline_name', 'description': 'pipeline_description'},
        fmt=format_
    )


@commands.command("update", short_help="Update a pipeline")
@PIPELINE_NAME_ARGUMENT
@PIPELINE_NAME_UPDATE
@PIPELINE_YAML_FILE_UPDATE
@VERSION_DEFAULT_UPDATE
@QUIET
def pipelines_update(pipeline_name, new_name, yaml_file, default_version, quiet):
    """
    Update a pipeline.

    If you only want to update the name of the pipeline or the default pipeline version,
    use the options `<new_name>` and `<default_version>`.
    If you want to update the pipeline input type and fields, please use a yaml file to define the new pipeline.

    Please note that it's only possible to update the input of a pipeline for pipelines that have no pipeline versions
    with a connected pipeline start
    """

    client = init_client()
    project_name = get_current_project(error=True)

    # Check if pipeline exists
    existing_pipeline = client.pipelines_get(
        project_name=project_name, pipeline_name=pipeline_name
    )

    if yaml_file:
        # Update pipeline according to yaml (and default version update if given)
        yaml_content = read_yaml(yaml_file, required_fields=PIPELINE_REQUIRED_FIELDS)

        pipeline_fields, input_fields = define_pipeline(
            yaml_content, pipeline_name, current_pipeline_name=pipeline_name
        )
        changed_input_data = get_changed_pipeline_input_data(existing_pipeline, input_fields)

        pipeline = api.PipelineUpdate(
            **pipeline_fields, **changed_input_data, default_version=default_version
        )
        if pipeline.name != pipeline_name:
            # Pipeline will be renamed
            try:
                client.pipelines_get(project_name=project_name, pipeline_name=pipeline.name)
                raise Exception(
                    f"Trying to rename pipeline '{pipeline_name}' to '{pipeline.name}', but a pipeline with the new "
                    f"name already exists"
                )
            except api.exceptions.ApiException:
                pass

        client.pipelines_update(project_name=project_name, pipeline_name=pipeline_name, data=pipeline)

        if not quiet:
            click.echo("Pipeline was successfully updated")

    elif new_name and new_name != pipeline_name:
        # Pipeline will be renamed (and default version update if given)
        try:
            client.pipelines_get(project_name=project_name, pipeline_name=new_name)
            raise Exception(
                f"Trying to rename pipeline '{pipeline_name}' to '{new_name}', but a pipeline with the new "
                f"name already exists"
            )
        except api.exceptions.ApiException:
            pass

        pipeline = api.PipelineUpdate(name=new_name, default_version=default_version)
        client.pipelines_update(project_name=project_name, pipeline_name=pipeline_name, data=pipeline)

        if not quiet:
            click.echo("Pipeline was successfully updated")

    elif default_version is not None:
        # Pipeline default version will be changed
        pipeline = api.PipelineUpdate(default_version=default_version)
        client.pipelines_update(project_name=project_name, pipeline_name=pipeline_name, data=pipeline)

        if not quiet:
            click.echo("Pipeline default version was successfully updated")

    else:
        if not quiet:
            click.echo("Nothing to update")

    client.api_client.close()


@commands.command("delete", short_help="Delete a pipeline")
@PIPELINE_NAME_ARGUMENT
@ASSUME_YES
@QUIET
def pipelines_delete(pipeline_name, assume_yes, quiet):
    """
    Delete a pipeline.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete pipeline <{pipeline_name}> of project <{project_name}>?"
    ):
        client = init_client()
        client.pipelines_delete(project_name=project_name, pipeline_name=pipeline_name)
        client.api_client.close()

        if not quiet:
            click.echo("Pipeline was successfully deleted")


@commands.command("complete", short_help="Create a pipeline, version, and structure")
@PIPELINE_NAME_OVERRULE
@VERSION_NAME_OPTIONAL
@PIPELINE_YAML_FILE
@OVERWRITE
@QUIET
def pipelines_complete(pipeline_name, version_name, yaml_file, overwrite, quiet):
    """
    Create/Update a pipeline, version, and structure.

    Use the <overwrite> option to update an existing pipeline or version.
    Without <overwrite>, a new pipeline will be created if it doesn't exist, and a new pipeline version will be created.

    \b
    Define the pipeline parameters using a yaml file.
    For example:
    ```
    pipeline_name: my-pipeline-name
    pipeline_description: Pipeline created via command line.
    pipeline_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    input_type: structured
    input_fields:
      - name: my-pipeline-param1
        data_type: int
    version_name: my-version-name
    version_name: my-pipeline-version
    version_description: Version created via command line.
    version_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    objects:
      - name: object1
        reference_name: my-deployment-name
        reference_version: my-deployment-version
    attachments:
      - destination_name: object1
        sources:
          - source_name: pipeline_start
            mapping:
              - source_field_name: my-pipeline-param1
                destination_field_name: my-deployment-param1
    ```

    Possible input/output types: [structured, plain].
    Possible data_types: [blob, int, string, double, bool, array_string, array_int, array_double].

    All object references must exist. Connect the objects in the pipeline using attachments.
    Please, connect the start of the pipeline version to your first object. You can do this by creating an attachment
    with a source with 'source_name: pipeline_start' and the name of your first object as destination
    'destination_name: ...'.
    """

    client = init_client()
    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)

    assert 'pipeline_name' in yaml_content or pipeline_name, \
        'Please, specify the pipeline name in either the yaml file or as a command argument'

    assert 'version_name' in yaml_content or version_name, \
        'Please, specify the version name in either the yaml file or as a command option'

    # Get the pipeline and version names
    pipeline_name = set_dict_default(pipeline_name, yaml_content, 'pipeline_name')
    version_name = set_dict_default(version_name, yaml_content, 'version_name')
    pipeline_fields, input_fields, version_fields = get_pipeline_and_version_fields_from_yaml(yaml_content=yaml_content)

    # Check the objects and attachments
    object_deployment_names = check_objects_requirements(yaml_content)
    check_attachments_requirements(yaml_content, object_deployment_names)

    # Check if the given pipeline exists
    existing_pipeline = get_pipeline_if_exists(client, pipeline_name, project_name)

    if overwrite and existing_pipeline is not None:
        # Check if input of pipeline needs to be updated
        changed_input_data = get_changed_pipeline_input_data(existing_pipeline, input_fields)
        check_pipeline_can_be_updated(
            client=client,
            version_name=version_name,
            pipeline_name=pipeline_name,
            project_name=project_name,
            input_data=changed_input_data
        )

        # Check if given pipeline version exists
        if pipeline_version_exists(client, version_name, pipeline_name, project_name):
            patch_pipeline_version(
                client=client,
                yaml_content=yaml_content,
                version_name=version_name,
                pipeline_name=pipeline_name,
                project_name=project_name,
                pipeline_data=changed_input_data,
                version_data=version_fields,
                quiet=quiet
            )

            data = api.PipelineUpdate(**pipeline_fields)
            client.pipelines_update(project_name=project_name, pipeline_name=pipeline_name, data=data)

            client.api_client.close()
            if not quiet:
                click.echo("Pipeline was successfully updated")

            return

        # Update the pipeline
        data = api.PipelineUpdate(**changed_input_data, **pipeline_fields)
        client.pipelines_update(project_name=project_name, pipeline_name=pipeline_name, data=data)

    # Pipeline exists, but don't want to change it
    elif existing_pipeline is not None:
        # Check if input of pipeline is the same
        if get_changed_pipeline_input_data(existing_pipeline, input_fields):
            raise Exception(f"The input of existing pipeline '{pipeline_name}' does not match the input fields "
                            f"provided in the yaml. Please, use --overwrite option to update the pipeline input.")

    if existing_pipeline is None:
        # Create the pipeline
        pipeline_data = api.PipelineCreate(**pipeline_fields, **input_fields)
        client.pipelines_create(project_name=project_name, data=pipeline_data)

    # Create the pipeline version
    version_data = api.PipelineVersionCreate(version=version_name, **version_fields)
    client.pipeline_versions_create(
        project_name=project_name,
        pipeline_name=pipeline_name,
        data=version_data
    )

    create_objects_and_attachments(
        client=client,
        yaml_content=yaml_content,
        version_name=version_name,
        pipeline_name=pipeline_name,
        project_name=project_name
    )

    client.api_client.close()
    if not quiet:
        click.echo("Pipeline was successfully created")


@commands.command("request", short_help="Create a pipeline direct request")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@REQUEST_DATA
@REQUEST_PIPELINE_TIMEOUT
@REQUEST_OBJECT_TIMEOUT
@REQUESTS_FORMATS
def pipelines_request(pipeline_name, version_name, data, pipeline_timeout, deployment_timeout, format_):
    """
    Create a pipeline request and retrieve the result.

    Use the version option to make a request to a specific pipeline version:
    `ubiops pipelines request <my-deployment> -v <my-version> --data <input>`

    If not specified, a request is made to the default version:
    `ubiops pipelines request <my-deployment> --data <input>`

    For structured input, specify the data as JSON formatted string. For example:
    `ubiops pipelines request <my-deployment> --data "{\\"param1\\": 1, \\"param2\\": \\"two\\"}"`
    """

    project_name = get_current_project(error=True)

    client = init_client()
    pipeline = client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)

    if pipeline.input_type == STRUCTURED_TYPE:
        data = parse_json(data)

    if version_name is not None:
        response = client.pipeline_version_requests_create(
            project_name=project_name,
            pipeline_name=pipeline_name,
            version=version_name,
            data=data,
            pipeline_timeout=pipeline_timeout,
            deployment_timeout=deployment_timeout
        )

    else:
        response = client.pipeline_requests_create(
            project_name=project_name,
            pipeline_name=pipeline_name,
            data=data,
            pipeline_timeout=pipeline_timeout,
            deployment_timeout=deployment_timeout
        )

    client.api_client.close()
    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference([response]))

    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline([response]))

    elif format_ == 'json':
        click.echo(format_json(response))

    else:
        click.echo(format_pipeline_requests_reference([response]))


@commands.group("batch_requests", short_help="Manage your pipeline batch requests")
def batch_requests():
    """
    Manage your pipeline batch requests.
    """

    pass


@batch_requests.command("create", short_help="Create a pipeline batch request")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@REQUEST_DATA_MULTI
@REQUESTS_FORMATS
def batch_requests_create(pipeline_name, version_name, data, format_):
    """
    Create a pipeline batch request and retrieve request IDs to collect the results later.

    Use the version option to make a batch request to a specific pipeline version:
    `ubiops pipelines batch_requests create <my-pipeline> -v <my-version> --data <input>`

    If not specified, a batch request is made to the default version:
    `ubiops pipelines batch_requests create <my-pipeline> --data <input>`

    Multiple data inputs can be specified at ones by using the '--data' options multiple times:
    `ubiops pipelines batch_requests create <my-pipeline> --data <input-1> --data <input-2> --data <input-3>`

    For structured input, specify each data input as JSON formatted string. For example:
    `ubiops pipelines batch_requests create <my-pipeline> --data "{\\"param1\\": 1, \\"param2\\": \\"two\\"}"`
    """

    data = list(data)

    project_name = get_current_project(error=True)

    client = init_client()
    pipeline = client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)

    if pipeline.input_type == STRUCTURED_TYPE:
        input_data = []
        for d in data:
            input_data.append(parse_json(d))
    else:
        input_data = data

    if version_name is not None:
        response = client.batch_pipeline_version_requests_create(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name, data=input_data
        )

    else:
        response = client.batch_pipeline_requests_create(
            project_name=project_name, pipeline_name=pipeline_name, data=input_data
        )

    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_pipeline_requests_reference(response))


@batch_requests.command("get", short_help="Get a pipeline batch request")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@REQUEST_ID_MULTI
@REQUESTS_FORMATS
def batch_requests_get(pipeline_name, version_name, request_id, format_):
    """
    Get the results of one or more pipeline batch requests.

    Use the version option to get a batch request for a specific pipeline version.
    If not specified, the batch request is retrieved for the default version.

    Multiple request ids can be specified at ones by using the '-id' options multiple times:
    `ubiops pipelines batch_requests get <my-pipeline> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`
    """

    request_ids = list(request_id)

    project_name = get_current_project(error=True)

    client = init_client()
    if version_name is not None:
        response = client.batch_pipeline_version_requests_batch_get(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name, data=request_ids
        )

    else:
        response = client.batch_pipeline_requests_batch_get(
            project_name=project_name, pipeline_name=pipeline_name, data=request_ids
        )

    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference(response))

    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline(response))

    elif format_ == 'json':
        click.echo(format_json(response))

    else:
        click.echo(format_pipeline_requests_reference(response))


@batch_requests.command("list", short_help="List pipeline batch requests")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@OFFSET
@REQUEST_LIMIT
@LIST_FORMATS
def batch_requests_list(pipeline_name, version_name, offset, limit, format_):
    """
    List pipeline batch requests.

    Use the version option to list the batch requests for a specific pipeline version.
    If not specified, the batch requests are listed for the default version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    if version_name is not None:
        response = client.batch_pipeline_version_requests_list(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name, limit=limit, offset=offset
        )

    else:
        response = client.batch_pipeline_requests_list(
            project_name=project_name, pipeline_name=pipeline_name, limit=limit, offset=offset
        )

    client.api_client.close()
    print_list(response, REQUEST_LIST_ITEMS, fmt=format_)
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more)")
