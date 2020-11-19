import os
import ubiops as api
import configparser
from pkg.exceptions import UnAuthorizedException
from pkg.ignore.ignore import walk
from pkg.version import VERSION
from datetime import datetime

import yaml
import zipfile
import click
import json


class Config:
    REQUIRED_SECTIONS = ['auth', 'default']
    DEFAULT_API_VERSION = "v2.1"
    DEFAULT_API = "https://api.ubiops.com/%s/" % DEFAULT_API_VERSION

    def __init__(self):
        basedir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(basedir, '.config')

        self.dictionary = configparser.ConfigParser()
        self.load()

    def __str__(self):
        string_list = []
        for section in self.dictionary.sections():
            d = dict(self.dictionary[section])
            for k, value in d.items():
                key = "%s.%s" % (section, k)
                if key != 'auth.tmp_access_token' and key != 'auth.service_token':
                    string_list.append("%s: %s" % (key, value))
        return "\n".join(string_list)

    def load(self):
        self.dictionary.read(self.config_file)
        for section in self.REQUIRED_SECTIONS:
            self.check_section(section)

        # Set defaults
        if not self.dictionary.has_option('auth', 'api'):
            self.dictionary.set('auth', 'api', self.DEFAULT_API)

    def set(self, key, value):
        section, option = self.split_key(key)
        self.check_section(section)

        if section == 'auth' and option == 'email':
            current_email = self.get('auth.email')
            if current_email and value != current_email:
                self.delete_option('auth.tmp_access_token')
                self.delete_option('auth.service_token')

        self.dictionary.set(section, option, value)

    def get(self, key):
        section, option = self.split_key(key)
        if not self.dictionary.has_section(section):
            return None
        if not self.dictionary.has_option(section, option):
            return None
        return self.dictionary.get(section, option)

    def delete_option(self, key):
        section, option = self.split_key(key)
        if not self.dictionary.has_section(section):
            return False
        if not self.dictionary.has_option(section, option):
            return False
        self.dictionary.remove_option(section, option)
        return True

    def write(self):
        with open(self.config_file, 'w') as f:
            self.dictionary.write(f)

    def check_section(self, section):
        if not self.dictionary.has_section(section):
            self.dictionary.add_section(section)

    def split_key(self, key):
        keys = key.split('.')
        assert len(keys) > 1, "key does not contain a section: %s" % key
        section = self.format_section(keys)
        option = keys[-1]
        return section, option

    @staticmethod
    def format_section(keys):
        section = keys[0]
        if len(keys) > 2:
            section = '%s "%s"' % (section, ".".join(keys[1:-1]))
        return section


def init_client():
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
            raise Exception("No access or service token found.")

        client = api.CoreApi(api.ApiClient(configuration))
        client.user_agent = "UbiOps/cli/%s" % VERSION
        assert client.service_status().status == 'ok'
        return client
    except Exception:
        raise UnAuthorizedException("Unauthorized. Please, use 'ubiops signin' first.")


def get_current_project(error=False):
    user_config = Config()
    current = user_config.get('default.project')
    if not current:
        client = init_client()
        projects = client.projects_list()
        client.api_client.close()
        try:
            # try to sort list
            projects = sorted(projects, key=lambda x: x.name)
        except AttributeError:
            pass

        if len(projects) > 0 and hasattr(projects[0], 'name') and hasattr(projects[0], 'organization_name'):
            user_config.set('default.project', projects[0].name)
            user_config.write()
            return projects[0].name
        else:
            if error:
                raise Exception("No project found.")
            return None
    return current


def abs_path(path_param):
    if not os.path.isabs(path_param):
        path_param = os.path.join(os.getcwd(), path_param)
    return path_param


def read_yaml(yaml_file, required_fields=None):
    if yaml_file is None:
        return {}

    with open(yaml_file) as f:
        content = yaml.safe_load(f)
    if required_fields:
        for field_name in required_fields:
            assert (field_name in content), "Missing field name '%s' in given file." % field_name
    return content


def write_yaml(yaml_file, dictionary, default_file_name):
    yaml_file = abs_path(yaml_file)
    if os.path.isdir(yaml_file):
        yaml_file = os.path.join(yaml_file, default_file_name)

    with open(yaml_file, 'w') as f:
        yaml.dump(dictionary, f, sort_keys=False)
    return yaml_file


def zip_dir(directory, output_path, ignore_filename=".ubiops-ignore", deployment_name=None, version_name=None,
            force=False):
    path_dir = abs_path(directory)
    assert os.path.isdir(path_dir), "Given path is not a directory."
    has_ignore_file = os.path.isfile(os.path.join(path_dir, ignore_filename)) if ignore_filename else False

    output_path = abs_path(output_path)
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, default_version_zip_name(deployment_name, version_name))
    if not force and os.path.isfile(output_path):
        click.confirm("File %s already exists. Do you want to overwrite it?" % output_path, abort=True)

    package_path = str(os.path.join(path_dir, ""))
    with zipfile.ZipFile(output_path, "w") as zf:
        for r, d, files in walk(path_dir, filename=ignore_filename) if has_ignore_file else os.walk(path_dir):
            root_subdir = os.path.join('', *r.split(package_path)[1:])
            package_subdir = os.path.join('deployment_package', root_subdir)
            for filename in files:
                if os.path.join(r, filename) != output_path:
                    zf.write(os.path.join(r, filename), os.path.join(package_subdir, filename))
    return output_path


def write_blob(blob, output_path, filename=None):
    output_path = abs_path(output_path)
    if os.path.isdir(output_path) and filename:
        output_path = os.path.join(output_path, filename)

    with open(output_path, 'wb') as f:
        f.write(blob)
    return output_path


def set_dict_default(value, defaults_dict, default_key, set_type=str):
    if not value and default_key in defaults_dict:
        value = set_type(defaults_dict[default_key])
    return value


def set_object_default(value, defaults_object, default_key):
    if not value and hasattr(defaults_object, default_key):
        value = getattr(defaults_object, default_key)
    return value


def default_version_zip_name(deployment_name, version_name):
    datetime_str = str(datetime.now()).replace(' ', '_').replace('.', '_').replace(':', '-')
    if deployment_name and version_name:
        return "%s_%s_%s.zip" % (deployment_name, version_name, datetime_str)
    elif deployment_name:
        return "%s_%s.zip" % (deployment_name, datetime_str)
    else:
        return "%s.zip" % datetime_str


def check_required_fields(input_dict, list_name, required_fields):
    for list_item in input_dict[list_name]:
        for requirement in required_fields:
            assert requirement in list_item, "No '%s' found for one of the %s." \
                                             "\nFound: %s" % (requirement, list_name, str(list_item))


def parse_json(data):
    if data is None:
        return {}

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        raise Exception("Failed to parse request data. JSON format expected. Input: %s" % str(data))
