import click
import ubiops as api

from ubiops_cli.utils import init_client, read_yaml, write_yaml, get_current_project, set_dict_default
from ubiops_cli.src.helpers.pipeline_helpers import rename_pipeline_object_reference_version, \
    set_pipeline_version_defaults, PIPELINE_VERSION_FIELDS, PIPELINE_VERSION_FIELDS_RENAMED, \
    PIPELINE_VERSION_RESPONSE_FILE, PIPELINE_VERSION_RESPONSE
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml
from ubiops_cli.src.helpers import options


LIST_ITEMS = ['last_updated', 'version', 'labels']


@click.group(name=["pipeline_versions", "pversions"], short_help="Manage your pipeline versions")
def commands():
    """
    Manage your pipeline versions.
    """

    return


@commands.command(name="list", short_help="List the pipeline versions")
@options.PIPELINE_NAME_OPTION
@options.LABELS_FILTER
@options.LIST_FORMATS
def pipeline_versions_list(pipeline_name, labels, format_):
    """
    List the versions of a pipeline.

    The `<labels>` option can be used to filter on specific labels.
    """

    label_filter = get_label_filter(labels)

    project_name = get_current_project(error=True)

    client = init_client()
    default = client.pipelines_get(
        project_name=project_name, pipeline_name=pipeline_name
    ).default_version
    response = client.pipeline_versions_list(
        project_name=project_name, pipeline_name=pipeline_name, labels=label_filter
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
        rename_cols={'version': 'version_name', **PIPELINE_VERSION_FIELDS_RENAMED},
        sorting_col=0,
        fmt=format_
    )


@commands.command(name="get", short_help="Get the version of a pipeline")
@options.PIPELINE_NAME_OPTION
@options.VERSION_NAME_ARGUMENT
@options.VERSION_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
def pipeline_versions_get(pipeline_name, version_name, output_path, quiet, format_):
    """
    Get the pipeline version structure: input_type, version, objects and connections between the objects (attachments).

    If you specify the `<output_path>` option, this location will be used to store the
    pipeline version settings in a yaml file. You can either specify the `<output_path>`
    as file or directory. If the specified `<output_path>` is a directory, the settings
    will be stored in `version.yaml`.

    \b
    Example of yaml content:
    ```
    pipeline_name: my-pipeline-name
    input_type: structured
    input_fields:
      - name: my-pipeline-param1
        data_type: int
    output_type: structured
    output_fields:
      - name: my-pipeline-output1
        data_type: int
    version_name: my-version-name
    version_description: Version created via command line.
    version_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    request_retention_mode: none
    request_retention_time: 604800
    objects:
      - name: object1
        reference_name: my-deployment-name
        reference_type: deployment
        reference_version: my-deployment-version
    attachments:
      - destination_name: object1
        sources:
          - source_name: pipeline_start
            mapping:
              - source_field_name: my-pipeline-param1
                destination_field_name: my-deployment-param1
    ```
    """

    project_name = get_current_project(error=True)

    # Get pipeline version structure - pipeline, objects and attachments details
    client = init_client()
    version = client.pipeline_versions_get(project_name=project_name, pipeline_name=pipeline_name, version=version_name)
    pipeline = client.pipelines_get(project_name=project_name, pipeline_name=pipeline_name)
    client.api_client.close()

    setattr(version, 'input_type', pipeline.input_type)
    setattr(version, 'input_fields', pipeline.input_fields)
    setattr(version, 'output_type', pipeline.output_type)
    setattr(version, 'output_fields', pipeline.output_fields)

    if output_path is not None:
        # Store only reusable settings
        dictionary = format_yaml(
            item=version,
            **PIPELINE_VERSION_RESPONSE_FILE,
            as_str=False
        )

        yaml_file = write_yaml(output_path, dictionary, default_file_name="pipeline_version.yaml")

        if not quiet:
            click.echo(f"Pipeline version file stored in: {yaml_file}")

    else:
        print_item(
            item=version,
            row_attrs=LIST_ITEMS,
            **PIPELINE_VERSION_RESPONSE,
            fmt=format_
        )


