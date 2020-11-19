import ubiops as api
import os

from pkg.utils import init_client, read_yaml, write_yaml, zip_dir, get_current_project, \
    set_dict_default, write_blob, default_version_zip_name, parse_json
from pkg.src.helpers.helpers import set_version_defaults, update_deployment_file, VERSION_FIELDS, get_label_filter
from pkg.src.helpers.formatting import print_list, print_item, format_yaml, format_requests_reference, \
    format_requests_oneline, format_json
from pkg.src.helpers.options import *
from pkg.constants import STATUS_INITIALISED, STRUCTURED_TYPE, DEFAULT_IGNORE_FILE


LIST_ITEMS = ['id', 'name', 'last_updated', 'labels']
REQUEST_LIST_ITEMS = ['id', 'status', 'success', 'time_created']


@click.group(["deployments", "dpl"], short_help="Manage your deployments")
def commands():
    """Manage your deployments."""
    pass


@commands.command("list", short_help="List deployments")
@LABELS_FILTER
@LIST_FORMATS
def deployments_list(labels, format_):
    """
    List all your deployments in your project.

    The <labels> option can be used to filter on specific labels.
    """

    label_filter = get_label_filter(labels)

    project_name = get_current_project()
    if project_name:
        client = init_client()
        deployments = client.deployments_list(project_name=project_name, labels=label_filter)
        client.api_client.close()
        print_list(deployments, LIST_ITEMS, project_name=project_name, sorting_col=1, fmt=format_)


@commands.command("get", short_help="Get details of a deployment")
@DEPLOYMENT_NAME_ARGUMENT
@DEPLOYMENT_YAML_OUTPUT
@QUIET
@GET_FORMATS
def deployments_get(deployment_name, output_path, quiet, format_):
    """Get the deployment settings, like, input_type and output_type.

    If you specify the <output_path> option, this location will be used to store the
    deployment settings in a yaml file. You can either specify the <output_path> as file or
    directory. If the specified <output_path> is a directory, the settings will be
    stored in `deployment.yaml`."""

    project_name = get_current_project(error=True)

    client = init_client()
    deployment = client.deployments_get(project_name=project_name, deployment_name=deployment_name)
    client.api_client.close()

    if output_path is not None:
        dictionary = format_yaml(
            deployment,
            required_front=['name', 'description', 'input_type', 'output_type'],
            optional=['input_fields', 'output_fields'],
            rename={'name': 'deployment_name', 'description': 'deployment_description'},
            as_str=False
        )
        yaml_file = write_yaml(output_path, dictionary, default_file_name="deployment.yaml")
        if not quiet:
            click.echo('Deployment file is stored in: %s' % yaml_file)
    else:
        print_item(deployment, row_attrs=LIST_ITEMS, project_name=project_name,
                   rename={'name': 'deployment_name', 'description': 'deployment_description'}, fmt=format_)


