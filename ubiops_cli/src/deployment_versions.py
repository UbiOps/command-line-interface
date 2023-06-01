import ubiops as api

from ubiops_cli.src.helpers.deployment_helpers import define_deployment_version, update_deployment_file, \
    DEPLOYMENT_VERSION_CREATE_FIELDS, DEPLOYMENT_VERSION_GET_FIELDS, DEPLOYMENT_VERSION_FIELDS_UPDATE, \
    DEPLOYMENT_VERSION_FIELDS_RENAMED
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers.wait_for import wait_for
from ubiops_cli.src.helpers.options import *
from ubiops_cli.utils import init_client, read_yaml, write_yaml, get_current_project, set_dict_default

LIST_ITEMS = ['last_updated', 'version', 'status', 'labels']


@click.group(["deployment_versions", "versions"], short_help="Manage your deployment versions")
def commands():
    """Manage your deployment versions."""
    pass


@commands.command("list", short_help="List the versions")
@DEPLOYMENT_NAME_OPTION
@LABELS_FILTER
@LIST_FORMATS
def versions_list(deployment_name, labels, format_):
    """
    List the versions of a deployment.

    The `<labels>` option can be used to filter on specific labels.
    """

    label_filter = get_label_filter(labels)

    project_name = get_current_project(error=True)

    client = init_client()
    default = client.deployments_get(
        project_name=project_name, deployment_name=deployment_name
    ).default_version
    response = client.deployment_versions_list(
        project_name=project_name, deployment_name=deployment_name, labels=label_filter
    )
    client.api_client.close()

    if format_ == 'table':
        # Add [DEFAULT] to default version
        for i in response:
            if default and hasattr(i, 'version') and i.version == default:
                i.version = f"{i.version} {click.style('[DEFAULT]', fg='yellow')}"

    print_list(
        items=response,
        attrs=LIST_ITEMS,
        rename_cols={'version': 'version_name', **DEPLOYMENT_VERSION_FIELDS_RENAMED},
        sorting_col=0,
        fmt=format_
    )


@commands.command("get", short_help="Get the version of a deployment")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_ARGUMENT
@VERSION_YAML_OUTPUT
@QUIET
@GET_FORMATS
def versions_get(deployment_name, version_name, output_path, quiet, format_):
    """Get the version of a deployment.

    If you specify the `<output_path>` option, this location will be used to store the
    deployment version settings in a yaml file. You can either specify the `<output_path>`
    as file or directory. If the specified `<output_path>` is a directory, the settings
    will be stored in `version.yaml`.

    \b
    Example of yaml content:
    ```
    deployment_name: my-deployment
    version_name: my-version
    version_description: Version created via command line.
    version_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    environment: python3-8
    instance_type: 2048mb
    minimum_instances: 0
    maximum_instances: 5
    maximum_idle_time: 300
    request_retention_mode: none
    request_retention_time: 604800
    maximum_queue_size_express: 100
    maximum_queue_size_batch: 100000
    has_request_method: true
    has_requests_method: false
    static_ip: false
    ```
    """

    project_name = get_current_project(error=True)

    # Show version details
    client = init_client()
    version = client.deployment_versions_get(
        project_name=project_name, deployment_name=deployment_name, version=version_name
    )
    client.api_client.close()

    if output_path is not None:
        # Store only reusable settings
        dictionary = format_yaml(
            item=version,
            required_front=['version', 'deployment', *DEPLOYMENT_VERSION_GET_FIELDS],
            rename={'deployment': 'deployment_name', 'version': 'version_name', **DEPLOYMENT_VERSION_FIELDS_RENAMED},
            as_str=False
        )
        yaml_file = write_yaml(output_path, dictionary, default_file_name="version.yaml")
        if not quiet:
            click.echo('Version file stored in: %s' % yaml_file)
    else:
        print_item(
            item=version,
            row_attrs=LIST_ITEMS,
            rename={'deployment': 'deployment_name', 'version': 'version_name', **DEPLOYMENT_VERSION_FIELDS_RENAMED},
            fmt=format_
        )


