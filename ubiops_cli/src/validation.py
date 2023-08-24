import sys

import click

from ubiops.utils import validate_requirements_file, validate_yaml_file

from ubiops_cli.src.helpers import options


@click.group(name="validate", short_help="Validate a file")
def commands():
    """
    Validate files.
    """

    return


@commands.command(name="requirements", short_help="Validate a requirements.txt file")
@options.REQUIREMENTS_FILE
def validate_requirements(requirements_file):
    """
    Validate the format of a requirements.txt file and check if the PyPi versions are available.
    """

    if validate_requirements_file(file_path=requirements_file):
        click.echo("Requirements file is valid")
    else:
        click.secho("Requirements file is not valid", fg='red')
        sys.exit(1)


@commands.command(name="yaml", short_help="Validate a ubiops.yaml file")
@options.UBIOPS_YAML_FILE
def validate_ubiops_yaml(yaml_file):
    """
    Validate the format of an UbiOps.yaml file.
    """

    if validate_yaml_file(file_path=yaml_file):
        click.echo("YAML file is valid")
    else:
        click.secho("YAML file is not valid", fg='red')
        sys.exit(1)
