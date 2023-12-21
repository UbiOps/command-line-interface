import os
from time import sleep

import click
import ubiops as api

from ubiops_cli.constants import STATUS_UNAVAILABLE, STRUCTURED_TYPE, PLAIN_TYPE, DEFAULT_IGNORE_FILE, UPDATE_TIME, \
    IMPLICIT_ENVIRONMENT_FILES
from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.src.helpers.deployment_helpers import define_deployment_version, update_deployment_file, \
    update_existing_deployment_version, DEPLOYMENT_VERSION_CREATE_FIELDS, DEPLOYMENT_REQUIRED_FIELDS
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml, format_requests_reference, \
    format_requests_oneline, format_json, parse_datetime, format_datetime
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import init_client, read_json, read_yaml, write_yaml, zip_dir, get_current_project, \
    set_dict_default, write_blob, default_version_zip_name, parse_json


LIST_ITEMS = ['last_updated', 'name', 'labels']
REQUEST_LIST_ITEMS = ['id', 'status', 'success', 'time_created']


@click.group(name=["deployments", "dpl"], short_help="Manage your deployments")
def commands():
    """
    Manage your deployments.
    """

    return


@commands.command(name="list", short_help="List deployments")
@options.LABELS_FILTER
@options.LIST_FORMATS
def deployments_list(labels, format_):
    """
    List all your deployments in your project.

    The `<labels>` option can be used to filter on specific labels.
    """

    label_filter = get_label_filter(labels)

    project_name = get_current_project()
    if project_name:
        client = init_client()
        deployments = client.deployments_list(project_name=project_name, labels=label_filter)
        client.api_client.close()
        print_list(items=deployments, attrs=LIST_ITEMS, sorting_col=1, fmt=format_)


@commands.command(name="get", short_help="Get details of a deployment")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.DEPLOYMENT_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
def deployments_get(deployment_name, output_path, quiet, format_):
    """
    Get the deployment settings, like, input_type and output_type.

    If you specify the `<output_path>` option, this location will be used to store the
    deployment settings in a yaml file. You can either specify the `<output_path>` as file or
    directory. If the specified `<output_path>` is a directory, the settings will be
    stored in `deployment.yaml`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    deployment = client.deployments_get(project_name=project_name, deployment_name=deployment_name)
    client.api_client.close()

    if output_path is not None:
        dictionary = format_yaml(
            item=deployment,
            required_front=['name', 'description', 'labels', 'input_type', 'output_type'],
            optional=['input_fields name', 'input_fields data_type', 'output_fields name', 'output_fields data_type'],
            rename={'name': 'deployment_name', 'description': 'deployment_description', 'labels': 'deployment_labels'},
            as_str=False
        )
        yaml_file = write_yaml(output_path, dictionary, default_file_name="deployment.yaml")
        if not quiet:
            click.echo(f"Deployment file is stored in: {yaml_file}")
    else:
        print_item(
            item=deployment,
            row_attrs=LIST_ITEMS,
            required_front=['id', 'name', 'project', 'description', 'labels', 'input_type', 'output_type'],
            optional=['input_fields name', 'input_fields data_type', 'output_fields name', 'output_fields data_type'],
            required_end=['creation_date', 'last_updated', 'default_version'],
            rename={'name': 'deployment_name', 'description': 'deployment_description', 'labels': 'deployment_labels'},
            fmt=format_
        )


@commands.command(name="create", short_help="Create a deployment")
@options.DEPLOYMENT_NAME_OVERRULE
@options.DEPLOYMENT_YAML_FILE
@options.CREATE_FORMATS
def deployments_create(deployment_name, yaml_file, format_):
    """
    Create a new deployment.

    \b
    Define the deployment parameters using a yaml file.
    For example:
    ```
    deployment_name: my-deployment-name
    deployment_description: Deployment created via command line.
    deployment_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    input_type: structured
    input_fields:
      - name: param1
        data_type: int
      - name: param2
        data_type: string
    output_type: plain
    ```

    The deployment name can either be passed as argument or specified inside the yaml
    file. If it is both passed as argument and specified inside the yaml file, the value
    passed as argument is used.

    Possible input/output types: [structured, plain]. Possible data_types: [blob, int,
    string, double, bool, array_string, array_int, array_double].
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=DEPLOYMENT_REQUIRED_FIELDS)
    client = init_client()

    assert 'deployment_name' in yaml_content or deployment_name, 'Please, specify the deployment name in either the ' \
                                                                 'yaml file or as a command argument'

    deployment_name = set_dict_default(deployment_name, yaml_content, 'deployment_name')
    description = set_dict_default(None, yaml_content, 'deployment_description')

    if 'input_fields' in yaml_content and isinstance(yaml_content['input_fields'], list):
        input_fields = [api.DeploymentInputFieldCreate(name=item['name'], data_type=item['data_type'])
                        for item in yaml_content['input_fields']]
    else:
        input_fields = None

    if 'output_fields' in yaml_content and isinstance(yaml_content['output_fields'], list):
        output_fields = [api.DeploymentInputFieldCreate(name=item['name'], data_type=item['data_type'])
                         for item in yaml_content['output_fields']]
    else:
        output_fields = None

    if 'deployment_labels' in yaml_content:
        labels = yaml_content['deployment_labels']
    else:
        labels = {}

    deployment = api.DeploymentCreate(
        name=deployment_name,
        description=description,
        input_type=yaml_content['input_type'],
        output_type=yaml_content['output_type'],
        input_fields=input_fields,
        output_fields=output_fields,
        labels=labels
    )
    response = client.deployments_create(project_name=project_name, data=deployment)
    client.api_client.close()

    print_item(
        item=response,
        row_attrs=LIST_ITEMS,
        required_front=['id', 'name', 'project', 'description', 'labels', 'input_type', 'output_type'],
        optional=['input_fields name', 'input_fields data_type', 'output_fields name', 'output_fields data_type'],
        required_end=['creation_date', 'last_updated'],
        rename={'name': 'deployment_name', 'description': 'deployment_description', 'labels': 'deployment_labels'},
        fmt=format_
    )