@commands.command("create", short_help="Create a deployment")
@DEPLOYMENT_NAME_OVERRULE
@DEPLOYMENT_YAML_FILE
@CREATE_FORMATS
def deployments_create(deployment_name, yaml_file, format_):
    """Create a new deployment.

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

    if 'input_fields' in yaml_content:
        input_fields = [api.DeploymentInputFieldCreate(name=item['name'], data_type=item['data_type'])
                        for item in yaml_content['input_fields']]
    else:
        input_fields = None

    if 'output_fields' in yaml_content:
        output_fields = [api.DeploymentInputFieldCreate(name=item['name'], data_type=item['data_type'])
                         for item in yaml_content['output_fields']]
    else:
        output_fields = None

    if 'deployment_labels' in yaml_content:
        labels = yaml_content['deployment_labels']
    else:
        labels = {}

    deployment = api.DeploymentCreate(
        name=deployment_name, description=description,
        input_type=yaml_content['input_type'], output_type=yaml_content['output_type'],
        input_fields=input_fields, output_fields=output_fields, labels=labels)
    response = client.deployments_create(project_name=project_name, data=deployment)
    client.api_client.close()

    print_item(response, row_attrs=LIST_ITEMS,  project_name=project_name,
               rename={'name': 'deployment_name', 'description': 'deployment_description'}, fmt=format_)


@commands.command("update", short_help="Update a deployment")
@DEPLOYMENT_NAME_ARGUMENT
@DEPLOYMENT_NAME_UPDATE
@QUIET
def deployments_update(deployment_name, new_name, quiet):
    """Update a deployment."""

    project_name = get_current_project(error=True)

    client = init_client()
    deployment = api.DeploymentUpdate(name=new_name if new_name else deployment_name)
    client.deployments_update(project_name=project_name, deployment_name=deployment_name, data=deployment)
    client.api_client.close()

    if not quiet:
        click.echo("Deployment was successfully updated")


@commands.command("delete", short_help="Delete a deployment")
@DEPLOYMENT_NAME_ARGUMENT
@ASSUME_YES
@QUIET
def deployments_delete(deployment_name, assume_yes, quiet):
    """Delete a deployment."""

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm("Are you sure you want to delete deployment <%s> "
                                   "of project <%s>?" % (deployment_name, project_name)):
        client = init_client()
        client.deployments_delete(project_name=project_name, deployment_name=deployment_name)
        client.api_client.close()

        if not quiet:
            click.echo("Deployment was successfully deleted")


@commands.command("package", short_help="Package deployment code")
@DEPLOYMENT_NAME_ZIP
@VERSION_NAME_ZIP
@PACKAGE_DIR
@ZIP_OUTPUT
@IGNORE_FILE
@ASSUME_YES
@QUIET
def deployments_package(deployment_name, version_name, directory, output_path, ignore_file, assume_yes, quiet):
    """Package code to ZIP file which is ready to be deployed.

    Please, specify the code <directory> that should be deployed. The files in this directory
    will be zipped and uploaded. Subdirectories and files that shouldn't be contained in
    the ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of
    this file is assumed to be equal to the wellknown .gitignore file.

    Use the <output_path> option to specify the output location of the zip file. If not specified,
    the current directory will be used. If the <output_path> is a directory, the zip will be saved in
    `[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use the <assume_yes> option to overwrite
    without confirmation if file specified in <output_path> already exists.
    """

    ignore_file = DEFAULT_IGNORE_FILE if ignore_file is None else ignore_file
    zip_path = zip_dir(directory, output_path, ignore_filename=ignore_file,
                       deployment_name=deployment_name, version_name=version_name, force=assume_yes)
    if not quiet:
        click.echo("Created zip: %s" % zip_path)


@commands.command("upload", short_help="Upload a deployment package")
@DEPLOYMENT_NAME_ARGUMENT
@VERSION_NAME_OPTION
@ZIP_FILE
@OVERWRITE
@QUIET
def deployments_upload(deployment_name, version_name, zip_path, overwrite, quiet):
    """Upload ZIP to a version of a deployment.

    Please, specify the deployment package <zip_path> that should be uploaded.
    Use the <overwrite> option to overwrite the deployment package on UbiOps if one already exists for this version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    current_version = client.versions_get(project_name=project_name, deployment_name=deployment_name,
                                          version=version_name)

    if overwrite or current_version.status == STATUS_INITIALISED:
        client.versions_file_upload(project_name=project_name, deployment_name=deployment_name,
                                    version=version_name, file=zip_path)
        client.api_client.close()

        if not quiet:
            click.echo("Deployment was successfully uploaded")
    else:
        client.api_client.close()
        raise Exception("A deployment package already exists for this deployment version")


@commands.command("download", short_help="Download a deployment package")
@DEPLOYMENT_NAME_ARGUMENT
@VERSION_NAME_OPTION
@ZIP_OUTPUT
@QUIET
def deployments_download(deployment_name, version_name, output_path, quiet):
    """Get the version of a deployment.

    The <output_path> option will be used as output location of the zip file. If not specified,
    the current directory will be used. If the <output_path> is a directory, the zip will be
    saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    with client.versions_file_download(project_name=project_name,
                                       deployment_name=deployment_name,
                                       version=version_name) as response:
        filename = default_version_zip_name(deployment_name, version_name)
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo("Zip stored in: %s" % output_path)


@commands.command("deploy", short_help="Deploy a new version of a deployment")
@DEPLOYMENT_NAME_OVERRULE
@VERSION_NAME_OPTIONAL
@PACKAGE_DIR
@DEPLOYMENT_FILE
@IGNORE_FILE
@ZIP_OUTPUT_STORE
@VERSION_YAML_FILE
@LANGUAGE
@MEMORY_ALLOCATION
@MIN_INSTANCES
@MAX_INSTANCES
@MAX_IDLE_TIME
@VERSION_LABELS
@VERSION_DESCRIPTION
@OVERWRITE
@ASSUME_YES
@QUIET
def deployments_deploy(deployment_name, version_name, directory, output_path, yaml_file, overwrite, assume_yes, quiet,
                       **kwargs):
    """Deploy a new version of a deployment.

    Please, specify the code <directory> that should be deployed. The files in this directory
    will be zipped and uploaded. Subdirectories and files that shouldn't be contained in the
    ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this
    file is assumed to be equal to the wellknown .gitignore file.

    If you want to store a local copy of the uploaded zip file, please use the <output_path> option.
    The <output_path> option will be used as output location of the zip file. If the <output_path> is a
    directory, the zip will be saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use
    the <assume_yes> option to overwrite without confirmation if file specified in <output_path> already exists.

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
    language: python3.6
    memory_allocation: 256
    minimum_instances: 0
    maximum_instances: 1
    maximum_idle_time: 300
    ```

    Those parameters can also be provided as command options. If both a <yaml_file> is set and options are given,
    the options defined by <yaml_file> will be overwritten by the specified command options. The deployment name can
    either be passed as command argument or specified inside the yaml file using <deployment_name>.
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

    deployment_name = set_dict_default(deployment_name, yaml_content, 'deployment_name')
    version_name = set_dict_default(version_name, yaml_content, 'version_name')

    existing_version = None
    if overwrite:
        try:
            existing_version = client.versions_get(project_name=project_name, deployment_name=deployment_name,
                                                   version=version_name)
        except api.exceptions.ApiException:
            # do nothing if version doesn't exist
            pass

    kwargs = set_version_defaults(kwargs, yaml_content, existing_version,
                                  extra_yaml_fields=['deployment_file', 'ignore_file'])
    kwargs['ignore_file'] = DEFAULT_IGNORE_FILE if kwargs['ignore_file'] is None else kwargs['ignore_file']
    version = api.VersionCreate(version=version_name, **{k: kwargs[k] for k in VERSION_FIELDS})
    zip_path = zip_dir(directory, output_path, ignore_filename=kwargs['ignore_file'],
                       deployment_name=deployment_name, version_name=version_name, force=assume_yes)

    try:
        if not (overwrite and existing_version):
            client.versions_create(project_name=project_name, deployment_name=deployment_name, data=version)

        update_deployment_file(client, project_name, deployment_name, version_name, kwargs['deployment_file'])
        client.versions_file_upload(project_name=project_name, deployment_name=deployment_name,
                                    version=version_name, file=zip_path)

        if overwrite and existing_version:
            client.versions_update(project_name=project_name, deployment_name=deployment_name, version=version_name,
                                   data=version)
        client.api_client.close()
    except Exception as e:
        if os.path.isfile(zip_path) and not store_zip:
            os.remove(zip_path)
        client.api_client.close()
        raise e

    if os.path.isfile(zip_path):
        if store_zip:
            if not quiet:
                click.echo("Created zip: %s" % zip_path)
        else:
            os.remove(zip_path)

    if not quiet:
        click.echo("Deployment was successfully deployed")


