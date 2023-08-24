import configparser
import json
import os
import zipfile

from datetime import datetime

import yaml
import click

import ubiops as api


from ubiops_cli.constants import IMPLICIT_ENVIRONMENT_FILES
from ubiops_cli.exceptions import UnAuthorizedException, UbiOpsException
from ubiops_cli.gitignorefile.gitignorefile import parse as parse_ignore
from ubiops_cli.version import VERSION


class Config:
    REQUIRED_SECTIONS = ['auth', 'default']
    DEFAULT_API_VERSION = "v2.1"
    DEFAULT_API = f"https://api.ubiops.com/{DEFAULT_API_VERSION}/"

    def __init__(self):
        basedir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(basedir, '.config')

        self.dictionary = configparser.ConfigParser()
        self.load()

    def __str__(self):
        string_list = []
        for section in self.dictionary.sections():
            options = dict(self.dictionary[section])
            for option, value in options.items():
                key = f"{section}.{option}"
                if key not in ['auth.tmp_access_token', 'auth.service_token']:
                    string_list.append(f"{key}: {value}")
        return "\n".join(string_list)

    def load(self):
        """
        Load the config from a file
        """

        self.dictionary.read(self.config_file)
        for section in self.REQUIRED_SECTIONS:
            self.check_section(section)

        # Set defaults
        if not self.dictionary.has_option('auth', 'api'):
            self.dictionary.set('auth', 'api', self.DEFAULT_API)

    def set(self, key, value):
        """
        Set the value for a key in the config

        :param str key: the key in the config, may contain sections
        :param str value: the value to put for the key
        """

        section, option = self.split_key(key)
        self.check_section(section)

        if section == 'auth' and option == 'email':
            current_email = self.get('auth.email')
            if current_email and value != current_email:
                self.delete_option('auth.tmp_access_token')
                self.delete_option('auth.service_token')

        self.dictionary.set(section, option, value)

    def get(self, key):
        """
        Get the value of an option from the config based on the key

        :param str key: the key to get the value from, may contain sections
        """
        section, option = self.split_key(key)
        if not self.dictionary.has_section(section):
            return None
        if not self.dictionary.has_option(section, option):
            return None
        return self.dictionary.get(section, option)

    def delete_option(self, key):
        """
        Delete an option from the config based on the key

        :param str key: the key to remove, may contain sections
        """

        section, option = self.split_key(key)
        if not self.dictionary.has_section(section):
            return False
        if not self.dictionary.has_option(section, option):
            return False
        self.dictionary.remove_option(section, option)
        return True

    def write(self):
        """
        Write config to file
        """

        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.dictionary.write(f)

    def check_section(self, section):
        """
        Check whether a section exists in the config, if not create it

        :param str section: the section to check
        """

        if not self.dictionary.has_section(section):
            self.dictionary.add_section(section)

    def split_key(self, key):
        """
        Split a key in section and option

        :param str key: the key to split
        """

        keys = key.split('.')
        assert len(keys) > 1, f"key does not contain a section: {key}"
        section = self.format_section(keys)
        option = keys[-1]
        return section, option

    @staticmethod
    def format_section(keys):
        """
        Format a section from keys. If subsections are given, split them with dots

        :param list[str] keys: the keys to format the sections from
        """

        section = keys[0]
        if len(keys) > 2:
            content = ".".join(keys[1:-1])
            section = f'{section} "{content}"'
        return section


# pylint: disable=broad-except
def init_client():
    """
    Initialize the client library with the credentials in the config
    """

    config_access_token = Config().get('auth.tmp_access_token')
    config_service_token = Config().get('auth.service_token')
    config_api = Config().get('auth.api')

    try:
        configuration = api.Configuration()
        configuration.host = config_api

        if config_access_token and len(config_access_token) > 0:
            configuration.api_key_prefix['Authorization'] = 'Bearer'
            configuration.api_key['Authorization'] = config_access_token
        elif config_service_token and len(config_service_token) > 0:
            configuration.api_key_prefix['Authorization'] = ''
            configuration.api_key['Authorization'] = config_service_token
        else:
            raise UbiOpsException("No access or service token found.")

        client = api.ApiClient(configuration)
        client.user_agent = f"UbiOps/cli/{VERSION}"

        core_api = api.CoreApi(client)
        assert core_api.service_status().status == 'ok'
        return core_api
    except Exception:
        raise UnAuthorizedException("Unauthorized. Please, use 'ubiops signin' first.")


