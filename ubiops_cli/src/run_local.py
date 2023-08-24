import json

from datetime import datetime

import click

from ubiops.utils import run_local

from ubiops_cli.exceptions import UbiOpsException
from ubiops_cli.src.helpers import options
from ubiops_cli.utils import read_json, parse_json


# pylint: disable=broad-except
# pylint: disable=too-many-branches
@click.command(name="run_local", short_help="Run a deployment locally in current environment")
@options.DEPLOYMENT_DIR
@options.REQUEST_DATA_MULTI
@options.REQUEST_DATA_FILE
@options.REQUEST_DATA_PLAIN
def deployment_run_local(directory, data, json_file, plain):
    """
    Run a deployment locally and call its request function.

    Use `-dir` to specify the deployment directory where the deployment.py is.

    Input data can be provided to the deployment in two ways:
    - Use `--json_file` to use input data from a JSON file.
    - Use `--data` to provide input data directly. The input data must be a valid JSON string.

    If the input data is plain, pass the `--plain` option. The input data will be sent as a string as it is provided.

    Multiple data inputs can be specified at once and sent as batch by using the '--data' options multiple times:
    `ubiops run_local -dir /path/to/deployment --data <input-1> --data <input-2> --data <input-3>`

    For structured input, specify each data input as JSON formatted string. For example:
    `ubiops run_local -dir /path/to/deployment --data "{\\"param1\\": 1, \\"param2\\": \\"two\\"}"`
    """

    data = list(data)

    if json_file and data:
        raise UbiOpsException("Specify data either using the <data> or <json_file> option, not both")

    if json_file:
        input_data = read_json(json_file)
        if plain and isinstance(input_data, list):
            for data_item in input_data:
                if not isinstance(data_item, str):
                    raise UbiOpsException("Each plain input must be a string")

        elif plain and not isinstance(input_data, str):
            raise UbiOpsException("Plain input must be a string")

    elif data:
        if plain:
            input_data = data
        else:
            input_data = []
            for data_item in data:
                input_data.append(parse_json(data=data_item))

    else:
        raise UbiOpsException("Missing option <data> or <json_file>")

    time_started = datetime.now().isoformat(timespec='milliseconds')
    result = None
    success = True
    error_message = ""

    try:
        result = run_local(deployment_directory=directory, data=input_data)
    except Exception as e:
        success = False
        error_message = str(e)

    time_completed = datetime.now().isoformat(timespec='milliseconds')

    click.echo(f"Start date: {time_started}")
    click.echo(f"Completion date: {time_completed}")

    if success:
        click.echo(f"Status: {click.style(text='completed', fg='green')}")
    else:
        click.echo(f"Status: {click.style(text='failed', fg='red')}")

    if error_message:
        click.echo(f"Error message: {click.style(text=error_message, fg='red')}")

    click.echo(f"Request data: {('-' if input_data is None else json.dumps(input_data))}")
    click.echo(f"Result: {('-' if result is None else json.dumps(result))}")