@commands.command(name="update", short_help="Update a deployment")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.DEPLOYMENT_NAME_UPDATE
@options.VERSION_DEFAULT_UPDATE
@options.DEPLOYMENT_YAML_FILE_OPTIONAL
@options.QUIET
def deployments_update(deployment_name, new_name, default_version, yaml_file, quiet):
    """
    Update a deployment.

    If you only want to update the name of the deployment or the default deployment version,
    use the options `<new_name>` and `<default_version>`.
    If you want to update the deployment input/output fields, description or labels, please use a yaml file to define
    the new deployment.

    \b
    For example:
    ```
    deployment_description: Deployment created via command line.
    deployment_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    input_fields:
      - name: param1
        data_type: int
      - name: param2
        data_type: string
    output_fields:
      - name: param1
        data_type: int
      - name: param2
        data_type: string
    ```
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)

    deployment = api.DeploymentUpdate(name=new_name, default_version=default_version)
    if 'deployment_description' in yaml_content:
        deployment.description = yaml_content['deployment_description']
    if 'deployment_labels' in yaml_content:
        deployment.labels = yaml_content['deployment_labels']
    if 'input_fields' in yaml_content and isinstance(yaml_content['input_fields'], list):
        deployment.input_fields = [
            api.DeploymentInputFieldCreate(name=item['name'], data_type=item['data_type'])
            for item in yaml_content['input_fields']
        ]
    if 'output_fields' in yaml_content and isinstance(yaml_content['output_fields'], list):
        deployment.output_fields = [
            api.DeploymentInputFieldCreate(name=item['name'], data_type=item['data_type'])
            for item in yaml_content['output_fields']
        ]

    client = init_client()
    client.deployments_update(project_name=project_name, deployment_name=deployment_name, data=deployment)
    client.api_client.close()

    if not quiet:
        click.echo("Deployment was successfully updated")


@commands.command(name="delete", short_help="Delete a deployment")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.ASSUME_YES
@options.QUIET
def deployments_delete(deployment_name, assume_yes, quiet):
    """
    Delete a deployment.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete deployment <{deployment_name}> of project <{project_name}>?"
    ):
        client = init_client()
        client.deployments_delete(project_name=project_name, deployment_name=deployment_name)
        client.api_client.close()

        if not quiet:
            click.echo("Deployment was successfully deleted")


