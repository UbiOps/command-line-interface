import click
import ubiops as api

from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.utils import init_client, read_yaml, write_yaml, get_current_project, write_blob, import_export_zip_name
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml
from ubiops_cli.src.helpers import options


LIST_ITEMS = ['id', 'creation_date', 'status', 'size']
GET_ITEMS = ['id', 'creation_date', 'status', 'error_message', 'size']


@click.group(name="imports", short_help="Manage your imports")
def commands():
    """
    Manage your imports.
    """

    return


@commands.command(name="list", short_help="List imports")
@options.IMPORT_STATUS_FILTER
@options.LIST_FORMATS
def imports_list(status, format_):
    """
    List all your imports in your project.

    The `<status>` option can be used to filter on specific statuses.
    """

    project_name = get_current_project()
    if project_name:
        client = init_client()
        imports = client.imports_list(project_name=project_name, status=status)
        client.api_client.close()
        print_list(items=imports, attrs=LIST_ITEMS, sorting_col=1, sorting_reverse=True, fmt=format_)


@commands.command(name="get", short_help="Get details of an import")
@options.IMPORT_ID
@options.IMPORT_DETAILS_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
def imports_get(import_id, output_path, quiet, format_):
    """
    Get the details of an import.

    If you specify the `<output_path>` option, this location will be used to store the
    import details in a yaml file. You can either specify the `<output_path>` as file or
    directory. If the specified `<output_path>` is a directory, the settings will be
    stored in `import.yaml`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    _import = client.imports_get(project_name=project_name, import_id=import_id)
    client.api_client.close()

    if output_path is not None:
        dictionary = format_yaml(
            item=_import,
            required_front=['deployments', 'pipelines', 'environment_variables'],
            as_str=False
        )
        yaml_file = write_yaml(output_path, dictionary, default_file_name="import.yaml")
        if not quiet:
            click.echo(f"Import details are stored in: {yaml_file}")
    else:
        print_item(item=_import, row_attrs=GET_ITEMS, fmt=format_)


@commands.command(name="create", short_help="Create an import")
@options.IMPORT_ZIP_FILE
@options.IMPORT_SKIP_CONFIRMATION
@options.PROGRESS_BAR
@options.CREATE_FORMATS
def imports_create(zip_path, skip_confirmation, progress_bar, format_):
    """
    Create a new import by uploading a ZIP.

    Please, specify the import file `<zip_path>` that should be uploaded.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    _import = client.imports_create(
        project_name=project_name, file=zip_path, skip_confirmation=skip_confirmation, _progress_bar=progress_bar
    )
    client.api_client.close()

    print_item(_import, row_attrs=LIST_ITEMS, fmt=format_)


@commands.command(name="confirm", short_help="Confirm an import")
@options.IMPORT_ID
@options.IMPORT_CONFIRM_YAML_FILE
@options.CREATE_FORMATS
def imports_confirm(import_id, yaml_file, format_):
    """
    Confirm (and update) an import by selecting the objects in the import.

    \b
    Define the import object selection using a yaml file.
    For example:
    ```
    deployments:
      deployment-1:
        description: My deployment
        labels:
          my-key-1: my-label-1
          my-key-2: my-label-2
        input_type: structured
        output_type: structured
        input_fields:
          - name: input
            data_type: int
        output_fields:
          - name: output
            data_type: int
        default_version: v1
        versions:
          v1:
            zip: "deployments/deployment_deployment-1/versions/deployment_deployment-1_version_v1.zip"
            description:
            environment: python3-8
            maximum_idle_time: 300
            minimum_instances: 0
            maximum_instances: 5
            instance_type: 512mb
            request_retention_mode: full
            request_retention_time: 604800
            environment_variables:
              deployment_version_env_var_1:
                value: env_var_value_1
                secret: True
              deployment_version_env_var_2:
                value: env_var_value_2
                secret: False
          v2: {}
    pipelines:
      pipeline-1:
        description: My pipeline
        labels:
          my-key-1: my-label-1
          my-key-2: my-label-2
        input_type: structured
        output_type: structured
        input_fields:
          - name: input
            data_type: int
        output_fields:
          - name: output
            data_type: int
        default_version: v1
        versions:
          v1:
            description:
            labels:
            request_retention_mode: full
            request_retention_time: 604800
            objects:
              - name: obj-1
                reference_name: deployment-1
                reference_type: deployment
                reference_version: v1
            attachments:
              - sources:
                - mapping:
                  - source_field_name: input
                    destination_field_name: input
                  source_name: pipeline_start
                destination_name: obj-1
              - sources:
                - mapping:
                  - source_field_name: input
                    destination_field_name: output
                  source_name: obj-1
                destination_name: pipeline_end
          v2: {}
    ```
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)
    client = init_client()

    if 'deployments' in yaml_content:
        if not isinstance(yaml_content['deployments'], dict):
            raise UbiOpsException(
                "Deployments field should be a dictionary with deployment names as key and deployment and version "
                "details as value"
            )
        deployments = yaml_content['deployments']
    else:
        deployments = {}

    if 'pipelines' in yaml_content:
        if not isinstance(yaml_content['pipelines'], dict):
            raise UbiOpsException(
                "Pipelines field should be a dictionary with pipelines names as key and pipeline and version "
                "details as value"
            )
        pipelines = yaml_content['pipelines']
    else:
        pipelines = {}

    if 'environment_variables' in yaml_content:
        if not isinstance(yaml_content['environment_variables'], dict):
            raise UbiOpsException(
                "Environment_variables field should be a dictionary with environment variable name as key and variable "
                "details as value"
            )
        environment_variables = yaml_content['environment_variables']
    else:
        environment_variables = {}

    import_update_data = api.ImportUpdate(
        deployments=deployments,
        pipelines=pipelines,
        environment_variables=environment_variables
    )
    response = client.imports_update(project_name=project_name, import_id=import_id, data=import_update_data)
    client.api_client.close()

    print_item(item=response, row_attrs=GET_ITEMS, fmt=format_)


@commands.command(name="delete", short_help="Delete an import")
@options.IMPORT_ID
@options.ASSUME_YES
@options.QUIET
def imports_delete(import_id, assume_yes, quiet):
    """
    Delete an import.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete import <{import_id}> of project <{project_name}>?"
    ):
        client = init_client()
        client.imports_delete(project_name=project_name, import_id=import_id)
        client.api_client.close()

        if not quiet:
            click.echo("Import was successfully deleted")


@commands.command(name="download", short_help="Download an import")
@options.IMPORT_ID
@options.IMPORT_ZIP_OUTPUT
@options.QUIET
def imports_download(import_id, output_path, quiet):
    """
    Download an import.

    The `<output_path>` option will be used as output location of the zip file. If not specified,
    the current directory will be used. If the `<output_path>` is a directory, the zip will be
    saved in `import_[import_id]_[datetime.now()].zip`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    with client.imports_download(project_name=project_name, import_id=import_id) as response:
        filename = import_export_zip_name(object_id=import_id, object_type='import')
        output_path = write_blob(response.read(), output_path, filename)
    client.api_client.close()

    if not quiet:
        click.echo(f"Import file stored in: {output_path}")
