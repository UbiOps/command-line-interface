import ubiops as api

from pkg.utils import init_client, get_current_project
from pkg.src.helpers.formatting import print_item, print_projects_list
from pkg.src.helpers.options import *


LIST_ITEMS = ['id', 'name', 'creation_date', 'organization_name']


@click.group("projects")
def commands():
    """Manage your projects."""
    pass


@commands.command("list")
@ORGANIZATION_NAME_OPTIONAL
@PROJECTS_FORMATS
def projects_list(organization_name, format_):
    """List all your projects.

    To select a project, use: `ubiops current_project set <project_name>`
    """
    client = init_client()
    projects = client.projects_list()
    if organization_name:
        projects = [i for i in projects if i.organization_name == organization_name]
    current = get_current_project()
    print_projects_list(projects, current, LIST_ITEMS, fmt=format_)


@commands.command("get")
@PROJECT_NAME
@GET_FORMATS
def projects_get(project_name, format_):
    """Get the details of a project."""
    client = init_client()
    response = client.projects_get(project_name=project_name)
    print_item(response, row_attrs=LIST_ITEMS, fmt=format_)


@commands.command("create")
@PROJECT_NAME
@ORGANIZATION_NAME_OPTIONAL
@CREATE_FORMATS
def projects_create(project_name, organization_name, format_):
    """Create a new project.

    The created project will automatically become the current project.

    When only one organization exists, it will automatically be selected.
    When multiple organizations exist and the <organization_name> option is not provided, the user will be prompted
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

    user_config = Config()
    user_config.set('default.project', response.name)
    user_config.write()

    print_item(response, row_attrs=LIST_ITEMS, fmt=format_)


@commands.command("delete")
@PROJECT_NAME
@ASSUME_YES
@QUIET
def projects_delete(project_name, assume_yes, quiet):
    """Delete a project."""

    if assume_yes or click.confirm("Are you sure you want to delete project <%s>?" % project_name):
        client = init_client()
        client.projects_delete(project_name=project_name)

        default_project = Config().get('default.project')
        if default_project and default_project == project_name:
            user_config = Config()
            user_config.delete_option('default.project')
            user_config.write()

        if not quiet:
            click.echo("Project was successfully deleted.")

            current = get_current_project()
            if default_project == project_name and current:
                click.echo("Current project changed to: <%s>. Use 'ubiops current_project set <project_name>' "
                           "to update." % current)


@click.group("current_project")
def current_project():
    """Manage your current command line interface project."""
    pass


@current_project.command("get")
@PROJECTS_FORMATS
def current_project_get(format_):
    """Get your current project of the command line interface."""

    current = get_current_project()

    client = init_client()
    response = client.projects_get(project_name=current)
    print_projects_list([response], current, LIST_ITEMS, fmt=format_)


@current_project.command("set")
@PROJECT_NAME
@PROJECTS_FORMATS
def current_project_set(project_name, format_):
    """Set your current project of the command line interface."""

    client = init_client()
    response = client.projects_get(project_name=project_name)

    user_config = Config()
    user_config.set('default.project', response.name)
    user_config.write()
    print_projects_list([response], response.name, LIST_ITEMS, fmt=format_)
