import click
import ubiops as api

from ubiops_cli.constants import STRUCTURED_TYPE, PLAIN_TYPE
from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.src.helpers.pipeline_helpers import define_pipeline, get_changed_pipeline_structure, \
    PIPELINE_REQUIRED_FIELDS
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml, format_pipeline_requests_reference, \
    format_pipeline_requests_oneline, format_json, format_datetime, parse_datetime
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import get_current_project, init_client, read_json, read_yaml, write_yaml, parse_json


LIST_ITEMS = ['last_updated', 'name', 'labels']
REQUEST_LIST_ITEMS = ['id', 'status', 'time_created']


@click.group(name=["pipelines", "ppl"], short_help="Manage your pipelines")
def commands():
    """
    Manage your pipelines.
    """

    return


@commands.command(name="list", short_help="List pipelines")
@options.LABELS_FILTER
@options.LIST_FORMATS
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


@commands.command(name="get", short_help="Get a pipeline")
@options.PIPELINE_NAME_ARGUMENT
@options.PIPELINE_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
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
            optional=[
                'input_fields name', 'input_fields data_type', 'output_type', 'output_fields name',
                'output_fields data_type'
            ],
            rename={'name': 'pipeline_name', 'description': 'pipeline_description'},
            as_str=False
        )

        yaml_file = write_yaml(output_path, dictionary, default_file_name="pipeline.yaml")
        if not quiet:
            click.echo(f"Pipeline file is stored in: {yaml_file}")

    else:
        print_item(
            pipeline,
            row_attrs=LIST_ITEMS,
            required_front=['name', 'description', 'input_type'],
            optional=[
                'input_fields name', 'input_fields data_type', 'output_type', 'output_fields name',
                'output_fields data_type', 'creation_date', 'last_updated', 'default_version'
            ],
            rename={'name': 'pipeline_name', 'description': 'pipeline_description'},
            fmt=format_
        )


@commands.command(name="create", short_help="Create a pipeline")
@options.PIPELINE_NAME_OVERRULE
@options.PIPELINE_YAML_FILE
@options.CREATE_FORMATS
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
        required_front=['name', 'description', 'input_type'],
        optional=[
            'input_fields name', 'input_fields data_type', 'output_type', 'output_fields name',
            'output_fields data_type', 'creation_date', 'last_updated'
        ],
        rename={'name': 'pipeline_name', 'description': 'pipeline_description'},
        fmt=format_
    )


@commands.command(name="update", short_help="Update a pipeline")
@options.PIPELINE_NAME_ARGUMENT
@options.PIPELINE_NAME_UPDATE
@options.PIPELINE_YAML_FILE_UPDATE
@options.VERSION_DEFAULT_UPDATE
@options.QUIET
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
                raise UbiOpsException(
                    f"Trying to rename pipeline '{pipeline_name}' to '{pipeline.name}', but a pipeline with the new "
                    "name already exists"
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
            raise UbiOpsException(
                f"Trying to rename pipeline '{pipeline_name}' to '{new_name}', but a pipeline with the new "
                "name already exists"
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


@commands.command(name="delete", short_help="Delete a pipeline")
@options.PIPELINE_NAME_ARGUMENT
@options.ASSUME_YES
@options.QUIET
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


@commands.group(name="requests", short_help="Manage your pipeline requests")
def requests():
    """
    Manage your pipeline requests.
    """

    return


# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
@requests.command(name="create", short_help="Create pipeline request")
@options.PIPELINE_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_BATCH
@options.REQUEST_TIMEOUT
@options.REQUEST_OBJECT_TIMEOUT
@options.REQUEST_DATA_MULTI
@options.REQUEST_DATA_FILE
@options.REQUESTS_FORMATS
def requests_create(pipeline_name, version_name, batch, timeout, deployment_timeout, data, json_file, format_):
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
        raise UbiOpsException("It's not possible to pass a deployment timeout for a batch pipeline request")

    if json_file and data:
        raise UbiOpsException("Specify data either using the <data> or <json_file> option, not both")

    if json_file:
        input_data = read_json(json_file)
        if not isinstance(input_data, list):
            input_data = [input_data]

    elif data:
        if pipeline.input_type == STRUCTURED_TYPE:
            input_data = []
            for data_item in data:
                input_data.append(parse_json(data=data_item))
        else:
            input_data = data

    else:
        raise UbiOpsException("Missing option <data> or <json_file>")

    method = "pipeline_requests_create"
    params = {'project_name': project_name, 'pipeline_name': pipeline_name}

    if version_name is not None:
        method = "pipeline_version_requests_create"
        params['version'] = version_name

    if batch:
        if timeout is not None:
            params['timeout'] = timeout
    else:
        if timeout is not None:
            params['pipeline_timeout'] = timeout
        if deployment_timeout is not None:
            params['deployment_timeout'] = deployment_timeout

    if batch:
        response = getattr(client, f"batch_{method}")(**params, data=input_data)

    elif pipeline.input_type == PLAIN_TYPE:
        # We don't support list input for plain type, create the requests one by one
        response = [getattr(client, method)(**params, data=data) for data in input_data]

    else:
        response = [getattr(client, method)(**params, data=input_data)]

    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response, skip_attributes=["success"]))
    else:
        click.echo(format_pipeline_requests_reference(response))


