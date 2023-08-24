import click

from ubiops_cli.exceptions import UnAuthorizedException
from ubiops_cli.utils import get_current_project
from ubiops_cli.src.config import Config
from ubiops_cli.src.helpers.requests import sign_in, authorize, authorize2fa, sign_out, raise_for_status
from ubiops_cli.src.helpers import options


@click.command(name="signin", short_help="Sign in using your credentials")
@options.BEARER
@options.TOKEN
@options.API_HOST
@options.EMAIL_PROMPT
@options.PASSWORD_PROMPT
def signin(method, host, email, password):
    """
    Sign in using your credentials.

    If you want to use a service token, use the `<token>` flag option.
    """

    assert len(host) > 0, 'Please, specify the UbiOps API host'
    # API host should not end with a '/'
    host = host[:-1] if host[-1] == "/" else host

    if method == 'bearer':
        if not email:
            email = click.prompt(text='Email', default=Config().get("auth.email"))

        provider, _ = sign_in(host=host, email=email)

        if provider == 'ubiops':
            if not password:
                password = click.prompt(text='Password', hide_input=True)
            success = authorize(host=host, email=email, password=password)
            if not success:
                token2fa = click.prompt(text='Two factor authentication token')
                authorize2fa(host=host, email=email, password=password, token=token2fa)

        else:
            raise NotImplementedError(
                f"Sign-in type {provider} not supported in the CLI.\n"
                "Please, use an API Token to sign in. You can create one in the WebApp in the Project Admin panel."
            )

    elif method == 'token':
        if not password:
            password = click.prompt(text='API Token', hide_input=True)
        if not password.startswith('Token '):
            click.echo(
                message=f"{click.style('Warning:', fg='yellow')} Token should be formatted like "
                        "`\"Token 1abc2def3ghi4jkl5mno6pqr7stu8vwx9yz\"`"
            )

        try:
            raise_for_status(host=host, token=password)
        except Exception:
            raise UnAuthorizedException('Could not authorize')

    click.echo(message="\nWelcome to UbiOps!")

    project = get_current_project(check_existing=True)
    if project:
        click.echo(message=f"\nSelected project: {click.style(project, fg='yellow')}")
        click.echo(message="To change the selected project, use: `ubiops current_project set <PROJECT_NAME>`")
    else:
        click.echo(message=f"\n{click.style('No projects found', fg='yellow')}")
        click.echo(message="To create a project, use: `ubiops projects create <PROJECT_NAME>`")


@click.group(name="user", short_help="The current user interacting with the CLI")
def user():
    """
    The current user interacting with the CLI.
    """

    return


@user.command(name="get", short_help="Show the email of the current user")
def user_get():
    """
    Show the email of the current user.
    """

    user_config = Config()
    current_email = user_config.get(key='auth.email')

    if current_email:
        click.echo(current_email)


@user.command(name="set")
@options.EMAIL_ARGUMENT
def user_set(email):
    """
    Change the user interacting with the CLI.
    """

    user_config = Config()
    user_config.set(key='auth.email', value=email)
    user_config.write()


@click.command(name="status", short_help="Get login status")
def status():
    """
    Whether the current user is authorized or not.
    """

    user_config = Config()
    api_endpoint = user_config.get(key='auth.api')
    email = user_config.get(key='auth.email')

    try:
        project = get_current_project()
        click.echo("Authorized")
        click.echo(f"email: {email}")
        click.echo(f"api: {api_endpoint}")
        if project:
            click.echo(f"project: {project}")
    except UnAuthorizedException:
        click.echo("Unauthorized")
        click.echo("Please, use 'ubiops signin' to sign in")


@click.command(name="signout", short_help="Sign out of the CLI")
def signout():
    """
    Sign out of the CLI.
    """

    sign_out()