def get_current_project(error=False, check_existing=False):
    """
    Get the current project from the config. If check_existing is True, we will check whether the project in the config
    still exists. If no project in the config is found, we will pick the first project in alphabetic order from the
    projects that the user has access to, and write it to the config.

    :param bool error: whether to raise an error if no project was found
    :param bool check_existing: whether the project found in the config should be check for existence
    """

    user_config = Config()
    current = user_config.get('default.project')
    if not current or check_existing:
        client = init_client()
        projects = client.projects_list()
        client.api_client.close()

        if check_existing and current:
            try:
                # Check if current project is in projects list
                if len(list(filter(lambda x: x.name == current, projects))) == 1:
                    return current
            except AttributeError:
                pass

        try:
            # Try to sort list
            projects = sorted(projects, key=lambda x: x.name)
        except AttributeError:
            pass

        # Select first project in list
        if len(projects) > 0 and hasattr(projects[0], 'name') and hasattr(projects[0], 'organization_name'):
            user_config.set(key='default.project', value=projects[0].name)
            user_config.write()
            return projects[0].name

        if error:
            raise UbiOpsException("No project found.")
        return None

    return current


def abs_path(path_param):
    """
    Get the absolute path if the path is a relative path

    :param str path_param: either a relative or absolute path
    """

    if not os.path.isabs(path_param):
        path_param = os.path.join(os.getcwd(), path_param)
    return path_param


def read_yaml(yaml_file, required_fields=None):
    """
    Read the content of a yaml file

    :param str yaml_file: the yaml file to read
    :param list[str] required_fields: the required keys in the yaml content
    """

    if yaml_file is None:
        return {}

    with open(yaml_file, encoding='utf-8') as f:
        content = yaml.safe_load(f)

    if content is None:
        content = {}

    if required_fields:
        for field_name in required_fields:
            assert (field_name in content), f"Missing field name '{field_name}' in given file."
    return content


def write_yaml(yaml_file, dictionary, default_file_name):
    """
    Write a dictionary to a yaml file

    :param str yaml_file: the output location of the yaml, either a file or directory
    :param dict dictionary: the dictionary to write to a file
    :param str default_file_name: the filename used when the output location is a directory
    """

    yaml_file = abs_path(yaml_file)
    if os.path.isdir(yaml_file):
        yaml_file = os.path.join(yaml_file, default_file_name)

    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(dictionary, f, sort_keys=False)
    return yaml_file


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
def zip_dir(directory, output_path, ignore_filename=".ubiops-ignore", deployment_name=None, version_name=None,
            force=False):
    """
    Zip a deployment package and take care of the ignore file if given

    :param str directory: the directory that should be zipped
    :param str output_path: the output location of the zip, either a file or directory
    :param str ignore_filename: the name of the ignore file
    :param str|None deployment_name: the name of the deployment, used for the default zip filename
    :param str|None version_name: the version of the deployment, used for the default zip filename
    :param bool force: whether to overwrite when the file already exists
    """

    path_dir = abs_path(directory)
    assert os.path.isdir(path_dir), "Given path is not a directory."
    has_ignore_file = os.path.isfile(os.path.join(path_dir, ignore_filename)) if ignore_filename else False

    output_path = abs_path(output_path)
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, default_version_zip_name(deployment_name, version_name))
    if not force and os.path.isfile(output_path):
        click.confirm(f"File {output_path} already exists. Do you want to overwrite it?", abort=True)

    implicit_environment = False

    # Initialize 'is_ignored' function. It will be overwritten with `parse_ignore` if a .ubiops-ignore file is present.
    def is_ignored(_):
        """
        If no ignore file is present, we will not ignore anything
        """
        return False

    if has_ignore_file:
        # Overwrite the 'is_ignored' function so we use what we found in the .ubiops-ignore file
        is_ignored = parse_ignore(os.path.join(path_dir, ignore_filename), path_dir)

    package_path = str(os.path.join(path_dir, ""))
    with zipfile.ZipFile(output_path, "w") as f:
        for root, _, files in os.walk(path_dir):
            root_subdir = os.path.join('', *root.split(package_path)[1:])
            package_subdir = os.path.join('deployment_package', root_subdir)
            for filename in files:
                source_file = os.path.join(root, filename)
                if source_file != output_path and not is_ignored(source_file):
                    if len(root_subdir.split()) == 0 and filename in IMPLICIT_ENVIRONMENT_FILES:
                        implicit_environment = True
                    f.write(source_file, os.path.join(package_subdir, filename))

    return output_path, implicit_environment


