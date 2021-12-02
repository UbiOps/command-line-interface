import ubiops as api

from ubiops_cli.utils import get_current_project, init_client, set_dict_default, read_yaml, write_yaml, parse_json
from ubiops_cli.src.helpers.pipeline_helpers import check_objects_requirements, check_attachments_requirements, \
    get_pipeline_and_version_fields_from_yaml, pipeline_version_exists, get_pipeline_if_exists, \
    check_pipeline_can_be_updated, patch_pipeline_version, define_pipeline, \
    create_objects_and_attachments, get_changed_pipeline_structure
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml, format_pipeline_requests_reference, \
    format_pipeline_requests_oneline, format_json, format_datetime, parse_datetime
from ubiops_cli.src.helpers.options import *
from ubiops_cli.constants import STRUCTURED_TYPE


LIST_ITEMS = ['last_updated', 'name', 'labels']
REQUEST_LIST_ITEMS = ['id', 'status', 'success', 'time_created']


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
            optional=['input_fields', 'output_type', 'output_fields'],
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
            optional=['input_fields', 'output_type', 'output_fields',
                      'creation_date', 'last_updated', 'default_version'],
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
    output_type: structured
    output_fields:
      - name: my-pipeline-output1
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

    pipeline_fields, input_fields, output_fields = define_pipeline(yaml_content, pipeline_name)
    pipeline_data = api.PipelineCreate(**pipeline_fields, **input_fields, **output_fields)
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
    If you want to update the pipeline input/output type and fields, please use a yaml file to define the new pipeline.

    Please note that it's only possible to update the input of a pipeline for pipelines that have no pipeline versions
    with a connected pipeline start, that it's only possible to update the output of a pipeline for pipelines that have
    no pipeline versions with a connected pipeline end.
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

        pipeline_fields, input_fields, output_fields = define_pipeline(
            yaml_content, pipeline_name, current_pipeline_name=pipeline_name
        )
        changed_input_data = get_changed_pipeline_structure(existing_pipeline, input_fields)
        changed_output_data = get_changed_pipeline_structure(existing_pipeline, output_fields, is_input=False)

        pipeline = api.PipelineUpdate(
            **pipeline_fields, **changed_input_data, **changed_output_data, default_version=default_version
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
    output_type: structured
    output_fields:
      - name: my-pipeline-output1
        data_type: int
    version_name: my-version-name
    version_name: my-pipeline-version
    version_description: Version created via command line.
    version_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    request_retention_mode: none
    request_retention_time: 604800
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
    Connect the object output fields to destination_name 'pipeline_end', to retrieve the output as pipeline
    request result.
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
    pipeline_fields, input_fields, output_fields, version_fields = get_pipeline_and_version_fields_from_yaml(
        yaml_content=yaml_content
    )

    # Check the objects and attachments
    object_deployment_names = check_objects_requirements(yaml_content)
    check_attachments_requirements(yaml_content, object_deployment_names)

    # Check if the given pipeline exists
    existing_pipeline = get_pipeline_if_exists(client, pipeline_name, project_name)

    if overwrite and existing_pipeline is not None:
        # Check if input of pipeline needs to be updated
        changed_input_data = get_changed_pipeline_structure(existing_pipeline, input_fields)
        check_pipeline_can_be_updated(
            client=client,
            version_name=version_name,
            pipeline_name=pipeline_name,
            project_name=project_name,
            data=changed_input_data
        )

        # Check if output of pipeline needs to be updated
        changed_output_data = get_changed_pipeline_structure(existing_pipeline, output_fields, is_input=False)
        check_pipeline_can_be_updated(
            client=client,
            version_name=version_name,
            pipeline_name=pipeline_name,
            project_name=project_name,
            data=changed_output_data
        )

        # Check if given pipeline version exists
        if pipeline_version_exists(client, version_name, pipeline_name, project_name):
            patch_pipeline_version(
                client=client,
                yaml_content=yaml_content,
                version_name=version_name,
                pipeline_name=pipeline_name,
                project_name=project_name,
                pipeline_input_data=changed_input_data,
                pipeline_output_data=changed_output_data,
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
        data = api.PipelineUpdate(**pipeline_fields, **changed_input_data, **changed_output_data)
        client.pipelines_update(project_name=project_name, pipeline_name=pipeline_name, data=data)

    # Pipeline exists, but don't want to change it
    elif existing_pipeline is not None:
        # Check if input of pipeline is the same
        if get_changed_pipeline_structure(existing_pipeline, input_fields):
            raise Exception(f"The input of existing pipeline '{pipeline_name}' does not match the input fields "
                            f"provided in the yaml. Please, use --overwrite option to update the pipeline input.")
        # Check if output of pipeline is the same
        if get_changed_pipeline_structure(existing_pipeline, output_fields):
            raise Exception(f"The output of existing pipeline '{pipeline_name}' does not match the output fields "
                            f"provided in the yaml. Please, use --overwrite option to update the pipeline output.")

    if existing_pipeline is None:
        # Create the pipeline
        pipeline_data = api.PipelineCreate(**pipeline_fields, **input_fields, **output_fields)
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


@commands.group("requests", short_help="Manage your pipeline requests")
def requests():
    """
    Manage your pipeline requests.
    """
    pass


@requests.command("create", short_help="Create pipeline request")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@REQUEST_BATCH
@REQUEST_TIMEOUT
@REQUEST_OBJECT_TIMEOUT
@REQUEST_DATA_MULTI
@REQUESTS_FORMATS
def requests_create(pipeline_name, version_name, batch, timeout, deployment_timeout, data, format_):
    """
    Create a pipeline request. Use `--batch` to create a batch (asynchronous) request.
    It's only possible to create a direct (synchronous) request to pipelines without 'batch' mode deployments. In
    contrast, batch (asynchronous) requests can be made to any pipeline, independent on the deployment modes.

    Pipeline requests are only stored for pipeline versions with `request_retention_mode` 'full' or 'metadata'.

    Use the option `timeout` to specify the timeout of the pipeline request. The minimum value is 10 seconds.
    The maximum value is 7200 (2 hours) for direct requests and 345600 (96 hours) for batch requests. The default value
    is 3600 (1 hour) for direct requests and 14400 (4 hours) for batch requests.

    Use the version option to make a request to a specific pipeline version:
    `ubiops pipelines requests create <my-pipeline> -v <my-version> --data <input>`

    If not specified, a request is made to the default version:
    `ubiops pipelines requests create <my-pipeline> --data <input>`

    Use `--batch` to make an asynchronous batch request:
    `ubiops pipelines requests create <my-pipeline> --batch --data <input>`

    Multiple data inputs can be specified at ones and send as batch by using the '--data' options multiple times:
    `ubiops pipelines requests create <my-pipeline> --batch --data <input-1> --data <input-2> --data <input-3>`

    For structured input, specify each data input as JSON formatted string. For example:
    `ubiops pipelines requests create <my-pipeline> --data "{\\"param1\\": 1, \\"param2\\": \\"two\\"}"`
    """

    data = list(data)

    project_name = get_current_project(error=True)

    client = init_client()
    pipeline = client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)

    if batch and deployment_timeout is not None:
        raise Exception("It's not possible to pass a deployment timeout for a batch pipeline request")

    if pipeline.input_type == STRUCTURED_TYPE:
        input_data = []
        for d in data:
            input_data.append(parse_json(d))
    else:
        input_data = data

    if version_name is not None:
        if batch:
            response = client.batch_pipeline_version_requests_create(
                project_name=project_name, pipeline_name=pipeline_name, version=version_name, data=input_data,
                timeout=timeout
            )
        else:
            response = [client.pipeline_version_requests_create(
                project_name=project_name, pipeline_name=pipeline_name, version=version_name, data=input_data,
                pipeline_timeout=timeout, deployment_timeout=deployment_timeout
            )]
    else:
        if batch:
            response = client.batch_pipeline_requests_create(
                project_name=project_name, pipeline_name=pipeline_name, data=input_data, timeout=timeout
            )
        else:
            response = [client.pipeline_requests_create(
                project_name=project_name, pipeline_name=pipeline_name, data=input_data,
                pipeline_timeout=timeout, deployment_timeout=deployment_timeout
            )]

    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_pipeline_requests_reference(response))