@commands.command("create", short_help="Create a version")
@DEPLOYMENT_NAME_OPTIONAL
@VERSION_NAME_OVERRULE
@LANGUAGE
@ENVIRONMENT
@INSTANCE_TYPE
@MIN_INSTANCES
@MAX_INSTANCES
@MAX_IDLE_TIME
@DEPLOYMENT_MODE_DEPRECATED
@RETENTION_MODE
@RETENTION_TIME
@MAX_QUEUE_SIZE_EXPRESS
@MAX_QUEUE_SIZE_BATCH
@VERSION_STATIC_IP
@VERSION_LABELS
@VERSION_DESCRIPTION
@VERSION_YAML_FILE
@DEPLOYMENT_FILE
@CREATE_FORMATS
def versions_create(deployment_name, version_name, yaml_file, format_, **kwargs):
    """Create a version of a deployment.

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

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
    options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
    The version name can either be passed as command argument or specified inside the yaml file using `<version_name>`.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=[])
    client = init_client()

    assert 'deployment_name' in yaml_content or deployment_name, 'Please, specify the deployment name in either ' \
                                                                 'the yaml file or as a command argument'
    assert 'version_name' in yaml_content or version_name, 'Please, specify the version name in either ' \
                                                           'the yaml file or as a command argument'

    if format_ != 'json' and ('deployment_mode' in yaml_content or kwargs['deployment_mode']):
        click.secho(
            "Deprecation warning: 'deployment_mode' is deprecated. From now on, both direct and batch requests can be "
            "made to the same deployment version.", fg='red'
        )

    if format_ != 'json' and ('language' in yaml_content or kwargs['language']):
        click.secho("Deprecation warning: 'language' is deprecated. Use 'environment' instead.", fg='red')

    kwargs = define_deployment_version(kwargs, yaml_content, extra_yaml_fields=['deployment_file'])

    deployment_name = set_dict_default(deployment_name, yaml_content, 'deployment_name')
    version_name = set_dict_default(version_name, yaml_content, 'version_name')

    version = api.DeploymentVersionCreate(
        version=version_name, **{k: kwargs[k] for k in DEPLOYMENT_VERSION_CREATE_FIELDS}
    )
    response = client.deployment_versions_create(
        project_name=project_name, deployment_name=deployment_name, data=version
    )

    update_deployment_file(client, project_name, deployment_name, version_name, kwargs['deployment_file'])
    client.api_client.close()

    print_item(
        item=response,
        row_attrs=LIST_ITEMS,
        rename={'deployment': 'deployment_name', 'version': 'version_name', **DEPLOYMENT_VERSION_FIELDS_RENAMED},
        fmt=format_
    )


@commands.command("update", short_help="Update a version")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_ARGUMENT
@VERSION_NAME_UPDATE
@DEPLOYMENT_FILE
@VERSION_YAML_FILE
@ENVIRONMENT
@INSTANCE_TYPE
@MIN_INSTANCES
@MAX_INSTANCES
@MAX_IDLE_TIME
@RETENTION_MODE
@RETENTION_TIME
@MAX_QUEUE_SIZE_EXPRESS
@MAX_QUEUE_SIZE_BATCH
@VERSION_STATIC_IP
@VERSION_LABELS
@VERSION_DESCRIPTION
@QUIET
def versions_update(deployment_name, version_name, yaml_file, new_name, quiet, **kwargs):
    """Update a version of a deployment.

    \b
    It is possible to define the parameters using a yaml file.
    For example:
    ```
    version_description: Version created via command line.
    version_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
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

    You may want to change some deployment options, like, `<maximum_instances>` and
    `<instance_Type>`. You can do this by either providing the options in a yaml file
    and passing the file path as `<yaml_file>`, or passing the options as command options.
    If both a `<yaml_file>` is set and options are given, the options defined by `<yaml_file>`
    will be overwritten by the specified command options.
    """

    project_name = get_current_project(error=True)

    client = init_client()

    yaml_content = read_yaml(yaml_file, required_fields=[])

    kwargs['version_name'] = new_name
    kwargs = define_deployment_version(kwargs, yaml_content, extra_yaml_fields=['deployment_file'])

    version = api.DeploymentVersionUpdate(
        **{k: kwargs[k] for k in DEPLOYMENT_VERSION_FIELDS_UPDATE if kwargs[k] is not None}
    )
    client.deployment_versions_update(
        project_name=project_name, deployment_name=deployment_name, version=version_name, data=version
    )
    update_deployment_file(client, project_name, deployment_name, version_name, kwargs['deployment_file'])
    client.api_client.close()

    if not quiet:
        click.echo("Deployment version was successfully updated")


@commands.command("delete", short_help="Delete a version")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_ARGUMENT
@ASSUME_YES
@QUIET
def versions_delete(deployment_name, version_name, assume_yes, quiet):
    """Delete a version of a deployment."""

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm("Are you sure you want to delete deployment version <%s> of deployment <%s> in"
                                   " project <%s>?" % (version_name, deployment_name, project_name)):
        client = init_client()
        client.deployment_versions_delete(
            project_name=project_name, deployment_name=deployment_name, version=version_name
        )
        client.api_client.close()
        if not quiet:
            click.echo("Deployment version was successfully deleted")


@commands.command("wait", short_help="Wait for a deployment version to be ready")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_ARGUMENT
@REVISION_ID_OPTIONAL
@TIMEOUT_OPTION
@QUIET
def versions_wait(deployment_name, version_name, revision_id, timeout, quiet):
    """
    Wait for a deployment version to be ready.

    To wait for a specific revision of the version, pass `--revision_id`:
    `ubiops versions wait v1 -d deployment-1 --revision_id=ced676ab-423b-4469-97e7-e5179515affb`
    """

    project_name = get_current_project(error=True)

    client = init_client()
    wait_for(
        api.utils.wait_for.wait_for_deployment_version,
        client=client.api_client,
        project_name=project_name,
        deployment_name=deployment_name,
        version=version_name,
        revision_id=revision_id,
        timeout=timeout,
        quiet=quiet
    )
    client.api_client.close()