def write_blob(blob, output_path, filename=None):
    """
    Write content to a file

    :param blob: the file content
    :param str output_path: path to output location, either a file or directory
    :param str filename: the filename of the blob, used if output_path is a directory
    """

    output_path = abs_path(output_path)
    if os.path.isdir(output_path) and filename:
        output_path = os.path.join(output_path, filename)

    with open(output_path, 'wb') as f:
        f.write(blob)
    return output_path


def set_dict_default(value, defaults_dict, default_key, set_type=str):
    """
    Obtain the default value from a dict if no value was provided

    :param value: the value that should be checked for None
    :param dict defaults_dict: the dict to retrieve the default value from
    :param str default_key: the key to look for in the dict
    :param set_type: function to set the type of the default value if given
    """

    if not value and default_key in defaults_dict and defaults_dict[default_key] is not None:
        if set_type is not None:
            value = set_type(defaults_dict[default_key])
        else:
            value = defaults_dict[default_key]
    return value


def set_object_default(value, defaults_object, default_key):
    """
    Obtain the default value from an object if no value was provided

    :param value: the value that should be checked for None
    :param object defaults_object: the object to retrieve the default value from
    :param str default_key: the key to look for in the object
    """

    if not value and hasattr(defaults_object, default_key):
        value = getattr(defaults_object, default_key)
    return value


def default_version_zip_name(deployment_name, version_name):
    """
    Obtain the default name for a deployment package zip file based on deployment name and version if given

    :param str|None deployment_name: name of the deployment
    :param str|None version_name: the deployment version
    """

    datetime_str = str(datetime.now()).replace(' ', '_').replace('.', '_').replace(':', '-')
    if deployment_name and version_name:
        return f"{deployment_name}_{version_name}_{datetime_str}.zip"
    if deployment_name:
        return f"{deployment_name}_{datetime_str}.zip"
    return f"{datetime_str}.zip"


def environment_revision_zip_name(environment_name):
    """
    Generate the name of the zip file for the environment package of the given environment
    """

    datetime_str = str(datetime.now()).replace(' ', '_').replace('.', '_').replace(':', '-')
    if environment_name:
        return f"{environment_name}_{datetime_str}.zip"
    return f"{datetime_str}.zip"


def check_required_fields_in_list(input_dict, list_name, required_fields):
    """
    Check whether required fields are
    """

    assert list_name in input_dict, f"No list '{list_name}' found in {str(input_dict)}"
    for list_item in input_dict[list_name]:
        for requirement in required_fields:
            assert requirement in list_item, (
                f"No key '{requirement}' found for one of the {list_name}.\nFound: {list_item}"
            )


def read_json(json_file):
    """
    Try to read a json file
    """

    if json_file is None:
        return {}

    try:
        with open(json_file, 'rb') as f:
            content = json.load(f)
    except ValueError:
        raise ValueError("Failed to parse json file")

    if content is None:
        content = {}

    return content


def parse_json(data):
    """
    Try to parse data as json

    :param str|None data: the data to parse
    """

    if data is None:
        return {}

    try:
        return json.loads(data)
    except (TypeError, ValueError):
        raise ValueError(f"Failed to parse request data. JSON format expected. Input: {data}")


def import_export_zip_name(object_id, object_type):
    """
    Get the name of the zip file to store import/export depending on the object id and type

    :param str object_id: import or export id
    :param str object_type: either 'import' or 'export'
    """

    datetime_str = str(datetime.now()).replace(' ', '_').replace('.', '_').replace(':', '-')
    return f"{object_type}_{object_id}_{datetime_str}.zip"