# pylint: disable=too-many-arguments
@commands.command(name="package", short_help="Package deployment code")
@options.DEPLOYMENT_NAME_ZIP
@options.VERSION_NAME_ZIP
@options.PACKAGE_DIR
@options.ZIP_OUTPUT
@options.IGNORE_FILE
@options.ASSUME_YES
@options.QUIET
def deployments_package(deployment_name, version_name, directory, output_path, ignore_file, assume_yes, quiet):
    """
    Package code to ZIP file which is ready to be deployed.

    Please, specify the code `<directory>` that should be deployed. The files in this directory will be zipped.
    Subdirectories and files that shouldn't be contained in the ZIP can be specified in an ignore file, which is by
    default '.ubiops-ignore'. The structure of this file is assumed to be equal to the well-known .gitignore file.

    Use the `<output_path>` option to specify the output location of the zip file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the zip will be saved in
    `[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use the `<assume_yes>` option to overwrite
    without confirmation if file specified in `<output_path>` already exists.
    """

    ignore_file = DEFAULT_IGNORE_FILE if ignore_file is None else ignore_file
    zip_path, _ = zip_dir(
        directory=directory,
        output_path=output_path,
        ignore_filename=ignore_file,
        deployment_name=deployment_name,
        version_name=version_name,
        force=assume_yes
    )
    if not quiet:
        click.echo(f"Created zip: {zip_path}")


@commands.command(name="upload", short_help="Upload a deployment package")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTION
@options.ZIP_FILE
@options.OVERWRITE
@options.PROGRESS_BAR
@options.QUIET
def deployments_upload(deployment_name, version_name, zip_path, overwrite, progress_bar, quiet):
    """
    Upload ZIP to a version of a deployment.

    Please, specify the deployment package `<zip_path>` that should be uploaded.
    Use the `<overwrite>` option to overwrite the deployment package on UbiOps if one already exists for this version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    current_version = client.deployment_versions_get(
        project_name=project_name, deployment_name=deployment_name, version=version_name
    )

    if overwrite or current_version.status == STATUS_UNAVAILABLE:
        client.revisions_file_upload(
            project_name=project_name, deployment_name=deployment_name, version=version_name, file=zip_path,
            _progress_bar=progress_bar
        )
        client.api_client.close()

        if not quiet:
            click.echo("Deployment was successfully uploaded")
    else:
        client.api_client.close()
        raise UbiOpsException("A deployment package already exists for this deployment version")


@commands.command(name="download", short_help="Download a deployment package")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTION
@options.ZIP_OUTPUT
@options.QUIET
def deployments_download(deployment_name, version_name, output_path, quiet):
    """
    Get the version of a deployment.

    The `<output_path>` option will be used as output location of the zip file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the zip will be
    saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    version = client.deployment_versions_get(
        project_name=project_name, deployment_name=deployment_name, version=version_name
    )
    if not version.active_revision:
        raise UbiOpsException("No active revision available for this deployment")

    with client.revisions_file_download(
            project_name=project_name, deployment_name=deployment_name,
            version=version_name, revision_id=version.active_revision
    ) as response:
        filename = default_version_zip_name(deployment_name, version_name)
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo(f"Zip stored in: {output_path}")


# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
@commands.command(name="deploy", short_help="Deploy a new version of a deployment")
@options.DEPLOYMENT_NAME_OVERRULE
@options.VERSION_NAME_OPTIONAL
@options.PACKAGE_DIR
@options.DEPLOYMENT_FILE
@options.IGNORE_FILE
@options.ZIP_OUTPUT_STORE
@options.VERSION_YAML_FILE
@options.LANGUAGE
@options.ENVIRONMENT
@options.INSTANCE_TYPE
@options.MIN_INSTANCES
@options.MAX_INSTANCES
@options.MAX_IDLE_TIME
@options.DEPLOYMENT_MODE_DEPRECATED
@options.RETENTION_MODE
@options.RETENTION_TIME
@options.MAX_QUEUE_SIZE_EXPRESS
@options.MAX_QUEUE_SIZE_BATCH
@options.VERSION_STATIC_IP
@options.VERSION_LABELS
@options.VERSION_DESCRIPTION
@options.OVERWRITE
@options.ASSUME_YES
@options.PROGRESS_BAR
@options.QUIET
def deployments_deploy(deployment_name, version_name, directory, output_path, yaml_file, overwrite, assume_yes,
                       progress_bar, quiet, **kwargs):
    """
    Deploy a new version of a deployment.

    Please, specify the code `<directory>` that should be deployed. The files in this directory
    will be zipped and uploaded. Subdirectories and files that shouldn't be contained in the
    ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this
    file is assumed to be equal to the well-known '.gitignore' file.

    If you want to store a local copy of the uploaded zip file, please use the `<output_path>` option.
    The `<output_path>` option will be used as output location of the zip file. If the `<output_path>` is a
    directory, the zip will be saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use
    the `<assume_yes>` option to overwrite without confirmation if file specified in `<output_path>` already exists.

    \b
    It is possible to define the parameters using a yaml file.
    For example:
    ```
    deployment_name: my-deployment-name
    version_name: my-deployment-version
    version_description: Version created via command line.
    version_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    environment: python3-8
    instance_type: 2048mb
    minimum_instances: 0
    maximum_instances: 1
    maximum_idle_time: 300
    request_retention_mode: none
    request_retention_time: 604800
    maximum_queue_size_express: 100
    maximum_queue_size_batch: 100000
    static_ip: false
    ```

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and options are given,
    the options defined by `<yaml_file>` will be overwritten by the specified command options. The deployment name can
    either be passed as command argument or specified inside the yaml file using `<deployment_name>`.
    """

    if output_path is None:
        store_zip = False
        output_path = ''
    else:
        store_zip = True

    project_name = get_current_project(error=True)
    client = init_client()
    yaml_content = read_yaml(yaml_file, required_fields=[])

    assert 'deployment_name' in yaml_content or deployment_name, 'Please, specify the deployment name in either the ' \
                                                                 'yaml file or as a command argument'
    assert 'version_name' in yaml_content or version_name, 'Please, specify the version name in either the yaml ' \
                                                           'file or as a command option'

    if not quiet and ('deployment_mode' in yaml_content or kwargs['deployment_mode']):
        click.secho(
            "Deprecation warning: 'deployment_mode' is deprecated. From now on, both direct and batch requests can be "
            "made to the same deployment version.", fg='red'
        )

    if not quiet and ('language' in yaml_content or kwargs['language']):
        click.secho("Deprecation warning: 'language' is deprecated. Use 'environment' instead.", fg='red')

    deployment_name = set_dict_default(deployment_name, yaml_content, 'deployment_name')
    version_name = set_dict_default(version_name, yaml_content, 'version_name')

    existing_version = None
    if overwrite:
        try:
            existing_version = client.deployment_versions_get(
                project_name=project_name, deployment_name=deployment_name, version=version_name
            )
        except api.exceptions.ApiException:
            # Do nothing if version doesn't exist
            pass

    kwargs = define_deployment_version(kwargs, yaml_content, extra_yaml_fields=['deployment_file', 'ignore_file'])
    kwargs['ignore_file'] = DEFAULT_IGNORE_FILE if kwargs['ignore_file'] is None else kwargs['ignore_file']

    zip_path, implicit_environment = zip_dir(
        directory=directory,
        output_path=output_path,
        ignore_filename=kwargs['ignore_file'],
        deployment_name=deployment_name,
        version_name=version_name,
        force=assume_yes
    )

    try:
        has_uploaded_zips = False
        has_changed_fields = False

        if not (overwrite and existing_version):
            # Only use the fields given in keyword arguments when creating the deployment version
            version_fields = {}
            for k in DEPLOYMENT_VERSION_CREATE_FIELDS:
                if k in kwargs:
                    version_fields[k] = kwargs[k]

            version = api.DeploymentVersionCreate(version=version_name, **version_fields)
            client.deployment_versions_create(project_name=project_name, deployment_name=deployment_name, data=version)
        else:
            revisions = client.revisions_list(
                project_name=project_name, deployment_name=deployment_name, version=version_name
            )
            has_uploaded_zips = len(revisions) > 0

        if implicit_environment and not has_uploaded_zips and kwargs.get('environment', None) is not None:
            # We don't show a warning on re-uploads
            try:
                environment = client.environments_get(
                    project_name=project_name, environment_name=kwargs['environment']
                )
                if environment.base_environment is not None:
                    # A custom environment is used
                    click.secho(
                        message="Warning: You are trying to upload a deployment file containing at least one"
                                f" environment file (e.g. {IMPLICIT_ENVIRONMENT_FILES[0]}). It's not possible to use"
                                " a custom environment in combination with an implicitly created environment.\nConsider"
                                f" adding the environment files to {kwargs['ignore_file']} so no implicit environment"
                                f" is created on revision file upload.",
                        fg='yellow'
                    )
            except api.exceptions.ApiException:
                pass

        if overwrite and existing_version:
            has_changed_fields = update_existing_deployment_version(
                client, project_name, deployment_name, version_name, existing_version, kwargs
            )

        has_changed_env_vars = update_deployment_file(
            client, project_name, deployment_name, version_name, kwargs['deployment_file']
        )

        if has_uploaded_zips and (has_changed_fields or has_changed_env_vars):
            # Wait for changes being applied
            click.echo(f"Waiting for changes to take effect... This takes {UPDATE_TIME} seconds.")
            sleep(UPDATE_TIME)

        client.revisions_file_upload(
            project_name=project_name, deployment_name=deployment_name, version=version_name, file=zip_path,
            _progress_bar=progress_bar
        )
        client.api_client.close()
    except Exception as e:
        if os.path.isfile(zip_path) and not store_zip:
            os.remove(zip_path)
        client.api_client.close()
        raise e

    if os.path.isfile(zip_path):
        if store_zip:
            if not quiet:
                click.echo(f"Created zip: {zip_path}")
        else:
            os.remove(zip_path)

    if not quiet:
        click.echo("Deployment was successfully deployed")


