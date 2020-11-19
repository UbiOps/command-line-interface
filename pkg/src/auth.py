import ubiops as api
import requests
import json
from json import JSONDecodeError

from pkg.exceptions import UnAuthorizedException
from pkg.utils import get_current_project
from pkg.src.helpers.options import *


@click.command("signin", short_help="Sign in using your credentials")
@BEARER
@TOKEN
@API_ENDPOINT
@EMAIL_PROMPT
@PASSWORD_PROMPT
def signin(type_, api_endpoint, email, password):
    """Sign in using your credentials.

    If you want to use a service token, use the <token> flag option."""

    user_config = Config()

    assert len(api_endpoint) > 0, 'Please, specify the UbiOps API endpoint'
    # API endpoint should not end with a '/'
    api_endpoint = api_endpoint[:-1] if api_endpoint[-1] == "/" else api_endpoint
    user_config.set('auth.api', api_endpoint)

    if type_ == 'bearer':
        if not email:
            email = click.prompt('Email', default=Config().get("auth.email"))
        if not password:
            password = click.prompt('Password', hide_input=True)

        url = "%s/authorize" % api_endpoint
        headers = {"Content-Type": "application/json", "accept": "application/json"}
        data = {"email": email, "password": password}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        try:
            response = json.loads(response.text)
        except JSONDecodeError:
            raise Exception("Could not access %s" % api_endpoint)

        assert 'error' not in response, response['error']
        assert 'access' in response, "Could not authorize."

        user_config.set('auth.email', email)
        user_config.set('auth.tmp_access_token', response['access'])
        user_config.delete_option('auth.service_token')

    elif type_ == 'token':
        if not password:
            password = click.prompt('API Token', hide_input=True)
        if not password.startswith('Token '):
            click.echo("%s Token should be formatted like`\"Token 1abc2def3ghi4jkl5mno6pqr7stu8vwx9yz\"`"
                       % click.style('Warning:', fg='yellow'))

        try:
            configuration = api.Configuration()
            configuration.host = api_endpoint
            configuration.api_key_prefix['Authorization'] = ''
            configuration.api_key['Authorization'] = password
            client = api.CoreApi(api.ApiClient(configuration))
            assert client.service_status().status == 'ok'

            url = "%s/user" % api_endpoint
            response = requests.get(url, headers={"Authorization": password, "accept": "application/json"})
            response = json.loads(response.text)
            assert 'error' not in response, response['error']

            service_user = response
            client.api_client.close()
        except Exception:
            raise Exception('Could not authorize')

        user_config.set('auth.email', service_user['email'])
        user_config.set('auth.service_token', password)
        user_config.delete_option('auth.tmp_access_token')

    user_config.write()
    click.echo("Welcome to UbiOps!")

    project = get_current_project()
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
    user_config = Config()
    user_config.delete_option('auth.tmp_access_token')
    user_config.delete_option('auth.service_token')
    user_config.write()
