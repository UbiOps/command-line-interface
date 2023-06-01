import json

from datetime import datetime

from ubiops.utils import run_local

from ubiops_cli.src.helpers.options import *
from ubiops_cli.utils import read_json, parse_json


@click.command("run_local", short_help="Run a deployment locally in current environment")
@DEPLOYMENT_DIR
@REQUEST_DATA_MULTI
@REQUEST_DATA_FILE
@REQUEST_DATA_PLAIN
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
        raise Exception("Specify data either using the <data> or <json_file> option, not both")

    if json_file:
        input_data = read_json(json_file)
        if plain and isinstance(input_data, list):
            for d in input_data:
                if not isinstance(d, str):
                    raise Exception("Each plain input must be a string")

        elif plain and not isinstance(input_data, str):
            raise Exception("Plain input must be a string")

    elif data:
        if plain:
            input_data = data
        else:
            input_data = []
            for d in data:
                input_data.append(parse_json(d))

    else:
        raise Exception("Missing option <data> or <json_file>")

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

    click.echo("Start date: %s" % time_started)
    click.echo("Completion date: %s" % time_completed)

    if success:
        click.echo('Status: %s' % click.style('completed', fg='green'))
    else:
        click.echo('Status: %s' % click.style('failed', fg='red'))

    if error_message:
        click.echo('Error message: %s' % click.style(error_message, fg='red'))

    click.echo("Request data: %s" % ('-' if input_data is None else json.dumps(input_data)))
    click.echo("Result: %s" % ('-' if result is None else json.dumps(result)))