@requests.command("get", short_help="Get a pipeline request")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@REQUEST_ID_MULTI
@REQUESTS_FORMATS
def requests_get(pipeline_name, version_name, request_id, format_):
    """
    Get one or more pipeline requests.
    Pipeline requests are only stored for pipeline versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to get a request for a specific pipeline version.
    If not specified, the request is retrieved for the default version.

    Multiple request ids can be specified at ones by using the '-id' options multiple times:
    `ubiops pipelines requests get <my-pipeline> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`
    """

    request_ids = list(request_id)

    project_name = get_current_project(error=True)

    client = init_client()
    if version_name is not None:
        response = client.pipeline_version_requests_batch_get(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name, data=request_ids
        )

    else:
        response = client.pipeline_requests_batch_get(
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


@requests.command("list", short_help="List pipeline requests")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@OFFSET
@REQUEST_LIMIT
@REQUEST_SORT
@REQUEST_FILTER_PIPELINE_STATUS
@REQUEST_FILTER_SUCCESS
@REQUEST_FILTER_START_DATE
@REQUEST_FILTER_END_DATE
@REQUEST_FILTER_SEARCH_ID
@LIST_FORMATS
def requests_list(pipeline_name, version_name, limit, format_, **kwargs):
    """
    List pipeline requests.
    Pipeline requests are only stored for pipeline versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to list the requests for a specific pipeline version.
    If not specified, the requests are listed for the default version.
    """

    project_name = get_current_project(error=True)

    if 'start_date' in kwargs and kwargs['start_date']:
        try:
            kwargs['start_date'] = format_datetime(parse_datetime(kwargs['start_date']), fmt='%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            raise Exception("Failed to parse start_date. Please use iso-format, "
                            "for example, '2020-01-01T00:00:00.000000Z'")

    if 'end_date' in kwargs and kwargs['end_date']:
        try:
            kwargs['end_date'] = format_datetime(parse_datetime(kwargs['end_date']), fmt='%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            raise Exception("Failed to parse end_date. Please use iso-format, "
                            "for example, '2020-01-01T00:00:00.000000Z'")

    client = init_client()
    if version_name is not None:
        response = client.pipeline_version_requests_list(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name, limit=limit, **kwargs
        )

    else:
        response = client.pipeline_requests_list(
            project_name=project_name, pipeline_name=pipeline_name, limit=limit, **kwargs
        )

    client.api_client.close()
    print_list(response, REQUEST_LIST_ITEMS, fmt=format_)
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more)")


