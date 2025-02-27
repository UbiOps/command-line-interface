import os
from time import sleep

import click
import ubiops as api

from ubiops_cli.constants import (
    STATUS_UNAVAILABLE,
    STRUCTURED_TYPE,
    DEFAULT_IGNORE_FILE,
    UPDATE_TIME,
    IMPLICIT_ENVIRONMENT_FILES,
)
from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.src.helpers.deployment_helpers import (
    define_deployment,
    define_deployment_version,
    set_default_scaling_parameters,
    update_deployment_file,
    update_existing_deployment_version,
    DEPLOYMENT_CREATE_FIELDS,
    DEPLOYMENT_UPDATE_FIELDS,
    DEPLOYMENT_DETAILS,
    DEPLOYMENT_DETAILS_OPTIONAL,
    DEPLOYMENT_FIELDS_RENAMED,
    DEPLOYMENT_VERSION_CREATE_FIELDS,
)
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers.formatting import (
    print_list,
    print_item,
    format_yaml,
    format_requests_reference,
    format_requests_oneline,
    format_json,
    parse_datetime,
    format_datetime,
)
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import (
    init_client,
    read_json,
    read_yaml,
    write_yaml,
    zip_dir,
    get_current_project,
    set_dict_default,
    write_blob,
    default_zip_name,
    parse_json,
)


LIST_ITEMS = ["last_updated", "name", "labels"]
REQUEST_LIST_ITEMS = ["id", "status", "success", "time_created"]


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
            required_front=DEPLOYMENT_DETAILS,
            optional=DEPLOYMENT_DETAILS_OPTIONAL,
            rename=DEPLOYMENT_FIELDS_RENAMED,
            as_str=False,
        )
        yaml_file = write_yaml(output_path, dictionary, default_file_name="deployment.yaml")
        if not quiet:
            click.echo(f"Deployment file is stored in: {yaml_file}")
    else:
        print_item(
            item=deployment,
            row_attrs=LIST_ITEMS,
            required_front=["id", *DEPLOYMENT_DETAILS],
            optional=DEPLOYMENT_DETAILS_OPTIONAL,
            required_end=["creation_date", "last_updated", "default_version"],
            rename=DEPLOYMENT_FIELDS_RENAMED,
            fmt=format_,
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
    deployment_supports_request_format: true
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

    Possible input/output types: [structured, plain]. Possible data_types: [int,
    string, double, bool, dict, file, array_string, array_int, array_double, array_file].
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=[])
    client = init_client()

    assert "deployment_name" in yaml_content or deployment_name, (
        "Please, specify the deployment name in either the " "yaml file or as a command argument"
    )

    kwargs = define_deployment(fields={"deployment_name": deployment_name}, yaml_content=yaml_content)

    deployment = api.DeploymentCreate(**{k: kwargs[k] for k in DEPLOYMENT_CREATE_FIELDS if k in kwargs})
    response = client.deployments_create(project_name=project_name, data=deployment)
    client.api_client.close()

    print_item(
        item=response,
        row_attrs=LIST_ITEMS,
        required_front=["id", *DEPLOYMENT_DETAILS],
        optional=DEPLOYMENT_DETAILS_OPTIONAL,
        required_end=["creation_date", "last_updated"],
        rename=DEPLOYMENT_FIELDS_RENAMED,
        fmt=format_,
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

    It is possible to define the updated parameter values using a yaml file. Or provide the `<new_name>` or
    `<default_version>` directly as command options. When both a yaml file and command options are given, the command
    options are prioritized over the yaml content.

    \b
    For example:
    ```
    deployment_name: new-name
    deployment_description: Deployment created via command line.
    deployment_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    deployment_supports_request_format: true
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
    default_version: v1
    ```
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)
    kwargs = define_deployment(
        fields={"deployment_name": new_name, "default_version": default_version},
        yaml_content=yaml_content,
        extra_yaml_fields=["default_version"],
    )

    deployment = api.DeploymentUpdate(
        **{k: kwargs[k] for k in DEPLOYMENT_UPDATE_FIELDS if kwargs.get(k, None) is not None}
    )

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
@options.DEPLOYMENT_ARCHIVE_OUTPUT
@options.IGNORE_FILE
@options.ASSUME_YES
@options.QUIET
def deployments_package(deployment_name, version_name, directory, output_path, ignore_file, assume_yes, quiet):
    """
    Package code to archive file which is ready to be deployed.

    Please, specify the code `<directory>` that should be deployed. The files in this directory will be zipped.
    Subdirectories and files that shouldn't be contained in the archive can be specified in an ignore file, which is by
    default '.ubiops-ignore'. The structure of this file is assumed to be equal to the well-known .gitignore file.

    Use the `<output_path>` option to specify the output location of the archive file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the archive will be saved as
    `[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use the `<assume_yes>` option to overwrite
    without confirmation if file specified in `<output_path>` already exists.
    """

    if not output_path:
        output_path = "."

    ignore_file = DEFAULT_IGNORE_FILE if ignore_file is None else ignore_file
    prefix = f"{deployment_name}_{version_name}" if deployment_name and version_name else deployment_name
    archive_path, _ = zip_dir(
        directory=directory, output_path=output_path, ignore_filename=ignore_file, prefix=prefix, force=assume_yes
    )
    if not quiet:
        click.echo(f"Created archive: {archive_path}")


