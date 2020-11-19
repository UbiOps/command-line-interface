import ubiops as api
from pkg.utils import init_client, read_yaml, write_yaml, get_current_project
from pkg.src.helpers.helpers import set_version_defaults, update_deployment_file, VERSION_FIELDS,\
    set_dict_default, VERSION_FIELDS_RENAMED, get_label_filter
from pkg.src.helpers.formatting import print_list, print_item, format_yaml
from pkg.src.helpers.options import *


LIST_ITEMS = ['id', 'version', 'creation_date', 'status', 'labels']


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

    The <labels> option can be used to filter on specific labels.
    """

    label_filter = get_label_filter(labels)

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.versions_list(project_name=project_name, deployment_name=deployment_name, labels=label_filter)
    client.api_client.close()

    print_list(response, LIST_ITEMS, rename_cols={'version': 'version_name', **VERSION_FIELDS_RENAMED},
               sorting_col=1, fmt=format_)


@commands.command("get", short_help="Get the version of a deployment")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_ARGUMENT
@VERSION_YAML_OUTPUT
@QUIET
@GET_FORMATS
def versions_get(deployment_name, version_name, output_path, quiet, format_):
    """Get the version of a deployment.

    If you specify the <output_path> option, this location will be used to store the
    deployment version settings in a yaml file. You can either specify the <output_path>
    as file or directory. If the specified <output_path> is a directory, the settings
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
    language: python3.7
    memory_allocation: 2048
    minimum_instances: 0
    maximum_instances: 5
    maximum_idle_time: 300
    ```
    """

    project_name = get_current_project(error=True)

    # Show version details
    client = init_client()
    version = client.versions_get(project_name=project_name, deployment_name=deployment_name, version=version_name)
    client.api_client.close()

    if output_path is not None:
        # Store only reusable settings
        dictionary = format_yaml(version, required_front=['version', 'deployment', *VERSION_FIELDS],
                                 rename={'deployment': 'deployment_name', 'version': 'version_name',
                                         **VERSION_FIELDS_RENAMED}, as_str=False)
        yaml_file = write_yaml(output_path, dictionary, default_file_name="version.yaml")
        if not quiet:
            click.echo('Version file stored in: %s' % yaml_file)
    else:
        print_item(version, row_attrs=LIST_ITEMS, rename={'deployment': 'deployment_name', 'version': 'version_name',
                                                          **VERSION_FIELDS_RENAMED}, fmt=format_)


@commands.command("create", short_help="Create a version")
@DEPLOYMENT_NAME_OPTIONAL
@VERSION_NAME_OVERRULE
@LANGUAGE
@MEMORY_ALLOCATION
@MIN_INSTANCES
@MAX_INSTANCES
@MAX_IDLE_TIME
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
    language: python3.6
    memory_allocation: 256
    minimum_instances: 0
    maximum_instances: 1
    maximum_idle_time: 300
    ```

    Those parameters can also be provided as command options. If both a <yaml_file> is set and
    options are given, the options defined by <yaml_file> will be overwritten by the specified command options.
    The version name can either be passed as command argument or specified inside the yaml file using <version_name>.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=[])
    client = init_client()

    assert 'deployment_name' in yaml_content or deployment_name, 'Please, specify the deployment name in either ' \
                                                                 'the yaml file or as a command argument'
    assert 'version_name' in yaml_content or version_name, 'Please, specify the version name in either ' \
                                                           'the yaml file or as a command argument'

    kwargs = set_version_defaults(kwargs, yaml_content, None, extra_yaml_fields=['deployment_file'])

    deployment_name = set_dict_default(deployment_name, yaml_content, 'deployment_name')
    version_name = set_dict_default(version_name, yaml_content, 'version_name')

    version = api.VersionCreate(version=version_name, **{k: kwargs[k] for k in VERSION_FIELDS})

    response = client.versions_create(project_name=project_name, deployment_name=deployment_name, data=version)
    update_deployment_file(client, project_name, deployment_name, version_name, kwargs['deployment_file'])
    client.api_client.close()

    print_item(response, row_attrs=LIST_ITEMS, rename={'deployment': 'deployment_name', 'version': 'version_name',
                                                       **VERSION_FIELDS_RENAMED}, fmt=format_)


@commands.command("update", short_help="Update a version")
@DEPLOYMENT_NAME_OPTION
@VERSION_NAME_ARGUMENT
@VERSION_NAME_UPDATE
@DEPLOYMENT_FILE
@VERSION_YAML_FILE
@LANGUAGE
@MEMORY_ALLOCATION
@MIN_INSTANCES
@MAX_INSTANCES
@MAX_IDLE_TIME
@VERSION_LABELS
@VERSION_DESCRIPTION
@QUIET
def versions_update(deployment_name, version_name, yaml_file, new_name, quiet, **kwargs):
    """Update a version of a deployment.

    You may want to change some deployment options, like, programming <language> and
    <memory_allocation>. You can do this by either providing the options in a yaml file
    and passing the file path as <yaml_file>, or passing the options as command options.
    If both a <yaml_file> is set and options are given, the options defined by <yaml_file>
    will be overwritten by the specified command options.
    """

    project_name = get_current_project(error=True)

    client = init_client()

    yaml_content = read_yaml(yaml_file, required_fields=[])
    existing_version = client.versions_get(project_name=project_name, deployment_name=deployment_name,
                                           version=version_name)

    kwargs = set_version_defaults(kwargs, yaml_content, existing_version, extra_yaml_fields=['deployment_file'])

    new_version_name = version_name if new_name is None else new_name
    version = api.VersionCreate(version=new_version_name, **{k: kwargs[k] for k in VERSION_FIELDS})
    update_deployment_file(client, project_name, deployment_name, version_name, kwargs['deployment_file'])
    client.versions_update(project_name=project_name, deployment_name=deployment_name, version=version_name,
                           data=version)
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
        client.versions_delete(project_name=project_name, deployment_name=deployment_name, version=version_name)
        client.api_client.close()
        if not quiet:
            click.echo("Deployment version was successfully deleted")
