import os

import click

from .helpers.formatting import print_list, parse_datetime, format_datetime

from ..exceptions import UbiOpsException
from ..utils import init_client, get_current_project


LIST_ITEMS = ["last_updated", "name", "labels"]
REQUEST_LIST_ITEMS = ["id", "status", "time_created"]


def list_requests(object_type, object_name, version_name, limit, format_, **kwargs):
    """
    Base method for (deployment/pipeline) requests_list

    :param str object_type: "deployment" or "pipeline"
    :param str object_name: name of the deployment/pipeline
    :param str version_name: name of the version
    :param int limit: maximum number of items returned
    :param str format_: how the requests should be formatted
    :param dict kwargs: additional options for the request list call
    """

    project_name = get_current_project(error=True)

    if "start_date" in kwargs and kwargs["start_date"]:
        try:
            kwargs["start_date"] = format_datetime(parse_datetime(kwargs["start_date"]), fmt="%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise UbiOpsException(
                "Failed to parse start_date. Please use iso-format, for example, '2020-01-01T00:00:00.000000Z'"
            )

    if "end_date" in kwargs and kwargs["end_date"]:
        try:
            kwargs["end_date"] = format_datetime(parse_datetime(kwargs["end_date"]), fmt="%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise UbiOpsException(
                "Failed to parse end_date. Please use iso-format, for example, '2020-01-01T00:00:00.000000Z'"
            )

    if version_name is None:
        method_name = f"{object_type}_requests_list"
        method_kwargs = {"project_name": project_name, f"{object_type}_name": object_name}
    else:
        method_name = f"{object_type}_version_requests_list"
        method_kwargs = {"project_name": project_name, f"{object_type}_name": object_name, "version": version_name}

    client = init_client()
    response = getattr(client, method_name)(**method_kwargs)
    client.api_client.close()

    print_list(response, REQUEST_LIST_ITEMS, fmt=format_, json_skip=["success"])
    if len(response) == limit:
        click.echo("\n(Use the <offset> and <limit> options to load more)")


# pylint: disable=too-many-arguments
def get_request_input_output(data_type, object_type, object_name, version_name, request_id, output_path, assume_yes):
    """
    Base method for (deployment/pipeline) requests_input and requests_output. Use `data_type` to specify
    whether it's for retrieving the input or output of the request.

    :param str data_type: "input" or "output"
    :param str object_type: "deployment" or "pipeline"
    :param str object_name: name of the deployment/pipeline
    :param str version_name: name of the version
    :param str request_id: id of the request
    :param str output_path: path of the output file if any
    :param bool assume_yes: whether to overwrite the file if exists
    """

    project_name = get_current_project(error=True)

    if output_path:
        # Make sure output path is absolute
        output_path = os.path.abspath(output_path)

    if version_name is None:
        method_name = f"{object_type}_requests_{data_type}_get"
        method_kwargs = {"project_name": project_name, f"{object_type}_name": object_name, "request_id": request_id}
    else:
        method_name = f"{object_type}_version_requests_{data_type}_get"
        method_kwargs = {
            "project_name": project_name,
            f"{object_type}_name": object_name,
            "version": version_name,
            "request_id": request_id,
        }

    client = init_client()

    if output_path:
        # Response = where the data is stored
        with getattr(client, method_name)(**method_kwargs, _request_stream=True) as stream:
            if os.path.isdir(output_path):
                filename = stream.getfilename() if hasattr(stream, "getfilename") else f"{request_id}_{data_type}.json"
                output_path = os.path.join(output_path, filename)

            if not assume_yes and os.path.exists(output_path):
                click.confirm(f"File {output_path} already exists. Do you want to overwrite it?", abort=True)

            with open(output_path, "wb") as output_file:
                output_file.write(stream.read())
        click.echo(output_path)

    else:
        # Response = the data as text
        response = getattr(client, method_name)(**method_kwargs)
        click.echo(response.text)

    client.api_client.close()