@requests.command(name="get", short_help="Get a pipeline request")
@options.PIPELINE_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_ID_MULTI
@options.REQUESTS_FORMATS
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
        click.echo(format_json(response, skip_attributes=["success"]))

    else:
        click.echo(format_pipeline_requests_reference(response))


@requests.command(name="list", short_help="List pipeline requests")
@options.PIPELINE_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.OFFSET
@options.REQUEST_LIMIT
@options.REQUEST_SORT
@options.REQUEST_FILTER_PIPELINE_STATUS
@options.REQUEST_FILTER_SUCCESS_DEPRECATED
@options.REQUEST_FILTER_START_DATE
@options.REQUEST_FILTER_END_DATE
@options.REQUEST_FILTER_SEARCH_ID
@options.LIST_FORMATS
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
            raise UbiOpsException(
                "Failed to parse start_date. Please use iso-format, for example, '2020-01-01T00:00:00.000000Z'"
            )

    if 'end_date' in kwargs and kwargs['end_date']:
        try:
            kwargs['end_date'] = format_datetime(parse_datetime(kwargs['end_date']), fmt='%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            raise UbiOpsException(
                "Failed to parse end_date. Please use iso-format, for example, '2020-01-01T00:00:00.000000Z'"
            )

    if kwargs['success'] is not None:
        click.secho(message="Deprecation warning: 'success' is deprecated use 'status' instead", fg='red')

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
    print_list(response, REQUEST_LIST_ITEMS, fmt=format_, json_skip=["success"])
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more)")


# pylint: disable=too-many-arguments
@commands.command(name="request", short_help="[DEPRECATED] Create a pipeline direct request")
@options.PIPELINE_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_DATA
@options.REQUEST_PIPELINE_TIMEOUT_DEPRECATED
@options.REQUEST_OBJECT_TIMEOUT
@options.REQUESTS_FORMATS
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

    params = {'project_name': project_name, 'pipeline_name': pipeline_name, 'data': data}

    if pipeline_timeout is not None:
        params['pipeline_timeout'] = pipeline_timeout
    if deployment_timeout is not None:
        params['deployment_timeout'] = deployment_timeout

    if version_name is not None:
        params['version'] = version_name
        response = client.pipeline_version_requests_create(**params)
    else:
        response = client.pipeline_requests_create(**params)

    client.api_client.close()
    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference([response]))

    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline([response]))

    elif format_ == 'json':
        click.echo(format_json(response, skip_attributes=["success"]))

    else:
        click.echo(format_pipeline_requests_reference([response]))


@commands.group(name="batch_requests", short_help="[DEPRECATED] Manage your pipeline batch requests")
def deprecated_batch_requests():
    """
    [DEPRECATED] Manage your pipeline batch requests.
    """

    return


@deprecated_batch_requests.command(name="create", short_help="[DEPRECATED] Create a pipeline batch request")
@options.PIPELINE_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_DATA_MULTI
@options.REQUESTS_FORMATS
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
        for data_item in data:
            input_data.append(parse_json(data=data_item))
    else:
        input_data = data

    params = {
        'project_name': project_name,
        'pipeline_name': pipeline_name,
        'data': input_data
    }

    if version_name is not None:
        params['version'] = version_name
        response = client.batch_pipeline_version_requests_create(**params)
    else:
        response = client.batch_pipeline_requests_create(**params)

    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_pipeline_requests_reference(pipeline_requests=response))
    elif format_ == 'oneline':
        click.echo(format_pipeline_requests_oneline(pipeline_requests=response))
    elif format_ == 'json':
        click.echo(format_json(items=response, skip_attributes=["success"]))
    else:
        click.echo(format_pipeline_requests_reference(pipeline_requests=response))


@deprecated_batch_requests.command(name="get", short_help="[DEPRECATED] Get a pipeline batch request")
@options.PIPELINE_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_ID_MULTI
@options.REQUESTS_FORMATS
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
        click.echo(format_json(response, skip_attributes=["success"]))

    else:
        click.echo(format_pipeline_requests_reference(response))


@deprecated_batch_requests.command(name="list", short_help="[DEPRECATED] List pipeline batch requests")
@options.PIPELINE_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.OFFSET
@options.REQUEST_LIMIT
@options.LIST_FORMATS
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
    print_list(response, REQUEST_LIST_ITEMS, fmt=format_, json_skip=["success"])
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more)")
