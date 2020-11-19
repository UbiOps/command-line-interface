import click
from pkg.utils import Config
from pkg.constants import SYS_DEPLOYMENT_FILE_NAME_VALUE
from pkg.src.helpers.helpers import DEPLOYMENT_REQUIRED_FIELDS, PIPELINE_REQUIRED_FIELDS


# General
ASSUME_YES = click.option('-y', '--assume_yes', default=False, required=False, is_flag=True,
                          help="Assume yes instead of asking for confirmation")
QUIET = click.option('-q', '--quiet', default=False, required=False, is_flag=True,
                     help="Suppress informational messages")
OVERWRITE = click.option('--overwrite', required=False, default=False, is_flag=True,
                         help="Whether you want to overwrite if exists")
OFFSET = click.option('--offset', required=False, default=None, type=int, metavar='<int>')

# Formatting output
LOGS_FORMATS = click.option('-fmt', '--format', 'format_',  default='reference', help="The output format",
                            type=click.Choice(['oneline', 'reference', 'extended'], case_sensitive=False),
                            show_default=True)
REQUESTS_FORMATS = click.option('-fmt', '--format', 'format_',  default='reference', help="The output format",
                                type=click.Choice(['oneline', 'reference', 'json'], case_sensitive=False),
                                show_default=True)
PROJECTS_FORMATS = click.option('-fmt', '--format', 'format_',  default='simple', help="The output format",
                                type=click.Choice(['simple', 'table', 'json'], case_sensitive=False), show_default=True)
LIST_FORMATS = click.option('-fmt', '--format', 'format_',  default='table', help="The output format",
                            type=click.Choice(['table', 'json'], case_sensitive=False), show_default=True)
CREATE_FORMATS = click.option('-fmt', '--format', 'format_',  default='row', help="The output format",
                              type=click.Choice(['row', 'yaml', 'json'], case_sensitive=False), show_default=True)
GET_FORMATS = click.option('-fmt', '--format', 'format_',  default='yaml', help="The output format",
                           type=click.Choice(['row', 'yaml', 'json'], case_sensitive=False), show_default=True)

# Get/Set
KEY = click.argument('key', nargs=1, required=True, metavar='<key>')
SET_VALUE = click.argument('value', nargs=1, required=True, metavar='<value>')

# Authentication
BEARER = click.option('--bearer', 'type_', flag_value='bearer', default=True,
                      help="Sign in with email and password [default]")
TOKEN = click.option('--token', 'type_', flag_value='token', help="Sign in with a service token")
API_ENDPOINT = click.option('--api', 'api_endpoint', default=Config().DEFAULT_API, show_default=True,
                            metavar="<endpoint>", type=click.STRING, help="The API endpoint of UbiOps")
EMAIL_ARGUMENT = click.argument('email', required=True, metavar="<email>", nargs=1)
EMAIL_PROMPT = click.option('-e', '--email', default=None, required=False, metavar="<email>", type=click.STRING,
                            help="E-mail to sign in with. User will be prompted if not specified and <token> "
                                 "option is not given")
PASSWORD_PROMPT = click.option('-p', '--password', default=None, required=False, metavar="<password/token>",
                               help="Password to sign in with. User will be prompted if not specified. If <token> "
                                    "option is given, use a service token formatted like "
                                    "`\"Token 1abc2def3ghi4jkl5mno6pqr7stu8vwx9yz\"`.", type=click.STRING)

# Projects & Organizations
PROJECT_NAME = click.argument('project_name', required=True, metavar='<name>', nargs=1)
ORGANIZATION_NAME_OPTIONAL = click.option('-o', '--organization_name', default=None, required=False, metavar='<name>',
                                          help="The organization name")

# Deployment variables
DEPLOYMENT_NAME_ARGUMENT = click.argument('deployment_name', required=True, metavar='<deployment_name>', nargs=1)
DEPLOYMENT_NAME_OPTION = click.option('-d', '--deployment_name', required=True, metavar='<name>',
                                      help="The deployment name")
DEPLOYMENT_NAME_OPTIONAL = click.option('-d', '--deployment_name', required=False, metavar='<name>', default=None,
                                        help="The deployment name")
DEPLOYMENT_NAME_ZIP = click.option('-d', '--deployment_name', required=False, default=None,
                                   help="The deployment name used in the ZIP filename", metavar='<name>')
DEPLOYMENT_NAME_OVERRULE = click.argument('deployment_name', required=False, default=None, metavar='<deployment_name>',
                                          nargs=1)
DEPLOYMENT_NAME_UPDATE = click.option('-n', '--new_name', required=False, default=None, help="The new deployment name",
                                      metavar='<name>')
