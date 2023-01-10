from ubiops_cli.exceptions import UnAuthorizedException
from ubiops_cli.utils import get_current_project
from ubiops_cli.src.helpers.options import *
from ubiops_cli.src.helpers.requests import sign_in, authorize, authorize2fa, sign_out, raise_for_status


@click.command("signin", short_help="Sign in using your credentials")
@BEARER
@TOKEN
@API_ENDPOINT
@EMAIL_PROMPT
@PASSWORD_PROMPT
def signin(type_, api_endpoint, email, password):
    """Sign in using your credentials.

    If you want to use a service token, use the `<token>` flag option."""

    assert len(api_endpoint) > 0, 'Please, specify the UbiOps API endpoint'
    # API endpoint should not end with a '/'
    api_endpoint = api_endpoint[:-1] if api_endpoint[-1] == "/" else api_endpoint

    if type_ == 'bearer':
        if not email:
            email = click.prompt('Email', default=Config().get("auth.email"))

        provider, url = sign_in(api_endpoint=api_endpoint, email=email)

        if provider == 'ubiops':
            if not password:
                password = click.prompt('Password', hide_input=True)
            success = authorize(api_endpoint, email, password)
            if not success:
                token2fa = click.prompt('Two factor authentication token')
                authorize2fa(api_endpoint, email, password, token2fa)

        else:
            raise NotImplementedError("Sign-in type %s not supported in the CLI.\n"
                                      "Please, use an API Token to sign in. You can create one in the WebApp "
                                      "in the Users & Permissions panel." % provider)

    elif type_ == 'token':
        if not password:
            password = click.prompt('API Token', hide_input=True)
        if not password.startswith('Token '):
            click.echo("%s Token should be formatted like`\"Token 1abc2def3ghi4jkl5mno6pqr7stu8vwx9yz\"`"
                       % click.style('Warning:', fg='yellow'))

        try:
            raise_for_status(api_endpoint=api_endpoint, token=password)
        except Exception:
            raise Exception('Could not authorize')

    click.echo("\nWelcome to UbiOps!")

    project = get_current_project(check_existing=True)
    if project:
        click.echo("\nSelected project: %s" % click.style(project, fg='yellow'))
        click.echo("To change the selected project, use: `ubiops current_project set <PROJECT_NAME>`")
    else:
        click.echo("\n%s" % click.style("No projects found", fg='yellow'))
        click.echo("To create a project, use: `ubiops projects create <PROJECT_NAME>`")


@click.group("user", short_help="The current user interacting with the CLI")
def user():
    """The current user interacting with the CLI."""
    pass


@user.command("get", short_help="Show the email of the current user")
def user_get():
    """Show the email of the current user."""
    user_config = Config()
    current_email = user_config.get('auth.email')

    if current_email:
        click.echo(current_email)


@user.command("set")
@EMAIL_ARGUMENT
def user_set(email):
    """Change the user interacting with the CLI."""
    user_config = Config()
    user_config.set('auth.email', email)
    user_config.write()


@click.command("status", short_help="Get login status")
def status():
    """Whether the current user is authorized or not."""
    user_config = Config()
    api_endpoint = user_config.get('auth.api')
    email = user_config.get('auth.email')

    try:
        project = get_current_project()
        click.echo("Authorized")
        click.echo("email: %s" % email)
        click.echo("api: %s" % api_endpoint)
        if project:
            click.echo("project: %s" % project)
    except UnAuthorizedException:
        click.echo("Unauthorized")
        click.echo("Please, use 'ubiops signin' to sign in")


@click.command("signout", short_help="Sign out of the CLI")
def signout():
    """Sign out of the CLI."""
    sign_out()
