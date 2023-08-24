import click
import ubiops as api

from ubiops_cli.utils import init_client, get_current_project, Config
from ubiops_cli.src.helpers.formatting import print_item, print_projects_list
from ubiops_cli.src.helpers import options


LIST_ITEMS = ['creation_date', 'name', 'organization_name']


@click.group(name=["projects", "prj"], short_help="Manage your projects")
def commands():
    """Manage your projects."""

    return


@commands.command(name="list", short_help="List projects")
@options.ORGANIZATION_NAME_OPTIONAL
@options.PROJECTS_FORMATS
def projects_list(organization_name, format_):
    """List all your projects.

    To select a project, use: `ubiops current_project set <project_name>`
    """

    client = init_client()
    projects = client.projects_list()
    if organization_name:
        projects = [i for i in projects if i.organization_name == organization_name]
    current = get_current_project()
    client.api_client.close()

    print_projects_list(projects, current, LIST_ITEMS, fmt=format_)


@commands.command(name="get", short_help="Get a project")
@options.PROJECT_NAME
@options.GET_FORMATS
def projects_get(project_name, format_):
    """Get the details of a project."""

    client = init_client()
    response = client.projects_get(project_name=project_name)
    client.api_client.close()

    print_item(response, row_attrs=LIST_ITEMS, fmt=format_)


@commands.command(name="create", short_help="Create a project")
@options.PROJECT_NAME
@options.ORGANIZATION_NAME_OPTIONAL
@options.CREATE_FORMATS
def projects_create(project_name, organization_name, format_):
    """Create a new project.

    The created project will automatically become the current project.

    When only one organization exists, it will automatically be selected.
    When multiple organizations exist and the `<organization_name>` option is not provided, the user will be prompted
    to choose the organization.

    No organization yet? Please, use the user interface and follow the registration process or contact sales.
    """

    client = init_client()

    if not organization_name:
        response = client.organizations_list()
        if len(response) == 1 and hasattr(response[0], 'name'):
            organization_name = response[0].name
        else:
            organization_name = click.prompt('Organization name')

    project = api.ProjectCreate(name=project_name, organization_name=organization_name)
    response = client.projects_create(data=project)
    client.api_client.close()

    user_config = Config()
    user_config.set('default.project', response.name)
    user_config.write()

    print_item(response, row_attrs=LIST_ITEMS, fmt=format_)


@commands.command(name="delete", short_help="Delete a project")
@options.PROJECT_NAME
@options.ASSUME_YES
@options.QUIET
def projects_delete(project_name, assume_yes, quiet):
    """Delete a project."""

    if assume_yes or click.confirm(f"Are you sure you want to delete project <{project_name}>?"):
        client = init_client()
        client.projects_delete(project_name=project_name)
        client.api_client.close()

        default_project = Config().get('default.project')
        if default_project and default_project == project_name:
            user_config = Config()
            user_config.delete_option('default.project')
            user_config.write()

        if not quiet:
            click.echo("Project was successfully deleted")

            current = get_current_project()
            if default_project == project_name and current:
                click.echo(
                    f"Current project changed to: <{current}>. Use 'ubiops current_project set <project_name>'"
                    " to update."
                )


@click.group(name=["current_project", "cprj"], short_help="Manage your current CLI project")
def current_project():
    """Manage your current CLI project."""

    return


@current_project.command(name="get", short_help="Get your current CLI project")
@options.PROJECTS_FORMATS
def current_project_get(format_):
    """Get your current CLI project."""

    current = get_current_project()

    client = init_client()
    response = client.projects_get(project_name=current)
    client.api_client.close()

    print_projects_list([response], current, LIST_ITEMS, fmt=format_)


@current_project.command(name="set", short_help="Set your current CLI project")
@options.PROJECT_NAME
@options.PROJECTS_FORMATS
def current_project_set(project_name, format_):
    """Set your current CLI project."""

    client = init_client()
    response = client.projects_get(project_name=project_name)
    client.api_client.close()

    user_config = Config()
    user_config.set(key='default.project', value=response.name)
    user_config.write()
    print_projects_list(projects=[response], current=response.name, attrs=LIST_ITEMS, fmt=format_)
