from datetime import datetime

import click


# pylint: disable=broad-except
def wait_for(func, **kwargs):
    """
    Executes a wait_for client library function and prints the result

    :param callable func: the wait_for function to execute
    :param dict kwargs: the keyword arguments to pass to the specified wait_for function
    """

    success = True
    error_message = ""
    time_started = datetime.now()
    try:
        func(**kwargs)
    except Exception as e:
        success = False
        error_message = str(e)

    if not kwargs.get('quiet'):
        time_completed = datetime.now()
        click.echo(f"Start date: {time_started.isoformat(timespec='milliseconds')}")
        click.echo(f"Completion date: {time_completed.isoformat(timespec='milliseconds')}")

    if success:
        click.echo(f"Status: {click.style('success', fg='green')}")
    else:
        click.echo(f"Status: {click.style('failed', fg='red')}")

    if error_message:
        click.echo(f"Error message: {click.style(error_message, fg='red')}")