@commands.command(name="upload", short_help="Upload a deployment package")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTION
@options.DEPLOYMENT_ARCHIVE_INPUT
@options.OVERWRITE
@options.PROGRESS_BAR
@options.QUIET
def deployments_upload(deployment_name, version_name, archive_path, overwrite, progress_bar, quiet):
    """
    Upload a deployment package archive file to a version of a deployment.

    Please, specify the deployment package `<archive_path>` that should be uploaded.
    Use the `<overwrite>` option to overwrite the deployment package on UbiOps if one already exists for this version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    current_version = client.deployment_versions_get(
        project_name=project_name, deployment_name=deployment_name, version=version_name
    )

    if overwrite or current_version.status == STATUS_UNAVAILABLE:
        client.revisions_file_upload(
            project_name=project_name,
            deployment_name=deployment_name,
            version=version_name,
            file=archive_path,
            _progress_bar=False if not archive_path else progress_bar,
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
@options.DEPLOYMENT_ARCHIVE_OUTPUT
@options.QUIET
def deployments_download(deployment_name, version_name, output_path, quiet):
    """
    Get the version of a deployment.

    The `<output_path>` option will be used as output location of the archive file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the archive will be
    saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`.
    """

    if not output_path:
        output_path = "."

    project_name = get_current_project(error=True)

    client = init_client()
    version = client.deployment_versions_get(
        project_name=project_name, deployment_name=deployment_name, version=version_name
    )
    if not version.active_revision:
        raise UbiOpsException("No active revision available for this deployment")

    with client.revisions_file_download(
        project_name=project_name,
        deployment_name=deployment_name,
        version=version_name,
        revision_id=version.active_revision,
    ) as response:
        prefix = f"{deployment_name}_{version_name}" if deployment_name and version_name else deployment_name
        filename = default_zip_name(prefix=prefix)
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo(f"Archive stored in: {output_path}")


# pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-statements
@commands.command(name="deploy", short_help="Deploy a new version of a deployment")
@options.DEPLOYMENT_NAME_OVERRULE
@options.VERSION_NAME_OPTIONAL
@options.PACKAGE_DIR
@options.DEPLOYMENT_FILE
@options.IGNORE_FILE
@options.DEPLOYMENT_ARCHIVE_OUTPUT
@options.VERSION_YAML_FILE
@options.ENVIRONMENT
@options.INSTANCE_TYPE
@options.INSTANCE_TYPE_GROUP_ID
@options.INSTANCE_TYPE_GROUP_NAME
@options.SCALING_STRATEGY
@options.MIN_INSTANCES
@options.MAX_INSTANCES
@options.INSTANCE_PROCESSES
@options.MAX_IDLE_TIME
@options.RETENTION_MODE
@options.RETENTION_TIME
@options.MAX_QUEUE_SIZE_EXPRESS
@options.MAX_QUEUE_SIZE_BATCH
@options.VERSION_STATIC_IP
@options.VERSION_PUBLIC_PORT
@options.VERSION_DEPLOYMENT_PORT
@options.VERSION_PORT_PROTOCOL
@options.VERSION_LABELS
@options.VERSION_DESCRIPTION
@options.OVERWRITE
@options.ASSUME_YES
@options.PROGRESS_BAR
@options.QUIET
def deployments_deploy(
    deployment_name,
    version_name,
    directory,
    output_path,
    yaml_file,
    overwrite,
    assume_yes,
    progress_bar,
    quiet,
    **kwargs,
):
    """
    Deploy a new version of a deployment.

    For deployments that support request format, you can specify the code `<directory>` that should be deployed. The
    files in this directory will be zipped and uploaded. Subdirectories and files that shouldn't be contained in the
    archive file can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this file
    is assumed to be equal to the well-known '.gitignore' file.
    It's also possible to skip `<directory>` and continue with an empty revision. In that case, we assume that your
    deployment code is part of your environment, e.g. custom docker image.

    If you want to store a local copy of the uploaded archive file, please use the `<output_path>` option.
    The `<output_path>` option will be used as output location of the archive file. If the `<output_path>` is a
    directory, the archive will be saved as `[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use
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
    instance_type_group_name: 2048 MB + 0.5 vCPU
    scaling_strategy: default
    minimum_instances: 0
    maximum_instances: 1
    instance_processes: 1
    maximum_idle_time: 300
    request_retention_mode: none
    request_retention_time: 604800
    maximum_queue_size_express: 100
    maximum_queue_size_batch: 100000
    static_ip: false
    ports:
    - public_port: 2222
      deployment_port: 2222
      protocol: tcp
    ```

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and options are given,
    the options defined by `<yaml_file>` will be overwritten by the specified command options. The deployment name can
    either be passed as command argument or specified inside the yaml file using `<deployment_name>`.

    The `ports` to open up for the deployment version can be provided as list of fields `public_port`, `deployment_port`
    and `protocol` inside the yaml file, or one port can be given via command options `--public_port`,
    `--deployment_port` and `--port_protocol`. Only one of the options (yaml or command options) can be used, not both.
    Use a yaml file with empty `ports` list and provide `--overwrite` command option to remove already existing opened
    ports.
    """

    if not output_path:
        store_archive = False
        output_path = "."
    else:
        store_archive = True

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=[])

    assert "deployment_name" in yaml_content or deployment_name, (
        "Please, specify the deployment name in either the " "yaml file or as a command argument"
    )
    assert "version_name" in yaml_content or version_name, (
        "Please, specify the version name in either the yaml " "file or as a command option"
    )

    deployment_name = set_dict_default(deployment_name, yaml_content, "deployment_name")
    version_name = set_dict_default(version_name, yaml_content, "version_name")

    # Convert command options for port forwarding to 'ports' list
    if "ports" in yaml_content and (kwargs.get("public_port", None) or kwargs.get("deployment_port", None)):
        raise AssertionError(
            "Please, specify the ports to open up either in the yaml file or as command options, not both"
        )
    if kwargs.get("public_port", None) or kwargs.get("deployment_port", None):
        if not (kwargs.get("public_port", None) and kwargs.get("deployment_port", None)):
            raise AssertionError("public_port and deployment_port should be provided together")
        yaml_content["ports"] = [
            {
                "public_port": kwargs.pop("public_port"),
                "deployment_port": kwargs.pop("deployment_port"),
                "protocol": kwargs.pop("port_protocol"),
            }
        ]

    client = init_client()
    deployment = client.deployments_get(project_name=project_name, deployment_name=deployment_name)

    existing_version = None
    if overwrite:
        try:
            existing_version = client.deployment_versions_get(
                project_name=project_name, deployment_name=deployment_name, version=version_name
            )
        except api.exceptions.ApiException:
            # Do nothing if version doesn't exist
            pass

    kwargs = define_deployment_version(kwargs, yaml_content, extra_yaml_fields=["deployment_file", "ignore_file"])
    kwargs["ignore_file"] = DEFAULT_IGNORE_FILE if kwargs["ignore_file"] is None else kwargs["ignore_file"]

    prefix = f"{deployment_name}_{version_name}" if deployment_name and version_name else deployment_name

    archive_path = None
    implicit_environment = False
    if deployment.supports_request_format and directory:
        archive_path, implicit_environment = zip_dir(
            directory=directory,
            output_path=output_path,
            ignore_filename=kwargs["ignore_file"],
            prefix=prefix,
            force=assume_yes,
        )

    try:
        has_uploaded_archives = False
        has_changed_fields = False

        if not (overwrite and existing_version):
            # Only use the fields given in keyword arguments when creating the deployment version
            version_fields = {}
            for k in DEPLOYMENT_VERSION_CREATE_FIELDS:
                if k in kwargs:
                    version_fields[k] = kwargs[k]

            version_fields = set_default_scaling_parameters(
                details=version_fields, supports_request_format=deployment.supports_request_format
            )

            version = api.DeploymentVersionCreate(version=version_name, **version_fields)
            client.deployment_versions_create(project_name=project_name, deployment_name=deployment_name, data=version)
        else:
            revisions = client.revisions_list(
                project_name=project_name, deployment_name=deployment_name, version=version_name
            )
            has_uploaded_archives = len(revisions) > 0

        if implicit_environment and not has_uploaded_archives and kwargs.get("environment", None) is not None:
            # We don't show a warning on re-uploads
            try:
                environment = client.environments_get(project_name=project_name, environment_name=kwargs["environment"])
                if environment.base_environment is not None:
                    # A custom environment is used
                    click.secho(
                        message="Warning: You are trying to upload a deployment file containing at least one"
                        f" environment file (e.g. {IMPLICIT_ENVIRONMENT_FILES[0]}). It's not possible to use"
                        " a custom environment in combination with an implicitly created environment.\nConsider"
                        f" adding the environment files to {kwargs['ignore_file']} so no implicit environment"
                        f" is created on revision file upload.",
                        fg="yellow",
                    )
            except api.exceptions.ApiException:
                pass

        if overwrite and existing_version:
            kwargs = set_default_scaling_parameters(
                details=kwargs, supports_request_format=deployment.supports_request_format, update=True
            )
            has_changed_fields = update_existing_deployment_version(
                client, project_name, deployment_name, version_name, existing_version, kwargs
            )

        has_changed_env_vars = update_deployment_file(
            client, project_name, deployment_name, version_name, kwargs["deployment_file"]
        )

        if has_uploaded_archives and (has_changed_fields or has_changed_env_vars):
            # Wait for changes being applied
            click.echo(f"Waiting for changes to take effect... This takes {UPDATE_TIME} seconds.")
            sleep(UPDATE_TIME)

        if deployment.supports_request_format:
            client.revisions_file_upload(
                project_name=project_name,
                deployment_name=deployment_name,
                version=version_name,
                file=archive_path,
                _progress_bar=False if not archive_path else progress_bar,
            )
        client.api_client.close()
    except Exception as e:
        if archive_path and os.path.isfile(archive_path) and not store_archive:
            os.remove(archive_path)
        client.api_client.close()
        raise e

    if archive_path and os.path.isfile(archive_path):
        if store_archive:
            if not quiet:
                click.echo(f"Created archive: {archive_path}")
        else:
            os.remove(archive_path)

    if not quiet:
        click.echo("Deployment was successfully deployed")


@commands.group(name="requests", short_help="Manage your deployment requests")
def requests():
    """
    Manage your deployment requests.
    """

    return


# pylint: disable=too-many-arguments,too-many-branches
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

    params = {"project_name": project_name, "deployment_name": deployment_name}
    if timeout is not None:
        params["timeout"] = timeout
    if version_name is not None:
        params["version"] = version_name

    if batch:
        if version_name is not None:
            response = getattr(client, "batch_deployment_version_requests_create")(**params, data=input_data)
        else:
            response = getattr(client, "batch_deployment_requests_create")(**params, data=input_data)

    else:
        # We don't support list input for plain type, create the requests one by one
        if deployment.input_type == STRUCTURED_TYPE:
            input_data = [input_data]

        response = []
        for item in input_data:
            for streaming_update in api.utils.stream_deployment_request(
                client=client.api_client, data=item, full_response=True, **params
            ):
                if isinstance(streaming_update, str):
                    # Immediately show streaming updates
                    click.echo(streaming_update)
                else:
                    # Keep the final result to display in the correct format
                    response.append(streaming_update)

    client.api_client.close()

    if format_ == "reference":
        click.echo(format_requests_reference(response))
    elif format_ == "oneline":
        click.echo(format_requests_oneline(response))
    elif format_ == "json":
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

    if format_ == "reference":
        click.echo(format_requests_reference(response))
    elif format_ == "oneline":
        click.echo(format_requests_oneline(response))
    elif format_ == "json":
        click.echo(format_json(response, skip_attributes=["success"]))
    else:
        click.echo(format_requests_reference(response))


@requests.command(name="list", short_help="List deployment requests")
@options.DEPLOYMENT_NAME_ARGUMENT
@options.VERSION_NAME_OPTIONAL
@options.OFFSET
@options.REQUEST_LIMIT
@options.REQUEST_FILTER_DEPLOYMENT_STATUS
@options.REQUEST_FILTER_START_DATE
@options.REQUEST_FILTER_END_DATE
@options.REQUEST_FILTER_SEARCH_ID
@options.LIST_FORMATS
def requests_list(deployment_name, version_name, limit, format_, **kwargs):
    """
    List stored deployment requests.
    Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

    Use the version option to list the requests for a specific deployment version.
    If not specified, the requests are listed for the default version.
    """

    project_name = get_current_project(error=True)

    if "start_date" in kwargs and kwargs["start_date"]:
        try:
            kwargs["start_date"] = format_datetime(parse_datetime(kwargs["start_date"]), fmt="%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise UbiOpsException(
                "Failed to parse start_date. Please use iso-format, for example, '2020-01-01T00:00:00.000000Z'"
            )

    if "end_date" in kwargs and kwargs["end_date"]:
        try:
            kwargs["end_date"] = format_datetime(parse_datetime(kwargs["end_date"]), fmt="%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise UbiOpsException(
                "Failed to parse end_date. Please use iso-format, for example, '2020-01-01T00:00:00.000000Z'"
            )

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