@commands.command("request", short_help="[DEPRECATED] Create a pipeline direct request")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@REQUEST_DATA
@REQUEST_PIPELINE_TIMEOUT_DEPRECATED
@REQUEST_OBJECT_TIMEOUT
@REQUESTS_FORMATS
def deprecated_pipelines_request(pipeline_name, version_name, data, pipeline_timeout, deployment_timeout, format_):
    """
    [DEPRECATED] Create a pipeline request and retrieve the result.

    Use the version option to make a request to a specific pipeline version:
    `ubiops pipelines request <my-deployment> -v <my-version> --data <input>`

    If not specified, a request is made to the default version:
    `ubiops pipelines request <my-deployment> --data <input>`

    For structured input, specify the data as JSON formatted string. For example:
    `ubiops pipelines request <my-deployment> --data "{\\"param1\\": 1, \\"param2\\": \\"two\\"}"`
    """

    if format_ != 'json':
        click.secho(
            "Deprecation warning: 'request' is deprecated, use 'requests create' instead",
            fg='red'
        )

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


@commands.group("batch_requests", short_help="[DEPRECATED] Manage your pipeline batch requests")
def deprecated_batch_requests():
    """
    [DEPRECATED] Manage your pipeline batch requests.
    """

    pass


@deprecated_batch_requests.command("create", short_help="[DEPRECATED] Create a pipeline batch request")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@REQUEST_DATA_MULTI
@REQUESTS_FORMATS
def deprecated_batch_requests_create(pipeline_name, version_name, data, format_):
    """
    [DEPRECATED] Create a pipeline batch request and retrieve request IDs to collect the results later.
    Pipeline requests are only stored for pipeline versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to make a batch request to a specific pipeline version:
    `ubiops pipelines batch_requests create <my-pipeline> -v <my-version> --data <input>`

    If not specified, a batch request is made to the default version:
    `ubiops pipelines batch_requests create <my-pipeline> --data <input>`

    Multiple data inputs can be specified at ones by using the '--data' options multiple times:
    `ubiops pipelines batch_requests create <my-pipeline> --data <input-1> --data <input-2> --data <input-3>`

    For structured input, specify each data input as JSON formatted string. For example:
    `ubiops pipelines batch_requests create <my-pipeline> --data "{\\"param1\\": 1, \\"param2\\": \\"two\\"}"`
    """

    if format_ != 'json':
        click.secho(
            "Deprecation warning: 'batch_requests create' is deprecated, use 'requests create --batch' instead",
            fg='red'
        )

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