DEPLOYMENT_YAML_FILE = click.option("-f", "--yaml_file", required=True, type=click.Path(), metavar='<path>',
                                    help="Path to a yaml file that contains at least the following fields: "
                                    "[%s]" % ", ".join(DEPLOYMENT_REQUIRED_FIELDS))
DEPLOYMENT_YAML_OUTPUT = click.option('-o', '--output_path', required=False, default=None, metavar='<path>',
                                      help="Path to file or directory to store deployment yaml file")
DEPLOYMENT_LABELS_OPTIONAL = click.option('-l', '--labels', 'deployment_labels', required=False, default=None,
                                          type=str, metavar='<key1:value,key2:value>', multiple=True,
                                          help="Labels defined as key/value pairs")
LABELS_FILTER = click.option('-l', '--labels', required=False, default=None, type=str, multiple=True,
                             metavar='<key1:value,key2:value>', help="Labels defined as key/value pairs")


# Deployment version variables
VERSION_NAME_ARGUMENT = click.argument('version_name', required=True, metavar='<version_name>', nargs=1)
VERSION_NAME_OPTION = click.option('-v', '--version_name', required=True, metavar='<name>',
                                   help="The version name")
VERSION_NAME_OPTIONAL = click.option('-v', '--version_name', required=False, metavar='<name>', default=None,
                                     help="The version name")
VERSION_NAME_UPDATE = click.option('-n', '--new_name', required=False, default=None,
                                   help="The new version name", metavar='<name>')
VERSION_NAME_ZIP = click.option('-v', '--version_name', required=False, default=None, metavar='<name>',
                                help="The version name used in the ZIP filename")
VERSION_NAME_OVERRULE = click.argument('version_name', required=False, default=None, metavar='<version_name>', nargs=1)
VERSION_YAML_FILE = click.option("-f", "--yaml_file", required=False, default=None, type=click.Path(), metavar='<path>',
                                 help="Path to a yaml file that contains deployment options")
VERSION_YAML_OUTPUT = click.option('-o', '--output_path', required=False, default=None, metavar='<path>',
                                   help="Path to file or directory to store version yaml file")

LANGUAGE = click.option('-l', '--language', required=False, default=None, type=click.STRING, metavar='<string>',
                        help="Programming language of code")
MEMORY_ALLOCATION = click.option('-mem', '--memory_allocation', required=False, default=None, type=int, metavar='<int>',
                                 help="Memory allocation for deployment")
MIN_INSTANCES = click.option('-min', '--minimum_instances', required=False, default=None, type=int, metavar='<int>',
                             help="Minimum number of instances")
MAX_INSTANCES = click.option('-max', '--maximum_instances', required=False, default=None, type=int, metavar='<int>',
                             help="Maximum number of instances")
MAX_IDLE_TIME = click.option('-t', '--maximum_idle_time', required=False, default=None, type=int, metavar='<int>',
                             help="Maximum idle time before shutting down instance (seconds)")

VERSION_LABELS = click.option('-l', '--labels', 'version_labels', required=False, default=None, multiple=True,
                              type=str, metavar='<key1:value,key2:value>', help="Labels defined as key/value pairs")
VERSION_DESCRIPTION = click.option('-desc', '--version_description', required=False, metavar='<string>',
                                   help="The version description")

# Deployment package variables
PACKAGE_DIR = click.option("-dir", "--directory", required=True, type=click.Path(resolve_path=True), metavar='<path>',
                           help="Path to a directory that contains at least "
                                "a '%s.py'" % SYS_DEPLOYMENT_FILE_NAME_VALUE)
IGNORE_FILE = click.option('-i', '--ignore_file', 'ignore_file', required=False, default=None, metavar='<filename>',
                           help="File name of ubiops-ignore file located in the root of the specified directory "
                                "[default = .ubiops-ignore]")
DEPLOYMENT_FILE = click.option('-deployment_py', '--deployment_file', required=False, default=None, type=click.STRING,
                               help="Name of deployment file which contains class Deployment. "
                                    "Must be located in the root of the deployment package directory",
                               metavar='<filename>')
ZIP_FILE = click.option('-z', '--zip_path', required=True, type=click.Path(), metavar='<path>',
                        help="Path to deployment version zip file")
STORE_ZIP = click.option('--store_zip', required=False, default=False, is_flag=True,
                         help="Whether you want to store the deployment package zip locally")

ZIP_OUTPUT_STORE = click.option('-o', '--output_path', required=False, default=None, metavar='<path>',
                                help="Path to file or directory to store local copy of deployment package zip")
ZIP_OUTPUT = click.option('-o', '--output_path', required=False, default='', metavar='<path>',
                          help="Path to file or directory to store deployment package zip")

