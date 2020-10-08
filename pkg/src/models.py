import ubiops as api
import os
import json

from pkg.utils import init_client, read_yaml, write_yaml, zip_dir, get_current_project, \
    set_dict_default, write_blob, default_model_version_zip_name
from pkg.src.helpers.helpers import set_version_defaults, update_model_file, MODEL_VERSION_FIELDS
from pkg.src.helpers.formatting import print_list, print_item, format_yaml, format_requests_reference, \
    format_requests_oneline, format_json
from pkg.src.helpers.options import *
from pkg.constants import STATUS_INITIALISED, STRUCTURED_TYPE, DEFAULT_IGNORE_FILE


LIST_ITEMS = ['id', 'name', 'input_type', 'output_type', 'last_updated']
REQUEST_LIST_ITEMS = ['id', 'status', 'success', 'time_created']


@click.group("models")
def commands():
    """Manage your models."""
    pass


@commands.command("list")
@LIST_FORMATS
def models_list(format_):
    """List all your models in your project."""

    project_name = get_current_project()
    if project_name:
        client = init_client()
        models = client.models_list(project_name=project_name)
        print_list(models, LIST_ITEMS, project_name=project_name, sorting_col=1, fmt=format_)


@commands.command("get")
@MODEL_NAME_ARGUMENT
@MODEL_YAML_OUTPUT
@QUIET
@GET_FORMATS
def models_get(model_name, output_path, quiet, format_):
    """Get the model settings, like, input_type and output_type.

    If you specify the <output_path> option, this location will be used to store the
    model settings in a yaml file. You can either specify the <output_path> as file or
    directory. If the specified <output_path> is a directory, the settings will be
    stored in `model.yaml`."""

    project_name = get_current_project(error=True)

    client = init_client()
    model = client.models_get(project_name=project_name, model_name=model_name)

    if output_path is not None:
        dictionary = format_yaml(model, required_front=['name', 'description', 'input_type', 'output_type'],
                                 optional=['input_fields', 'output_fields'],
                                 rename={'name': 'model_name', 'description': 'model_description'}, as_str=False)
        yaml_file = write_yaml(output_path, dictionary, default_file_name="model.yaml")
        if not quiet:
            click.echo('Model file is stored in: %s' % yaml_file)
    else:
        print_item(model, row_attrs=LIST_ITEMS, project_name=project_name,
                   rename={'name': 'model_name', 'description': 'model_description'}, fmt=format_)