@commands.group(name="requests", short_help="Manage your deployment requests")
def requests():
    """
    Manage your deployment requests.
    """

    return


# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
@requests.command(name="create", short_help="Create deployment request")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_BATCH
@options.REQUEST_DATA_MULTI
@options.REQUEST_DATA_FILE
@options.REQUEST_TIMEOUT
@options.REQUESTS_FORMATS
def requests_create(deployment_name, version_name, batch, data, json_file, timeout, format_):
    """
    Create a deployment request and retrieve request IDs to collect the results later.
    Use the option `timeout` to specify the timeout of the request. The minimum value is 10 seconds. The maximum value
    is 3600 (1 hour) for direct (synchronous) requests and 345600 (96 hours) for batch (asynchronous) requests.
    The default value is 300 (5 minutes) for direct requests and 14400 (4 hours) for batch requests.

    Use the version option to make a request to a specific deployment version:
    `ubiops deployments requests create <my-deployment> -v <my-version> --data <input>`

    If not specified, a request is made to the default version:
    `ubiops deployments requests create <my-deployment> --data <input>`

    Use `--batch` to make an asynchronous batch request:
    `ubiops deployments requests create <my-deployment> --batch --data <input>`

    Multiple data inputs can be specified at ones and send as batch by using the '--data' options multiple times:
    `ubiops deployments requests create <my-deployment> --batch --data <input-1> --data <input-2> --data <input-3>`

    For structured input, specify data input as JSON formatted string. For example:
    `ubiops deployments requests create <my-deployment> --data "{\\"param1\\": 1, \\"param2\\": \\"two\\"}"`
    """

    data = list(data)

    project_name = get_current_project(error=True)

    client = init_client()
    deployment = client.deployments_get(project_name=project_name, deployment_name=deployment_name)

    if json_file and data:
        raise UbiOpsException("Specify data either using the <data> or <json_file> option, not both")

    if json_file:
        input_data = read_json(json_file)
        if not isinstance(input_data, list):
            input_data = [input_data]

    elif data:
        if deployment.input_type == STRUCTURED_TYPE:
            input_data = []
            for data_item in data:
                input_data.append(parse_json(data_item))
        else:
            input_data = data

    else:
        raise UbiOpsException("Missing option <data> or <json_file>")

    method = "deployment_requests_create"
    params = {'project_name': project_name, 'deployment_name': deployment_name}

    if timeout is not None:
        params['timeout'] = timeout

    if version_name is not None:
        method = "deployment_version_requests_create"
        params['version'] = version_name

    if batch:
        response = getattr(client, f"batch_{method}")(**params, data=input_data)

    elif deployment.input_type == PLAIN_TYPE:
        # We don't support list input for plain type, create the requests one by one
        response = [getattr(client, method)(**params, data=data) for data in input_data]

    else:
        response = [getattr(client, method)(**params, data=input_data)]

    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response, skip_attributes=["success"]))
    else:
        click.echo(format_requests_reference(response))