# Requests
REQUEST_DATA = click.option('-d', '--data', required=True, help="The input data of the request", metavar='<string>')
REQUEST_DATA_UPDATE = click.option('--data', required=False, help="The new input data of the request",
                                   metavar='<string>')
REQUEST_DATA_MULTI = click.option('--data', required=True, help="The input data of the request",
                                  metavar='<string>', multiple=True)
REQUEST_ID_MULTI = click.option('-id', '--request_id', required=True, metavar='<id>', multiple=True,
                                help="The ID of the request")
REQUEST_ID_OPTIONAL = click.option('-id', '--request_id', required=False, default=None, metavar='<id>',
                                   help="The ID of the deployment request")
PIPELINE_REQUEST_ID_OPTIONAL = click.option('-pid', '--pipeline_request_id', required=False, default=None,
                                            metavar='<id>', help="The ID of the pipeline request")
REQUEST_LIMIT = click.option('--limit', required=False, default=10, type=click.IntRange(1, 50), show_default=True,
                             help="Limit of the number of requests. The maximum value is 50.", metavar='[1-50]')
REQUEST_TIMEOUT = click.option('--timeout', required=False, default=300, type=click.IntRange(10, 3600),
                               metavar='[10-3600]', show_default=True, help="Timeout in seconds")

# Blobs
BLOB_ID = click.argument('blob_id', required=True, metavar="<id>", nargs=1)
BLOB_PATH = click.option('-f', '--input_path', required=True, help="Path to file", metavar="<path>")
BLOB_OUTPUT = click.option('-o', '--output_path', required=False, default="", metavar="<path>",
                           help="Path to file or directory to store blob")
BLOB_TTL = click.option('-ttl', '--time_to_live', 'ttl', required=False, default=259200,
                        type=click.IntRange(1000, 259200), metavar="<seconds>",
                        help="The time to live of the blob in seconds (default = 259200 seconds, 3 days)")

# Pipelines
PIPELINE_NAME = click.argument('pipeline_name', required=True, metavar='<name>', nargs=1)
PIPELINE_NAME_OPTIONAL = click.option('-p', '--pipeline_name', required=False, default=None, metavar='<name>',
                                      help="The pipeline name")
PIPELINE_NAME_OVERRULE = click.argument('pipeline_name', required=False, default=None, metavar='<name>', nargs=1)
PIPELINE_NAME_UPDATE = click.option('-n', '--new_name', required=False, default=None, help="The new pipeline name")

PIPELINE_YAML_FILE = click.option("-f", "--yaml_file", required=True, type=click.Path(), metavar='<path>',
                                  help="Path to a yaml file that contains at least the following fields: "
                                       "[%s]" % ", ".join(PIPELINE_REQUIRED_FIELDS))
PIPELINE_YAML_FILE_UPDATE = click.option("-f", "--yaml_file", required=False, default=None, type=click.Path(),
                                         help="Path to a yaml file that contains at least the following fields: "
                                              "[%s]" % ", ".join(PIPELINE_REQUIRED_FIELDS), metavar='<path>')
PIPELINE_YAML_OUTPUT = click.option('-o', '--output_path', required=False, default=None, metavar='<path>',
                                    help="Path to file or directory to store pipeline yaml file")

# Environment variables
ENV_VAR_ID = click.argument('env_var_id', required=True, metavar="<id>", nargs=1)
ENV_VAR_NAME = click.argument('env_var_name', required=True, metavar="<name>", nargs=1)
ENV_VAR_NAME_UPDATE = click.option('-n', '--new_name', required=False, default=False,
                                   help="The new environment variable name")
ENV_VAR_VALUE = click.option('--value', 'env_var_value', required=False, default=None, metavar="<string>",
                             help="Environment variable value")
ENV_VAR_SECRET = click.option('--secret', required=False, default=False, is_flag=True,
                              help="Store value as secret")
FROM_DEPLOYMENT_NAME = click.option('-fd', '--from_deployment', required=True, metavar="<string>",
                                    help="The deployment name to copy the environment variables from")
FROM_VERSION_NAME = click.option('-fv', '--from_version', required=False, metavar="<string>",
                                 help="The version name to copy the environment variables from. "
                                      "If None, the environment variables on deployment level are copied.")
TO_DEPLOYMENT_NAME = click.option('-td', '--to_deployment', required=True, metavar="<string>",
                                  help="The deployment name to copy the environment variables to")
TO_VERSION_NAME = click.option('-tv', '--to_version', required=False, metavar="<string>",
                               help="The version name to copy the environment variables to. "
                                    "If None, the environment variables are copied to deployment level.")

