import click
import ubiops as api

from .helpers.service_helpers import (
    define_service,
    SERVICE_CREATE_FIELDS,
    SERVICE_DETAILS,
    SERVICE_FIELDS_RENAMED,
    SERVICE_UPDATE_FIELDS,
)
from .helpers.formatting import print_list, print_item, format_yaml
from .helpers.helpers import get_label_filter
from .helpers import options
from ..utils import get_current_project, init_client, read_yaml, write_yaml

LIST_ITEMS = ["time_updated", "name", "labels"]


@click.group(name="services", short_help="Manage your services")
def commands():
    """
    Manage your services.
    """

    return


@commands.command(name="list", short_help="List services")
@options.LABELS_FILTER
@options.DEPLOYMENT_VERSION_IDS_FILTER
@options.LIST_FORMATS
def services_list(labels, format_, **kwargs):
    """
    List all your services in your project.

    The `<labels>` option can be used to filter on specific labels. The `<deployment_version_ids>` option can be used to
    filter on specific deployment versions.
    """

    project_name = get_current_project(error=True)
    label_filter = get_label_filter(labels)

    client = init_client()
    services = client.services_list(project_name=project_name, labels=label_filter, **kwargs)
    client.api_client.close()

    print_list(items=services, attrs=LIST_ITEMS, sorting_col=1, fmt=format_)


@commands.command(name="get", short_help="Get details of a service")
@options.SERVICE_NAME_ARGUMENT
@options.SERVICE_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
def services_get(service_name, output_path, quiet, format_):
    """
    Get the service details.

    If you specify the `<output_path>` option, this location will be used to store the
    service settings in a yaml file. You can either specify the `<output_path>` as
    file or directory. If the specified `<output_path>` is a directory, the settings
    will be stored in `service.yaml`.

    \b
    Example of yaml content:
    ```
    service_name: my-service
    service_description: Service created via command line.
    service_labels:
        my-key-1: my-label-1
        my-key-2: my-label-2
    ```
    """

    project_name = get_current_project(error=True)

    # Show service details
    client = init_client()
    service = client.services_get(project_name=project_name, service_name=service_name)
    client.api_client.close()

    if output_path is not None:
        # Store only reusable settings
        non_reusable_fields = ["time_created", "time_updated", "endpoint"]
        dictionary = format_yaml(
            item=service,
            optional=[field for field in SERVICE_DETAILS if field not in non_reusable_fields],
            rename=SERVICE_FIELDS_RENAMED,
            as_str=False,
        )

        yaml_file = write_yaml(output_path, dictionary, default_file_name="service.yaml")
        if not quiet:
            click.echo(f"Service file stored in: {yaml_file}")

    else:
        print_item(
            item=service,
            row_attrs=LIST_ITEMS,
            optional=SERVICE_DETAILS,
            rename=SERVICE_FIELDS_RENAMED,
            fmt=format_,
        )


@commands.command(name="create", short_help="Create a service")
@options.SERVICE_NAME_OVERRULE
@options.SERVICE_YAML_FILE
@options.OVERWRITE
@options.CREATE_FORMATS
def services_create(yaml_file, overwrite, format_, **kwargs):
    """
    Create a service.

    Use `--overwrite` flag to update the service if it already exists.

    \b
    Use a yaml file. For example:
    ```
    service_name: my-service-name
    service_description: Service created via command line.
    service_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    service_deployment: my-deployment-name
    service_version: my-deployment-version
    port: 8080
    authentication_required: true
    authentication_method_token_enabled: true
    request_logging_excluded_paths: "(health|status)$"
    request_logging_excluded_extensions:
      - svg
      - tar
    health_check:
      path: "/status"
    rate_limit_token: 300
    ```

    The service name can either be passed as command argument or specified inside the yaml file using
    `<service_name>`.
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)

    assert (
        "service_name" in yaml_content or "service_name" in kwargs
    ), "Please, specify the service name in either the yaml file or as a command argument"

    kwargs = define_service(kwargs, yaml_content)
    service_name = kwargs["name"]

    client = init_client()
    existing_service = None
    if overwrite:
        try:
            existing_service = client.services_get(project_name=project_name, service_name=service_name)
        except api.exceptions.ApiException:
            # Do nothing if service doesn't exist
            pass

    if existing_service:
        service = api.ServiceUpdate(**{k: kwargs[k] for k in SERVICE_UPDATE_FIELDS if kwargs.get(k, None) is not None})
        response = client.services_update(project_name=project_name, service_name=service_name, data=service)
    else:
        service = api.ServiceCreate(
            **{k: kwargs[k] for k in SERVICE_CREATE_FIELDS if k in kwargs and kwargs[k] is not None}
        )
        response = client.services_create(project_name=project_name, data=service)

    client.api_client.close()

    print_item(
        item=response,
        row_attrs=LIST_ITEMS,
        optional=SERVICE_DETAILS,
        rename=SERVICE_FIELDS_RENAMED,
        fmt=format_,
    )


@commands.command(name="update", short_help="Update a service")
@options.SERVICE_NAME_ARGUMENT
@options.SERVICE_NAME_UPDATE
@options.SERVICE_YAML_FILE_OPTIONAL
@options.QUIET
def services_update(service_name, new_name, yaml_file, quiet):
    """
    Update a service.

    It is possible to define the updated parameter values using a yaml file. Or provide the `<new_name>` directly as
    command option. When both a yaml file and command options are given, the command options are prioritized over the
    yaml content.

    \b
    For example:
    ```
    service_name: new-name
    service_description: Service created via command line.
    service_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    service_deployment: my-deployment-name
    service_version: my-deployment-version
    port: 8080
    authentication_required: true
    authentication_method_token_enabled: true
    request_logging_excluded_paths: "(health|status)$"
    request_logging_excluded_extensions:
      - svg
      - tar
    health_check:
      path: "/status"
    rate_limit_token: 300
    ```
    """

    project_name = get_current_project(error=True)

    yaml_content = read_yaml(yaml_file)
    kwargs = define_service({"service_name": new_name}, yaml_content)
    service = api.ServiceUpdate(
        **{k: kwargs[k] for k in SERVICE_UPDATE_FIELDS if k in kwargs and kwargs[k] is not None}
    )

    client = init_client()
    client.services_update(project_name=project_name, service_name=service_name, data=service)
    client.api_client.close()

    if not quiet:
        click.echo("Service was successfully updated")


@commands.command(name="delete", short_help="Delete a service")
@options.SERVICE_NAME_ARGUMENT
@options.ASSUME_YES
@options.QUIET
def services_delete(service_name, assume_yes, quiet):
    """
    Delete a service.
    """

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete service <{service_name}> in project <{project_name}>?"
    ):
        client = init_client()
        client.services_delete(project_name=project_name, service_name=service_name)
        client.api_client.close()
        if not quiet:
            click.echo("Service was successfully deleted")