@requests.command(name="get", short_help="Get deployment request")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_ID_MULTI
@options.REQUESTS_FORMATS
def requests_get(deployment_name, version_name, request_id, format_):
    """
    Get one or more stored deployment requests.
    Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to get a request for a specific deployment version.
    If not specified, the request is retrieved for the default version.

    Multiple request ids can be specified at ones by using the '-id' options multiple times:
    `ubiops deployments requests get <my-deployment> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`
    """

    request_ids = list(request_id)

    project_name = get_current_project(error=True)

    client = init_client()
    if version_name is not None:
        response = client.deployment_version_requests_batch_get(
            project_name=project_name, deployment_name=deployment_name, version=version_name, data=request_ids
        )
    else:
        response = client.deployment_requests_batch_get(
            project_name=project_name, deployment_name=deployment_name, data=request_ids
        )
    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response, skip_attributes=["success"]))
    else:
        click.echo(format_requests_reference(response))


@requests.command(name="list", short_help="List deployment requests")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.OFFSET
@options.REQUEST_LIMIT
@options.REQUEST_SORT
@options.REQUEST_FILTER_DEPLOYMENT_STATUS
@options.REQUEST_FILTER_SUCCESS_DEPRECATED
@options.REQUEST_FILTER_START_DATE
@options.REQUEST_FILTER_END_DATE
@options.REQUEST_FILTER_SEARCH_ID
@options.REQUEST_FILTER_IN_PIPELINE
@options.LIST_FORMATS
def requests_list(deployment_name, version_name, limit, format_, **kwargs):
    """
    List stored deployment requests.
    Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to list the requests for a specific deployment version.
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
        response = client.deployment_version_requests_list(
            project_name=project_name, deployment_name=deployment_name, version=version_name, limit=limit, **kwargs
        )
    else:
        response = client.deployment_requests_list(
            project_name=project_name, deployment_name=deployment_name, limit=limit, **kwargs
        )
    client.api_client.close()

    print_list(response, REQUEST_LIST_ITEMS, fmt=format_, json_skip=["success"])
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more)")


@commands.command(name="request", short_help="[DEPRECATED] Create deployment direct requests")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_DATA
@options.REQUEST_DEPLOYMENT_TIMEOUT_DEPRECATED
@options.REQUESTS_FORMATS
def deprecated_deployments_request(deployment_name, version_name, data, timeout, format_):
    """
    [DEPRECATED] Create a deployment request and retrieve the result.

    Use the version option to make a request to a specific deployment version:
    `ubiops deployments request <my-deployment> -v <my-version> --data <input>`

    If not specified, a request is made to the default version:
    `ubiops deployments request <my-deployment> --data <input>`

    For structured input, specify the data as JSON formatted string. For example:
    `ubiops deployments request <my-deployment> --data "{\\"param1\\": 1, \\"param2\\": \\"two\\"}"`
    """

    if format_ != 'json':
        click.secho(
            "Deprecation warning: 'request' is deprecated, use 'requests create' instead",
            fg='red'
        )

    project_name = get_current_project(error=True)

    client = init_client()
    deployment = client.deployments_get(project_name=project_name, deployment_name=deployment_name)

    if deployment.input_type == STRUCTURED_TYPE:
        data = parse_json(data)

    params = {
        'project_name': project_name,
        'deployment_name': deployment_name,
        'data': data
    }

    if timeout is not None:
        params['timeout'] = timeout

    if version_name is not None:
        params['version'] = version_name
        response = client.deployment_version_requests_create(**params)
    else:
        response = client.deployment_requests_create(**params)

    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_requests_reference([response]))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline([response]))
    elif format_ == 'json':
        click.echo(format_json(response, skip_attributes=["success"]))
    else:
        click.echo(format_requests_reference([response]))


@commands.group(name="batch_requests", short_help="[DEPRECATED] Manage your deployment batch requests")
def deprecated_batch_requests():
    """
    [DEPRECATED] Manage your deployment batch requests.
    """

    return


@deprecated_batch_requests.command(name="create", short_help="[DEPRECATED] Create deployment batch request")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_DATA_MULTI
@options.REQUEST_TIMEOUT
@options.REQUESTS_FORMATS
def deprecated_batch_requests_create(deployment_name, version_name, data, timeout, format_):
    """
    [DEPRECATED] Create a deployment batch request and retrieve request IDs to collect the results later.
    Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

    Use the option `timeout` to specify the timeout of the request. The minimum value is 10 seconds. The maximum value
    is 345600 (96 hours). The default value is 14400 (4 hours).

    Use the version option to make a batch request to a specific deployment version:
    `ubiops deployments batch_requests create <my-deployment> -v <my-version> --data <input>`

    If not specified, a batch request is made to the default version:
    `ubiops deployments batch_requests create <my-deployment> --data <input>`

    Multiple data inputs can be specified at ones by using the '--data' options multiple times:
    `ubiops deployments batch_requests create <my-deployment> --data <input-1> --data <input-2> --data <input-3>`

    For structured input, specify each data input as JSON formatted string. For example:
    `ubiops deployments batch_requests create <my-deployment> --data "{\\"param1\\": 1, \\"param2\\": \\"two\\"}"`
    """

    if format_ != 'json':
        click.secho(
            "Deprecation warning: 'batch_requests create' is deprecated, use 'requests create --batch' instead",
            fg='red'
        )

    data = list(data)

    project_name = get_current_project(error=True)

    client = init_client()
    deployment = client.deployments_get(project_name=project_name, deployment_name=deployment_name)

    if deployment.input_type == STRUCTURED_TYPE:
        input_data = []
        for data_item in data:
            input_data.append(parse_json(data=data_item))
    else:
        input_data = data

    params = {
        'project_name': project_name,
        'deployment_name': deployment_name,
        'data': input_data
    }

    if timeout is not None:
        params['timeout'] = timeout

    if version_name is not None:
        params['version'] = version_name
        response = client.batch_deployment_version_requests_create(**params)
    else:
        response = client.batch_deployment_requests_create(**params)

    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response, skip_attributes=["success"]))
    else:
        click.echo(format_requests_reference(response))


@deprecated_batch_requests.command(name="get", short_help="[DEPRECATED] Get deployment batch request")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.REQUEST_ID_MULTI
@options.REQUESTS_FORMATS
def deprecated_batch_requests_get(deployment_name, version_name, request_id, format_):
    """
    [DEPRECATED] Get the results of one or more deployment batch requests.
    Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to get a batch request for a specific deployment version.
    If not specified, the batch request is retrieved for the default version.

    Multiple request ids can be specified at ones by using the '-id' options multiple times:
    `ubiops deployments batch_requests get <my-deployment> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`
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
        response = client.deployment_version_requests_batch_get(
            project_name=project_name, deployment_name=deployment_name, version=version_name, data=request_ids
        )
    else:
        response = client.deployment_requests_batch_get(
            project_name=project_name, deployment_name=deployment_name, data=request_ids
        )
    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response, skip_attributes=["success"]))
    else:
        click.echo(format_requests_reference(response))


@deprecated_batch_requests.command(name="list", short_help="[DEPRECATED] List deployment batch requests")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.OFFSET
@options.REQUEST_LIMIT
@options.LIST_FORMATS
def deprecated_batch_requests_list(deployment_name, version_name, offset, limit, format_):
    """
    [DEPRECATED] List deployment batch requests.
    Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to list the batch requests for a specific deployment version.
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
        response = client.deployment_version_requests_list(
            project_name=project_name, deployment_name=deployment_name, version=version_name, limit=limit, offset=offset
        )
    else:
        response = client.deployment_requests_list(
            project_name=project_name, deployment_name=deployment_name, limit=limit, offset=offset
        )
    client.api_client.close()

    print_list(response, REQUEST_LIST_ITEMS, fmt=format_, json_skip=["success"])
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more)")
