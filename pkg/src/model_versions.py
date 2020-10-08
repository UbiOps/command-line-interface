import ubiops as api
from pkg.utils import init_client, read_yaml, write_yaml, get_current_project
from pkg.src.helpers.helpers import set_version_defaults, update_model_file, MODEL_VERSION_FIELDS, set_dict_default
from pkg.src.helpers.formatting import print_list, print_item, format_yaml
from pkg.src.helpers.options import *


LIST_ITEMS = ['id', 'version', 'creation_date', 'status']


@click.group("model_versions")
def commands():
    """Manage your model versions."""
    pass


@commands.command("list")
@MODEL_NAME_OPTION
@LIST_FORMATS
def versions_list(model_name, format_):
    """List the versions of a model."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.model_versions_list(project_name=project_name, model_name=model_name)
    print_list(response, LIST_ITEMS, rename_cols={'version': 'version_name'}, sorting_col=1, fmt=format_)


@commands.command("get")
@MODEL_NAME_OPTION
@VERSION_NAME_ARGUMENT
@VERSION_YAML_OUTPUT
@QUIET
@GET_FORMATS
def versions_get(model_name, version_name, output_path, quiet, format_):
    """Get the version of a model.

    If you specify the <output_path> option, this location will be used to store the
    model version settings in a yaml file. You can either specify the <output_path> as file or
    directory. If the specified <output_path> is a directory, the settings will be
    stored in `version.yaml`.

    \b
    Example of yaml content:
    ```
    version_name: my-version
    model_name: my-model
    language: python3.7
    memory_allocation: 2048
    minimum_instances: 0
    maximum_instances: 5
    maximum_idle_time: 300
    ```
    """

    project_name = get_current_project(error=True)

    client = init_client()

    # Show version details
    version = client.model_versions_get(project_name=project_name,
                                        model_name=model_name,
                                        version=version_name)

    if output_path is not None:
        # Store only reusable settings
        dictionary = format_yaml(version, required_front=['version', 'model', *MODEL_VERSION_FIELDS],
                                 rename={'model': 'model_name', 'version': 'version_name'}, as_str=False)
        yaml_file = write_yaml(output_path, dictionary, default_file_name="version.yaml")
        if not quiet:
            click.echo('Version file stored in: %s' % yaml_file)
    else:
        print_item(version, row_attrs=LIST_ITEMS, rename={'model': 'model_name', 'version': 'version_name'},
                   fmt=format_)


@commands.command("create")
@MODEL_NAME_OPTIONAL
@VERSION_NAME_OVERRULE
@LANGUAGE
@MEMORY_ALLOCATION
@MIN_INSTANCES
@MAX_INSTANCES
@MAX_IDLE_TIME
@VERSION_YAML_FILE
@MODEL_FILE
@CREATE_FORMATS
def versions_create(model_name, version_name, yaml_file, format_, **kwargs):
    """Create a version of a model.

    \b
    It is possible to define the parameters using a yaml file.
    For example:
    ```
    version_name: my-model-version
    model_name: my-model-name
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

    yaml_content = read_yaml(yaml_file, required_fields=[]) if yaml_file else None
    client = init_client()

    assert 'model_name' in yaml_content or model_name, 'Please, specify the model name in either the yaml ' \
                                                       'file or as a command argument.'
    assert 'version_name' in yaml_content or version_name, 'Please, specify the version name in either the yaml ' \
                                                           'file or as a command argument.'

    kwargs = set_version_defaults(kwargs, yaml_content, None, extra_yaml_fields=['model_file'])

    model_name = set_dict_default(model_name, yaml_content, 'model_name')
    version_name = set_dict_default(version_name, yaml_content, 'version_name')

    version = api.ModelVersionCreate(version=version_name, **{k: kwargs[k] for k in MODEL_VERSION_FIELDS})

    response = client.model_versions_create(project_name=project_name, model_name=model_name, data=version)
    update_model_file(client, project_name, model_name, version_name, kwargs['model_file'])

    print_item(response, row_attrs=LIST_ITEMS, rename={'model': 'model_name', 'version': 'version_name'}, fmt=format_)


@commands.command("update")
@MODEL_NAME_OPTION
@VERSION_NAME_ARGUMENT
@VERSION_NAME_UPDATE
@MODEL_FILE
@VERSION_YAML_FILE
@LANGUAGE
@MEMORY_ALLOCATION
@MIN_INSTANCES
@MAX_INSTANCES
@MAX_IDLE_TIME
@QUIET
def versions_update(model_name, version_name, yaml_file, new_name, quiet, **kwargs):
    """Update a version of a model.

    You may want to change some deployment options, like, programming <language> and
    <memory_allocation>. You can do this by either providing the options in a yaml file
    and passing the file path as <yaml_file>, or passing the options as command options.
    If both a <yaml_file> is set and options are given, the options defined by <yaml_file>
    will be overwritten by the specified command options.
    """

    project_name = get_current_project(error=True)

    client = init_client()

    yaml_content = read_yaml(yaml_file, required_fields=[]) if yaml_file else None
    existing_version = client.model_versions_get(project_name=project_name, model_name=model_name,
                                                 version=version_name)

    kwargs = set_version_defaults(kwargs, yaml_content, existing_version, extra_yaml_fields=['model_file'])

    new_version_name = version_name if new_name is None else new_name
    version = api.ModelVersionCreate(version=new_version_name, **{k: kwargs[k] for k in MODEL_VERSION_FIELDS})
    update_model_file(client, project_name, model_name, version_name, kwargs['model_file'])
    client.model_versions_update(project_name=project_name, model_name=model_name, version=version_name,
                                 data=version)

    if not quiet:
        click.echo("Model version was successfully updated.")


@commands.command("delete")
@MODEL_NAME_OPTION
@VERSION_NAME_ARGUMENT
@ASSUME_YES
@QUIET
def versions_delete(model_name, version_name, assume_yes, quiet):
    """Delete a version of a model."""

    project_name = get_current_project(error=True)

    client = init_client()
    if assume_yes or click.confirm("Are you sure you want to delete model version <%s> of model <%s> in project <%s>?" %
                                   (version_name, model_name, project_name)):
        client.model_versions_delete(project_name=project_name, model_name=model_name, version=version_name)
        if not quiet:
            click.echo("Model version was successfully deleted.")