@commands.command(name="create", short_help="Create a pipeline version")
@options.PIPELINE_NAME_OPTIONAL
@options.VERSION_NAME_OVERRULE
@options.VERSION_LABELS
@options.VERSION_DESCRIPTION
@options.RETENTION_MODE
@options.RETENTION_TIME
@options.VERSION_YAML_FILE
@options.CREATE_FORMATS
def pipeline_versions_create(pipeline_name, version_name, yaml_file, format_, **kwargs):
    """
    Create a version of a pipeline.

    \b
    It is possible to define the parameters using a yaml file.
    For example:
    ```
    pipeline_name: my-pipeline-name
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
        reference_type: deployment
        reference_version: my-deployment-version
    attachments:
      - destination_name: object1
        sources:
          - source_name: pipeline_start
            mapping:
              - source_field_name: my-pipeline-param1
                destination_field_name: my-deployment-param1
    ```

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
    options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
    The version name can either be passed as command argument or specified inside the yaml file using `<version_name>`.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=[])
    client = init_client()

    assert 'pipeline_name' in yaml_content or pipeline_name, \
        'Please, specify the pipeline name in either the yaml file or as a command argument'

    assert 'version_name' in yaml_content or version_name, \
        'Please, specify the version name in either the yaml file or as a command argument'

    pipeline_name = set_dict_default(pipeline_name, yaml_content, 'pipeline_name')
    version_name = set_dict_default(version_name, yaml_content, 'version_name')

    # Define the pipeline version
    kwargs = set_pipeline_version_defaults(kwargs, yaml_content, None)

    # Rename objects reference version
    kwargs = rename_pipeline_object_reference_version(content=kwargs)

    version = api.PipelineVersionCreate(version=version_name, **{k: kwargs[k] for k in PIPELINE_VERSION_FIELDS})
    response = client.pipeline_versions_create(project_name=project_name, pipeline_name=pipeline_name, data=version)
    client.api_client.close()

    print_item(
        item=response,
        row_attrs=LIST_ITEMS,
        **PIPELINE_VERSION_RESPONSE,
        fmt=format_
    )


@commands.command(name="update", short_help="Update a pipeline version")
@options.PIPELINE_NAME_OPTION
@options.VERSION_NAME_ARGUMENT
@options.VERSION_NAME_UPDATE
@options.VERSION_LABELS
@options.VERSION_DESCRIPTION
@options.RETENTION_MODE
@options.RETENTION_TIME
@options.VERSION_YAML_FILE
@options.QUIET
def pipeline_versions_update(pipeline_name, version_name, yaml_file, new_name, quiet, **kwargs):
    """
    Update a version of a pipeline.

    \b
    It is possible to define the parameters using a yaml file.
    For example:
    ```
    version_description: Version created via command line.
    version_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    request_retention_mode: none
    request_retention_time: 604800
    objects:
      - name: object1
        reference_name: my-deployment-name
        reference_type: deployment
        reference_version: my-deployment-version
    attachments:
      - destination_name: object1
        sources:
          - source_name: pipeline_start
            mapping:
              - source_field_name: my-pipeline-param1
                destination_field_name: my-deployment-param1
    ```

    You can update version parameters by either providing the options in a yaml file
    and passing the file path as `<yaml_file>`, or passing the options as command options.
    If both a `<yaml_file>` is set and options are given, the options defined by `<yaml_file>`
    will be overwritten by the specified command options.
    """

    project_name = get_current_project(error=True)

    client = init_client()

    yaml_content = read_yaml(yaml_file, required_fields=[])
    existing_version = client.pipeline_versions_get(
        project_name=project_name, pipeline_name=pipeline_name, version=version_name
    )

    # Define the pipeline version
    kwargs = set_pipeline_version_defaults(kwargs, yaml_content, existing_version)

    # Rename objects reference version
    kwargs = rename_pipeline_object_reference_version(content=kwargs)

    version_data = api.PipelineVersionUpdate(**{'version': new_name, **{k: kwargs[k] for k in PIPELINE_VERSION_FIELDS}})
    client.pipeline_versions_update(
        project_name=project_name,
        pipeline_name=pipeline_name,
        version=version_name,
        data=version_data
    )
    client.api_client.close()

    if not quiet:
        click.echo("Pipeline version was successfully updated")


@commands.command(name="delete", short_help="Delete a pipeline version")
@options.PIPELINE_NAME_OPTION
@options.VERSION_NAME_ARGUMENT
@options.ASSUME_YES
@options.QUIET
def pipeline_versions_delete(pipeline_name, version_name, assume_yes, quiet):
    """
    Delete a version of a pipeline.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete pipeline version <{version_name}> of pipeline <{pipeline_name}> "
        f"in project <{project_name}>?"
    ):
        client = init_client()
        client.pipeline_versions_delete(project_name=project_name, pipeline_name=pipeline_name, version=version_name)
        client.api_client.close()

        if not quiet:
            click.echo("Pipeline version was successfully deleted")
