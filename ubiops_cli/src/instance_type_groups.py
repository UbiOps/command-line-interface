import click
import ubiops as api

from ubiops_cli.src.helpers.instance_type_group_helpers import (
    INSTANCE_TYPE_GROUP_LIST_FIELDS,
    INSTANCE_TYPE_GROUP_RESPONSE_FILE,
    INSTANCE_TYPE_GROUP_RESPONSE,
)
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import init_client, read_yaml, write_yaml, get_current_project, set_dict_default


@click.group(name="instance_type_groups", short_help="Manage your instance type groups")
def commands():
    """
    Manage your instance type groups.
    """

    return


@commands.command(name="list", short_help="List the instance type groups")
@options.INSTANCE_TYPE_GROUP_LIMIT
@options.LIST_FORMATS
def instance_type_groups_list(limit, format_):
    """
    List the instance type groups in your project.
    """

    project_name = get_current_project(error=True)

    client = init_client()
    response = client.instance_type_groups_list(project_name=project_name, limit=limit)
    client.api_client.close()

    print_list(items=response.results, attrs=INSTANCE_TYPE_GROUP_LIST_FIELDS, sorting_col=0, fmt=format_)


@commands.command(name="get", short_help="Get the instance type group")
@options.INSTANCE_TYPE_GROUP_ID_ARGUMENT
@options.INSTANCE_TYPE_GROUP_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
def instance_type_groups_get(instance_type_group_id, output_path, quiet, format_):
    """
    Get the instance type group in your project.

    If you specify the `<output_path>` option, this location will be used to store the
    instance type group settings in a yaml file. You can either specify the `<output_path>`
    as file or directory. If the specified `<output_path>` is a directory, the settings
    will be stored in `instance_type_group.yaml`.

    \b
    Example of yaml content:
    ```
    name: my-instance-type-group
    instance_types:
        - id: 2aae90dd-057b-4dfd-8502-f9074aa1be0f
          name: 256mb
          display_name: 256 MB + 0.062 vCPU
          cpu: 0.062
          memory: 256.0
          storage: 1024.0
          accelerator: 0
          credit_rate: 0.25
          dedicated_node: false
          priority: 0
          schedule_timeout: 300
    ```
    """

    project_name = get_current_project(error=True)

    client = init_client()
    group = client.instance_type_groups_get(project_name=project_name, instance_type_group_id=instance_type_group_id)
    client.api_client.close()

    if output_path is not None:
        # Store only reusable settings
        dictionary = format_yaml(
            item=group, required_front=INSTANCE_TYPE_GROUP_RESPONSE_FILE["required_front"], as_str=False
        )
        yaml_file = write_yaml(output_path, dictionary, default_file_name="instance_type_group.yaml")
        if not quiet:
            click.echo(f"Instance type group file stored in: {yaml_file}")
    else:
        print_item(
            item=group,
            row_attrs=INSTANCE_TYPE_GROUP_LIST_FIELDS,
            fmt=format_,
            required_front=INSTANCE_TYPE_GROUP_RESPONSE["required_front"],
            optional=INSTANCE_TYPE_GROUP_RESPONSE["optional"],
        )


@commands.command(name="create", short_help="Create a version")
@options.INSTANCE_TYPE_GROUP_NAME_OVERRULE
@options.INSTANCE_TYPE_GROUP_YAML_FILE
@options.CREATE_FORMATS
def instance_type_groups_create(name, yaml_file, format_):
    """
    Create an instance type group in your project.

    \b
    Define the instance type group parameters using a yaml file.
    For example:
    ```
    name: my-instance-type-group-name
    instance_types:
        - id: 2aae90dd-057b-4dfd-8502-f9074aa1be0f
          priority: 0
          schedule_timeout: 300
    ```

    Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
    options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
    The instance type group name can either be passed as command argument or specified inside the yaml file using
    `<name>`.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file=yaml_file)
    client = init_client()

    assert (
        "name" in yaml_content or name
    ), "Please, specify the instance type group name in either the yaml file or as a command argument"

    name = set_dict_default(name, yaml_content, "name")

    group = api.InstanceTypeGroupCreate(name=name, instance_types=yaml_content["instance_types"])
    response = client.instance_type_groups_create(project_name=project_name, data=group)
    client.api_client.close()

    print_item(
        item=response,
        row_attrs=INSTANCE_TYPE_GROUP_LIST_FIELDS,
        required_front=INSTANCE_TYPE_GROUP_RESPONSE["required_front"],
        optional=INSTANCE_TYPE_GROUP_RESPONSE["optional"],
        fmt=format_,
    )


@commands.command(name="update", short_help="Update an instance type group")
@options.INSTANCE_TYPE_GROUP_ID_ARGUMENT
@options.INSTANCE_TYPE_GROUP_NAME_UPDATE
@options.INSTANCE_TYPE_GROUP_YAML_FILE_OPTIONAL
@options.QUIET
def instance_type_groups_update(instance_type_group_id, new_name, yaml_file, quiet):
    """
    Update an instance type group.

    If you only want to update the name of the instance type group, use the option `<new_name>`.
    If you want to update the instance types, please use a yaml file to define the new instance type group.

    \b
    For example:
    ```
    name: my-instance-type-group-name
    instance_types:
        - id: 2aae90dd-057b-4dfd-8502-f9074aa1be0f
          priority: 0
          schedule_timeout: 300
    ```
    """

    project_name = get_current_project(error=True)
    client = init_client()

    yaml_content = read_yaml(yaml_file=yaml_file)
    new_name = set_dict_default(new_name, yaml_content, "name")

    parameters = {"name": new_name}
    if "instance_types" in yaml_content:
        parameters["instance_types"] = yaml_content["instance_types"]

    group = api.InstanceTypeGroupCreate(**parameters)
    client.instance_type_groups_update(
        project_name=project_name, instance_type_group_id=instance_type_group_id, data=group
    )
    client.api_client.close()

    if not quiet:
        click.echo("Instance type group was successfully updated")


@commands.command(name="delete", short_help="Delete an instance type group")
@options.INSTANCE_TYPE_GROUP_ID_ARGUMENT
@options.ASSUME_YES
@options.QUIET
def instance_type_groups_delete(instance_type_group_id, assume_yes, quiet):
    """
    Delete an instance type group.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete instance type group <{instance_type_group_id}> in project <{project_name}>?"
    ):
        client = init_client()
        client.instance_type_groups_delete(project_name=project_name, instance_type_group_id=instance_type_group_id)
        client.api_client.close()

        if not quiet:
            click.echo("Instance type group was successfully deleted")