@commands.command("request", short_help="Create deployment direct requests")
@DEPLOYMENT_NAME_ARGUMENT
@VERSION_NAME_OPTION
@REQUEST_DATA
@REQUEST_TIMEOUT
@REQUESTS_FORMATS
def deployments_request(deployment_name, version_name, data, timeout, format_):
    """Create a deployment request and retrieve the result.

    For structured input, specify the data as JSON formatted string. For example:
    `ubiops deployments request <my-deployment> -v <my-version> --data "{\"param1\": 1, \"param2\": \"two\"}"`
    """

    project_name = get_current_project(error=True)

    client = init_client()
    deployment = client.deployments_get(project_name=project_name, deployment_name=deployment_name)

    if deployment.input_type == STRUCTURED_TYPE:
        data = parse_json(data)

    response = client.deployment_requests_create(project_name=project_name, deployment_name=deployment_name,
                                                 version=version_name, data=data, timeout=timeout)
    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_requests_reference([response]))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline([response]))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_requests_reference([response]))


@commands.group("batch_requests", short_help="Manage your deployment batch requests")
def batch_requests():
    """Manage your deployment batch requests."""
    pass


@batch_requests.command("create", short_help="Create deployment batch request")
@DEPLOYMENT_NAME_ARGUMENT
@VERSION_NAME_OPTION
@REQUEST_DATA_MULTI
@REQUESTS_FORMATS
def batch_requests_create(deployment_name, version_name, data, format_):
    """Create a deployment batch request and retrieve request IDs to collect the results later.

    Multiple data inputs can be specified at ones by using the '--data' options multiple times:
    `ubiops deployments batch_requests create <my-deployment> -v <my-version> --data <input-1> --data <input-2> --data <input-3>`

    For structured input, specify each data input as JSON formatted string. For example:
    `ubiops deployments batch_requests create <my-deployment> -v <my-version> --data "{\"param1\": 1, \"param2\": \"two\"}"`
    """

    data = list(data)

    project_name = get_current_project(error=True)

    client = init_client()
    deployment = client.deployments_get(project_name=project_name, deployment_name=deployment_name)

    if deployment.input_type == STRUCTURED_TYPE:
        input_data = []
        for d in data:
            input_data.append(parse_json(d))
    else:
        input_data = data

    response = client.batch_deployment_requests_create(project_name=project_name, deployment_name=deployment_name,
                                                       version=version_name, data=input_data)
    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_requests_reference(response))