# Logs
SYSTEM = click.option('--system', required=False, default=None, type=click.BOOL, metavar='[True|False]',
                      help="Filter on logs generated by the system (true) or generated by user code (false)")
START_DATE = click.option('--start_date', required=False, default=None, metavar='<datetime in iso-format>',
                          help="Start date of the interval for which the logs are retrieved. Formatted like "
                               "'2020-01-01T00:00:00.000000Z'. [default = now]")
START_LOG = click.option('--start_log', required=False, default=None, metavar='<id>',
                         help="Identifier for log lines. If specified, it will act as a starting point for the "
                              "interval in which to query the logs. This can be useful when making multiple queries "
                              "to obtain consecutive logs. It will include the log having the log id equal to the "
                              "id value in the response, regardless of whether the date_range is positive or negative.")
LIMIT = click.option('--limit', required=False, default=500, type=click.IntRange(1, 500), show_default=True,
                     help="Limit of the logs response. The maximum value is 500.")
DATE_RANGE = click.option('--date_range', required=False, default=-86400, type=click.IntRange(-86400, 86400),
                          show_default=True,
                          help="Duration (seconds) of the interval for which the logs are retrieved. If it is "
                               "positive, logs starting from the specified date / log id (both inclusive) "
                               "plus date range seconds towards the present time are returned. Otherwise, logs "
                               "starting from the specified date / log id (both inclusive) minus date range "
                               "seconds towards the past are returned.")
LOG_ID = click.argument('log_id', required=True, metavar='<id>', nargs=1)

# Audit events
AUDIT_LIMIT = click.option('--limit', required=False, default=10, type=click.IntRange(1, 100), show_default=True,
                           help="Limit of the audit events response. The maximum value is 100.")
AUDIT_OFFSET = click.option('--offset', required=False, default=0, type=int,
                            help="The number which forms the starting point of the audit events given back. If offset "
                                 "equals 2, then the first 2 events will be omitted from the list.")
AUDIT_ACTION = click.option('--action', required=False, default=None, show_default=True,
                            type=click.Choice(['create', 'update', 'delete', 'info'], case_sensitive=False),
                            help="Type of action")


# Scheduled requests
SCHEDULE_NAME = click.argument('schedule_name', required=True, metavar="<name>", nargs=1)
SCHEDULE_NAME_UPDATE = click.option('-n', '--new_name', required=False, default=None, help="The new schedule name",
                                    metavar='<name>')
OBJECT_TYPE = click.option('-ot', '--object_type', default="deployment", help="The object type",
                           type=click.Choice(['deployment', 'pipeline'], case_sensitive=False), show_default=True)
OBJECT_NAME = click.option('-on', '--object_name', required=True, metavar="[<deployment name>|<pipeline name>]",
                           help="The object name")
OBJECT_VERSION = click.option('-ov', '--object_version', required=False, metavar="<version name>",
                              help="The version name. Only relevant for object_type='deployment'.")
SCHEDULE = click.option('-s', '--schedule', required=True, metavar="<0 0 1 * *>",
                        help="Schedule in crontab format (in UTC)")
SCHEDULE_UPDATE = click.option('-s', '--schedule', required=False, default=None, metavar="<0 0 1 * *>",
                               help="New schedule in crontab format (in UTC)")
IS_BATCH_REQUEST = click.option('--batch', required=False, default=True, type=click.BOOL, metavar='[True|False]',
                                help="Boolean value indicating whether the request will be performed as "
                                     "batch request (true) or as direct request (false)", show_default=True)
IS_BATCH_REQUEST_UPDATE = click.option('--batch', required=False, default=None, type=click.BOOL, metavar='[True|False]',
                                       help="Boolean value indicating whether the request will be performed as "
                                            "batch request (true) or as direct request (false)")
IS_ENABLED = click.option('--enabled', required=False, default=True, type=click.BOOL, metavar='[True|False]',
                          help="Boolean value indicating whether the created schedule is enabled or disabled",
                          show_default=True)
IS_ENABLED_UPDATE = click.option('--enabled', required=False, default=None, type=click.BOOL, metavar='[True|False]',
                                 help="Boolean value indicating whether the created schedule is enabled or disabled")
SCHEDULE_TIMEOUT = click.option('--timeout', required=False, default=300, type=click.IntRange(10, 3600),
                                metavar='[10-3600]', show_default=True,
                                help="Timeout in seconds. This field is not used for batch requests.")
SCHEDULE_TIMEOUT_UPDATE = click.option('--timeout', required=False, default=None, type=click.IntRange(10, 3600),
                                       metavar='[10-3600]',
                                       help="Timeout in seconds. This field is not used for batch requests.")