@deprecated_batch_requests.command("get", short_help="[DEPRECATED] Get a pipeline batch request")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@REQUEST_ID_MULTI
@REQUESTS_FORMATS
def deprecated_batch_requests_get(pipeline_name, version_name, request_id, format_):
    """
    [DEPRECATED] Get the results of one or more pipeline batch requests.
    Pipeline requests are only stored for pipeline versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to get a batch request for a specific pipeline version.
    If not specified, the batch request is retrieved for the default version.

    Multiple request ids can be specified at ones by using the '-id' options multiple times:
    `ubiops pipelines batch_requests get <my-pipeline> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`
    """

    if format_ != 'json':
        click.secho(
            "Deprecation warning: 'batch_requests get' is deprecated, use 'requests get' instead",
            fg='red'
        )

    request_ids = list(request_id)

    project_name = get_current_project(error=True)

    client = init_client()
    if version_name is not None:
        response = client.pipeline_version_requests_batch_get(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name, data=request_ids
        )

    else:
        response = client.pipeline_requests_batch_get(
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


@deprecated_batch_requests.command("list", short_help="[DEPRECATED] List pipeline batch requests")
@PIPELINE_NAME_ARGUMENT
@VERSION_NAME_OPTIONAL
@OFFSET
@REQUEST_LIMIT
@LIST_FORMATS
def deprecated_batch_requests_list(pipeline_name, version_name, offset, limit, format_):
    """
    [DEPRECATED] List pipeline batch requests.
    Pipeline requests are only stored for pipeline versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to list the batch requests for a specific pipeline version.
    If not specified, the batch requests are listed for the default version.
    """

    if format_ != 'json':
        click.secho(
            "Deprecation warning: 'batch_requests list' is deprecated, use 'requests list' instead",
            fg='red'
        )

    project_name = get_current_project(error=True)

    client = init_client()
    if version_name is not None:
        response = client.pipeline_version_requests_list(
            project_name=project_name, pipeline_name=pipeline_name, version=version_name, limit=limit, offset=offset
        )

    else:
        response = client.pipeline_requests_list(
            project_name=project_name, pipeline_name=pipeline_name, limit=limit, offset=offset
        )

    client.api_client.close()
    print_list(response, REQUEST_LIST_ITEMS, fmt=format_)
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more)")