@batch_requests.command("get", short_help="Get deployment batch request")
@DEPLOYMENT_NAME_ARGUMENT
@VERSION_NAME_OPTION
@REQUEST_ID_MULTI
@REQUESTS_FORMATS
def batch_requests_get(deployment_name, version_name, request_id, format_):
    """Get the results of one or more deployment batch requests.

    Multiple request ids can be specified at ones by using the '-id' options multiple times:
    `ubiops deployments batch_requests get <my-deployment> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`
    """

    request_ids = list(request_id)

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.batch_deployment_requests_batch_get(
        project_name=project_name, deployment_name=deployment_name, version=version_name, data=request_ids
    )
    client.api_client.close()

    if format_ == 'reference':
        click.echo(format_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_requests_reference(response))


@batch_requests.command("list", short_help="List deployment batch requests")
@DEPLOYMENT_NAME_ARGUMENT
@VERSION_NAME_OPTION
@OFFSET
@REQUEST_LIMIT
@LIST_FORMATS
def batch_requests_list(deployment_name, version_name, offset, limit, format_):
    """List deployment batch requests."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.batch_deployment_requests_list(
        project_name=project_name, deployment_name=deployment_name, version=version_name, limit=limit, offset=offset
    )
    client.api_client.close()

    print_list(response, REQUEST_LIST_ITEMS, fmt=format_)
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more)")
