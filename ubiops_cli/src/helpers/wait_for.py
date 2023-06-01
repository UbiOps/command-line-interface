from datetime import datetime

import click


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
        click.echo("Start date: %s" % time_started.isoformat(timespec='milliseconds'))
        click.echo("Completion date: %s" % time_completed.isoformat(timespec='milliseconds'))

    if success:
        click.echo('Status: %s' % click.style('success', fg='green'))
    else:
        click.echo('Status: %s' % click.style('failed', fg='red'))

    if error_message:
        click.echo('Error message: %s' % click.style(error_message, fg='red'))