@commands.command("create")
@MODEL_NAME_OVERRULE
@MODEL_YAML_FILE
@CREATE_FORMATS
def models_create(model_name, yaml_file, format_):
    """Create a new model.

    \b
    Define the model parameters using a yaml file.
    For example:
    ```
    model_name: my-model-name
    model_description: Model created via command line.
    input_type: structured
    input_fields:
      - name: param1
        data_type: int
      - name: param2
        data_type: string
    output_type: plain
    ```

    The model name can either be passed as argument or specified inside the yaml file. If it is both passed as argument
    and specified inside the yaml file, the value passed as argument is used.

    Possible input/output types: [structured, plain]. Possible data_types: [blob, int,
    string, double, bool, array_string, array_int, array_double].
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file, required_fields=MODEL_REQUIRED_FIELDS)
    client = init_client()

    assert 'model_name' in yaml_content or model_name, 'Please, specify the model name in either the yaml ' \
                                                       'file or as a command argument.'

    model_name = set_dict_default(model_name, yaml_content, 'model_name')
    description = set_dict_default(None, yaml_content, 'model_description')

    if 'input_fields' in yaml_content:
        input_fields = [api.models.ModelInputFieldCreate(
            name=item['name'], data_type=item['data_type']) for item in yaml_content['input_fields']]
    else:
        input_fields = None

    if 'output_fields' in yaml_content:
        output_fields = [api.models.ModelInputFieldCreate(
            name=item['name'], data_type=item['data_type']) for item in yaml_content['output_fields']]
    else:
        output_fields = None

    model = api.models.ModelCreate(
        name=model_name, description=description,
        input_type=yaml_content['input_type'], output_type=yaml_content['output_type'],
        input_fields=input_fields, output_fields=output_fields)
    response = client.models_create(project_name=project_name, data=model)
    print_item(response, row_attrs=LIST_ITEMS,  project_name=project_name,
               rename={'name': 'model_name', 'description': 'model_description'}, fmt=format_)


@commands.command("update")
@MODEL_NAME_ARGUMENT
@MODEL_NAME_UPDATE
@QUIET
def models_update(model_name, new_name, quiet):
    """Delete a model."""

    project_name = get_current_project(error=True)

    client = init_client()
    model = api.ModelUpdate(name=new_name if new_name else model_name)
    client.models_update(project_name=project_name, model_name=model_name, data=model)

    if not quiet:
        click.echo("Model was successfully updated.")


@commands.command("delete")
@MODEL_NAME_ARGUMENT
@ASSUME_YES
@QUIET
def models_delete(model_name, assume_yes, quiet):
    """Delete a model."""

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm("Are you sure you want to delete model <%s> "
                                   "of project <%s>?" % (model_name, project_name)):
        client = init_client()
        client.models_delete(project_name=project_name, model_name=model_name)

        if not quiet:
            click.echo("Model was successfully deleted.")


@commands.command("package")
@MODEL_NAME_ZIP
@VERSION_NAME_ZIP
@PACKAGE_DIR
@ZIP_OUTPUT
@IGNORE_FILE
@ASSUME_YES
@QUIET
def models_package(model_name, version_name, directory, output_path, ignore_file, assume_yes, quiet):
    """Package code to ZIP file which is ready to be deployed.

    Please, specify the code <directory> that should be deployed. The files in this directory
    will be zipped and uploaded. Subdirectories and files that shouldn't be contained in
    the ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of
    this file is assumed to be equal to the wellknown .gitignore file.

    Use the <output_path> option to specify the output location of the zip file. If not specified,
    the current directory will be used. If the <output_path> is a directory, the zip will be saved in
    `[model_name]_[model_version]_[datetime.now()].zip`. Use the <assume_yes> option to overwrite
    without confirmation if file specified in <output_path> already exists.
    """

    ignore_file = DEFAULT_IGNORE_FILE if ignore_file is None else ignore_file
    zip_path = zip_dir(directory, output_path, ignore_filename=ignore_file,
                       model_name=model_name, model_version=version_name, force=assume_yes)
    if not quiet:
        click.echo("Created zip: %s" % zip_path)


@commands.command("upload")
@MODEL_NAME_ARGUMENT
@VERSION_NAME_OPTION
@ZIP_FILE
@OVERWRITE
@QUIET
def models_upload(model_name, version_name, zip_path, overwrite, quiet):
    """Upload ZIP to a version of a model.

    Please, specify the model package <zip_path> that should be uploaded.
    Use the <overwrite> option to overwrite the model package on UbiOps if one already exists for this version.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    current_version = client.model_versions_get(project_name=project_name, model_name=model_name, version=version_name)

    if overwrite or current_version.status == STATUS_INITIALISED:
        client.model_versions_file_upload(project_name=project_name, model_name=model_name,
                                          version=version_name, file=zip_path)
        if not quiet:
            click.echo("Model was successfully uploaded.")
    else:
        raise Exception("A model package already exists for this model version.")


