import click
import ubiops as api

from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import init_client, read_yaml, write_yaml, get_current_project, write_blob, import_export_zip_name


LIST_ITEMS = ['id', 'creation_date', 'status', 'size']
GET_ITEMS = ['id', 'creation_date', 'status', 'error_message', 'size']


@click.group(name="exports", short_help="Manage your exports")
def commands():
    """
    Manage your exports.
    """

    return


@commands.command(name="list", short_help="List exports")
@options.EXPORT_STATUS_FILTER
@options.LIST_FORMATS
def exports_list(status, format_):
    """
    List all your exports in your project.

    The `<status>` option can be used to filter on specific statuses.
    """

    project_name = get_current_project()
    if project_name:
        client = init_client()
        exports = client.exports_list(project_name=project_name, status=status)
        client.api_client.close()
        print_list(items=exports, attrs=LIST_ITEMS, sorting_col=1, sorting_reverse=True, fmt=format_)


@commands.command(name="get", short_help="Get details of an export")
@options.EXPORT_ID
@options.EXPORT_DETAILS_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
def exports_get(export_id, output_path, quiet, format_):
    """
    Get the details of an export.

    If you specify the `<output_path>` option, this location will be used to store the
    export details in a yaml file. You can either specify the `<output_path>` as file or
    directory. If the specified `<output_path>` is a directory, the settings will be
    stored in `export.yaml`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    export = client.exports_get(project_name=project_name, export_id=export_id)
    client.api_client.close()

    if output_path is not None:
        dictionary = format_yaml(
            item=export,
            required_front=['id', 'deployments', 'pipelines', 'environment_variables'],
            as_str=False
        )
        yaml_file = write_yaml(output_path, dictionary, default_file_name="export.yaml")
        if not quiet:
            click.echo(f"Export details are stored in: {yaml_file}")
    else:
        print_item(item=export, row_attrs=GET_ITEMS, fmt=format_)


@commands.command(name="create", short_help="Create an export")
@options.EXPORT_DETAILS_YAML_FILE
@options.CREATE_FORMATS
def exports_create(yaml_file, format_):
    """
    Create a new export.

    \b
    Define the export objects parameters using a yaml file.
    For example:
    ```
    deployments:
      deployment-1:
        versions:
          v1:
            environment_variables:
              deployment_version_env_var_1:
                include_value: True
              deployment_version_env_var_2:
                include_value: False
          v2: {}
        environment_variables:
           deployment_env_var:
             include_value: False
    pipelines:
      pipeline-1:
        versions:
          v1: {}
          v2: {}
    environment_variables:
      project_env_var:
        include_value: False
    ```
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)
    client = init_client()

    if 'deployments' in yaml_content:
        if not isinstance(yaml_content['deployments'], dict):
            raise UbiOpsException(
                "Deployments field should be a dictionary with deployment names as key and versions as value"
            )
        deployments = yaml_content['deployments']
    else:
        deployments = {}

    if 'pipelines' in yaml_content:
        if not isinstance(yaml_content['pipelines'], dict):
            raise UbiOpsException(
                "Pipelines field should be a dictionary with pipeline names as key and versions as value"
            )
        pipelines = yaml_content['pipelines']
    else:
        pipelines = {}

    if 'environment_variables' in yaml_content:
        if not isinstance(yaml_content['environment_variables'], dict):
            raise UbiOpsException(
                "Environment_variables field should be a dictionary with environment variable name as key and details "
                "of whether to include the variable value as value"
            )
        environment_variables = yaml_content['environment_variables']
    else:
        environment_variables = {}

    export = api.ExportCreate(
        deployments=deployments,
        pipelines=pipelines,
        environment_variables=environment_variables
    )
    response = client.exports_create(project_name=project_name, data=export)
    client.api_client.close()

    print_item(item=response, row_attrs=LIST_ITEMS, fmt=format_)


@commands.command(name="delete", short_help="Delete an export")
@options.EXPORT_ID
@options.ASSUME_YES
@options.QUIET
def exports_delete(export_id, assume_yes, quiet):
    """
    Delete an export.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete export <{export_id}> of project <{project_name}>?"
    ):
        client = init_client()
        client.exports_delete(project_name=project_name, export_id=export_id)
        client.api_client.close()

        if not quiet:
            click.echo("Export was successfully deleted")


@commands.command(name="download", short_help="Download an export")
@options.EXPORT_ID
@options.EXPORT_ZIP_OUTPUT
@options.QUIET
def exports_download(export_id, output_path, quiet):
    """
    Download an export.

    The `<output_path>` option will be used as output location of the zip file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the zip will be
    saved in `export_[export_id]_[datetime.now()].zip`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    with client.exports_download(project_name=project_name, export_id=export_id) as response:
        filename = import_export_zip_name(object_id=export_id, object_type='export')
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo(f"Export file stored in: {output_path}")
