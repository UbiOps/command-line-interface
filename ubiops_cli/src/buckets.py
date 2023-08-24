import click
import ubiops as api

from ubiops_cli.utils import get_current_project, init_client, read_yaml, write_yaml
from ubiops_cli.src.helpers.bucket_helpers import define_bucket, BUCKET_OUTPUT_FIELDS, BUCKET_FIELDS_RENAMED
from ubiops_cli.src.helpers.formatting import print_list, print_item, format_yaml
from ubiops_cli.src.helpers.helpers import get_label_filter
from ubiops_cli.src.helpers import options


LIST_ITEMS = ['name', 'provider', 'labels']


@click.group(name="buckets", short_help="Manage your buckets")
def commands():
    """Manage your buckets."""

    return


@commands.command(name="list", short_help="List buckets")
@options.LABELS_FILTER
@options.LIST_FORMATS
def buckets_list(labels, format_):
    """List buckets in project."""

    label_filter = get_label_filter(labels)
    project_name = get_current_project(error=True)

    client = init_client()
    response = client.buckets_list(project_name=project_name, labels=label_filter)
    client.api_client.close()

    print_list(response, LIST_ITEMS, sorting_col=0, fmt=format_)


@commands.command(name="get", short_help="Get a bucket")
@options.BUCKET_NAME_ARGUMENT
@options.BUCKET_YAML_OUTPUT
@options.QUIET
@options.GET_FORMATS
def buckets_get(bucket_name, output_path, quiet, format_):
    """Retrieve details of a bucket in a project.

    If you specify the `<output_path>` option, this location will be used to store the
    bucket settings in a yaml file. You can either specify the `<output_path>`
    as file or directory. If the specified `<output_path>` is a directory, the settings
    will be stored in `bucket.yaml`.

    Bucket credentials are never returned by the UbiOps API.

    \b
    Example of yaml content:
    ```
    bucket_name: my-bucket
    provider: amazon_s3
    configuration:
      region: eu-central-1
      bucket: my-bucket
    bucket_description: Bucket created via command line.
    bucket_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    ttl: 3600
    ```
    """

    project_name = get_current_project(error=True)

    client = init_client()
    bucket = client.buckets_get(project_name=project_name, bucket_name=bucket_name)
    client.api_client.close()

    if output_path is not None:

        # Store only reusable settings
        dictionary = format_yaml(
            item=bucket,
            required_front=["name"],
            optional=["provider", "configuration", "description", "labels", "ttl"],
            rename=BUCKET_FIELDS_RENAMED,
            as_str=False
        )

        yaml_file = write_yaml(output_path, dictionary, default_file_name="bucket.yaml")
        if not quiet:
            click.echo(f"Bucket file stored in: {yaml_file}")
    else:

        print_item(
            bucket,
            row_attrs=LIST_ITEMS,
            required_front=['id', 'creation_date', 'name'],
            optional=BUCKET_OUTPUT_FIELDS,
            rename=BUCKET_FIELDS_RENAMED,
            fmt=format_
        )


@commands.command(name="create", short_help="Create a bucket")
@options.BUCKET_NAME_OVERRULE
@options.BUCKET_PROVIDER
@options.BUCKET_CREDENTIALS
@options.BUCKET_CONFIGURATION
@options.BUCKET_DESCRIPTION
@options.BUCKET_LABELS
@options.BUCKET_TTL
@options.BUCKET_YAML_FILE
@options.CREATE_FORMATS
def buckets_create(yaml_file, format_, **kwargs):
    """
    Create a new bucket.

    \b
    Define the bucket parameters using a yaml file.
    For example:
    ```
    bucket_name: my-bucket
    bucket_description: Bucket created via command line.
    bucket_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    provider: amazon_s3
    credentials:
      access_key: my-access-key
      secret_key: my-secret-key
    configuration:
      region: eu-central-1
      bucket: my-bucket
    ttl: 3600
    ```

    The bucket name can either be passed as argument or specified inside the yaml
    file. If it is both passed as argument and specified inside the yaml file, the value
    passed as argument is used.

    Possible providers: [ubiops, google_cloud_storage, amazon_s3, azure_blob_storage].
    """

    project_name = get_current_project(error=True)
    yaml_content = read_yaml(yaml_file, required_fields=[])

    assert 'bucket_name' in yaml_content or 'bucket_name' in kwargs, \
        'Please, specify the bucket name in either the yaml file or as a command argument'

    bucket = define_bucket(fields=kwargs, yaml_content=yaml_content, update=False)

    client = init_client()
    bucket_response = client.buckets_create(project_name=project_name, data=bucket)
    client.api_client.close()

    print_item(
        bucket_response,
        row_attrs=LIST_ITEMS,
        required_front=['name'],
        optional=BUCKET_OUTPUT_FIELDS,
        rename=BUCKET_FIELDS_RENAMED,
        fmt=format_
    )


@commands.command(name="update", short_help="Update a bucket")
@options.BUCKET_NAME_OVERRULE
@options.BUCKET_PROVIDER
@options.BUCKET_DESCRIPTION
@options.BUCKET_LABELS
@options.BUCKET_TTL
@options.BUCKET_YAML_FILE
@options.CREATE_FORMATS
@options.QUIET
def buckets_update(yaml_file, quiet, **kwargs):
    """Update a bucket.

    \b
    It is possible to define the parameters using a yaml file. Note that the bucket_name and provider cannot be changed.
    For example:
    ```
    bucket_description: Bucket created via command line.
    bucket_labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    ttl: 3600
    ```
    """

    client = init_client()
    project_name = get_current_project(error=True)
    yaml_content = read_yaml(yaml_file, required_fields=[])

    bucket_dict = define_bucket(fields=kwargs, yaml_content=yaml_content, update=True)
    bucket = api.BucketUpdate(**bucket_dict)

    client.buckets_update(project_name=project_name, bucket_name=bucket_dict['name'], data=bucket)
    client.api_client.close()

    if not quiet:
        click.echo("Bucket was successfully updated")


@commands.command(name="delete", short_help="Delete a bucket")
@options.BUCKET_NAME_ARGUMENT
@options.ASSUME_YES
@options.QUIET
def buckets_delete(bucket_name, assume_yes, quiet):
    """Delete a bucket."""

    project_name = get_current_project(error=True)

    if assume_yes or click.confirm(
        f"Are you sure you want to delete bucket <{bucket_name}> of project <{project_name}>?"
    ):
        client = init_client()
        client.buckets_delete(project_name=project_name, bucket_name=bucket_name)
        client.api_client.close()

        if not quiet:
            click.echo("Bucket was successfully deleted")