@commands.command("download")
@MODEL_NAME_ARGUMENT
@VERSION_NAME_OPTION
@ZIP_OUTPUT
@QUIET
def models_download(model_name, version_name, output_path, quiet):
    """Get the version of a model.

    The <output_path> option will be used as output location of the zip file. If not specified,
    the current directory will be used. If the <output_path> is a directory, the zip will be
    saved in `[model_name]_[model_version]_[datetime.now()].zip`.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.model_versions_file_download(project_name=project_name,
                                                   model_name=model_name,
                                                   version=version_name)
    filename = default_model_version_zip_name(model_name, version_name)
    output_path = write_blob(response.read(), output_path, filename)
    if not quiet:
        click.echo("Zip stored in: %s" % output_path)


@commands.command("deploy")
@MODEL_NAME_OVERRULE
@VERSION_NAME_OPTIONAL
@PACKAGE_DIR
@MODEL_FILE
@IGNORE_FILE
@ZIP_OUTPUT_STORE
@VERSION_YAML_FILE
@LANGUAGE
@MEMORY_ALLOCATION
@MIN_INSTANCES
@MAX_INSTANCES
@MAX_IDLE_TIME
@OVERWRITE
@ASSUME_YES
@QUIET
def models_deploy(model_name, version_name, directory, output_path, yaml_file, overwrite,
                  assume_yes, quiet, **kwargs):
    """Deploy a new version of a model.

    Please, specify the code <directory> that should be deployed. The files in this directory
    will be zipped and uploaded. Subdirectories and files that shouldn't be contained in the
    ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this
    file is assumed to be equal to the wellknown .gitignore file.

    If you want to store a local copy of the uploaded zip file, please use the <output_path> option.
    The <output_path> option will be used as output location of the zip file. If the <output_path> is a
    directory, the zip will be saved in `[model_name]_[model_version]_[datetime.now()].zip`. Use
    the <assume_yes> option to overwrite without confirmation if file specified in <output_path> already exists.

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
    The model name can either be passed as command argument or specified inside the yaml file using <model_name>.
    """

    if output_path is None:
        store_zip = False
        output_path = ''
    else:
        store_zip = True

    project_name = get_current_project(error=True)
    client = init_client()
    yaml_content = read_yaml(yaml_file, required_fields=[]) if yaml_file else None

    assert 'model_name' in yaml_content or model_name, 'Please, specify the model name in either the yaml ' \
                                                       'file or as a command argument.'
    assert 'version_name' in yaml_content or version_name, 'Please, specify the version name in either the yaml ' \
                                                           'file or as a command option.'
    model_name = set_dict_default(model_name, yaml_content, 'model_name')
    version_name = set_dict_default(version_name, yaml_content, 'version_name')

    existing_version = None
    if overwrite:
        try:
            existing_version = client.model_versions_get(project_name=project_name, model_name=model_name,
                                                         version=version_name)
        except Exception:
            # do nothing if version doesn't exist
            pass

    kwargs = set_version_defaults(kwargs, yaml_content, existing_version,
                                  extra_yaml_fields=['model_file', 'ignore_file'])
    kwargs['ignore_file'] = DEFAULT_IGNORE_FILE if kwargs['ignore_file'] is None else kwargs['ignore_file']

    version = api.ModelVersionCreate(version=version_name, **{k: kwargs[k] for k in MODEL_VERSION_FIELDS})
    zip_path = zip_dir(directory, output_path, ignore_filename=kwargs['ignore_file'],
                       model_name=model_name, model_version=version_name, force=assume_yes)

    try:
        if not (overwrite and existing_version):
            client.model_versions_create(project_name=project_name, model_name=model_name, data=version)

        update_model_file(client, project_name, model_name, version_name, kwargs['model_file'])
        client.model_versions_file_upload(project_name=project_name, model_name=model_name,
                                          version=version_name, file=zip_path)

        if overwrite and existing_version:
            client.model_versions_update(project_name=project_name, model_name=model_name, version=version_name,
                                         data=version)
    except Exception as e:
        if os.path.isfile(zip_path) and not store_zip:
            os.remove(zip_path)
        raise e

    if os.path.isfile(zip_path):
        if store_zip:
            if not quiet:
                click.echo("Created zip: %s" % zip_path)
        else:
            os.remove(zip_path)

    if not quiet:
        click.echo("Model was successfully deployed.")


@commands.command("request")
@MODEL_NAME_ARGUMENT
@VERSION_NAME_OPTION
@REQUEST_DATA
@REQUEST_TIMEOUT
@REQUESTS_FORMATS
def models_request(model_name, version_name, data, timeout, format_):
    """Create a model request and retrieve the result.

    For structured input, specify the data as JSON formatted string. For example:
    `ubiops models request <my-model> -v <my-version> -d "{\"param1\": 1, \"param2\": \"two\"}"`
    """

    project_name = get_current_project(error=True)

    client = init_client()
    model = client.models_get(project_name=project_name, model_name=model_name)

    if model.input_type == STRUCTURED_TYPE:
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            raise Exception("Failed to parse data. JSON format expected.")

    response = client.model_requests_create(project_name=project_name, model_name=model_name,
                                            version=version_name, data=data, timeout=timeout)

    if format_ == 'reference':
        click.echo(format_requests_reference([response]))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline([response]))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_requests_reference([response]))


@commands.group("batch_requests")
def batch_requests():
    """Manage your model batch requests."""
    pass


@batch_requests.command("create")
@MODEL_NAME_ARGUMENT
@VERSION_NAME_OPTION
@REQUEST_DATA_MULTI
@REQUESTS_FORMATS
def batch_requests_create(model_name, version_name, data, format_):
    """Create a model batch request and retrieve request IDs to collect the results later.

    Multiple data inputs can be specified at ones by using the '-d' options multiple times:
    `ubiops models batch_requests create <my-model> -v <my-version> -d <input-1> -d <input-2> -d <input-3>`

    For structured input, specify each data input as JSON formatted string. For example:
    `ubiops models batch_requests create <my-model> -v <my-version> -d "{\"param1\": 1, \"param2\": \"two\"}"`
    """

    data = list(data)

    project_name = get_current_project(error=True)

    client = init_client()
    model = client.models_get(project_name=project_name, model_name=model_name)

    if model.input_type == STRUCTURED_TYPE:
        input_data = []
        for d in data:
            try:
                input_data.append(json.loads(d))
            except json.JSONDecodeError:
                raise Exception("Failed to parse data. JSON format expected. Input: %s" % d)
    else:
        input_data = data

    response = client.batch_model_requests_create(project_name=project_name, model_name=model_name,
                                                  version=version_name, data=input_data)

    if format_ == 'reference':
        click.echo(format_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_requests_reference(response))


@batch_requests.command("get")
@MODEL_NAME_ARGUMENT
@VERSION_NAME_OPTION
@REQUEST_ID_MULTI
@REQUESTS_FORMATS
def batch_requests_get(model_name, version_name, request_id, format_):
    """Get the results of one or more model batch requests.

    Multiple request ids can be specified at ones by using the '-id' options multiple times:
    `ubiops models batch_requests get <my-model> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`
    """

    request_ids = list(request_id)

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.batch_model_requests_batch_collect(project_name=project_name, model_name=model_name,
                                                         version=version_name, data=request_ids)

    if format_ == 'reference':
        click.echo(format_requests_reference(response))
    elif format_ == 'oneline':
        click.echo(format_requests_oneline(response))
    elif format_ == 'json':
        click.echo(format_json(response))
    else:
        click.echo(format_requests_reference(response))


@batch_requests.command("list")
@MODEL_NAME_ARGUMENT
@VERSION_NAME_OPTION
@OFFSET
@REQUEST_LIMIT
@LIST_FORMATS
def batch_requests_list(model_name, version_name, offset, limit, format_):
    """List model batch requests."""

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.batch_model_requests_list(project_name=project_name, model_name=model_name, version=version_name,
                                                limit=limit, offset=offset)
    print_list(response, REQUEST_LIST_ITEMS, fmt=format_)
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more.)")
