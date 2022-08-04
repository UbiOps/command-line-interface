import click
from ubiops_cli.utils import Config
from ubiops_cli.constants import SYS_DEPLOYMENT_FILE_NAME_VALUE
from ubiops_cli.src.helpers.deployment_helpers import DEPLOYMENT_REQUIRED_FIELDS
from ubiops_cli.src.helpers.pipeline_helpers import PIPELINE_REQUIRED_FIELDS


# General
ASSUME_YES = click.option(
    '-y', '--assume_yes', default=False, required=False, is_flag=True,
    help="Assume yes instead of asking for confirmation"
)
QUIET = click.option(
    '-q', '--quiet', default=False, required=False, is_flag=True, help="Suppress informational messages"
)
OVERWRITE = click.option(
    '--overwrite', required=False, default=False, is_flag=True, help="Whether you want to overwrite if exists"
)
OFFSET = click.option(
    '--offset', required=False, default=None, type=int, metavar='<int>',
    help="The starting point: if offset equals 2, then the first 2 records will be omitted"
)

# Formatting output
LOGS_FORMATS = click.option(
    '-fmt', '--format', 'format_',  default='oneline', help="The output format",
    type=click.Choice(['oneline', 'reference', 'extended', 'json'], case_sensitive=False), show_default=True
)
REQUESTS_FORMATS = click.option(
    '-fmt', '--format', 'format_',  default='reference', help="The output format",
    type=click.Choice(['oneline', 'reference', 'json'], case_sensitive=False), show_default=True
)
PROJECTS_FORMATS = click.option(
    '-fmt', '--format', 'format_',  default='simple', help="The output format",
    type=click.Choice(['simple', 'table', 'json'], case_sensitive=False), show_default=True
)
LIST_FORMATS = click.option(
    '-fmt', '--format', 'format_',  default='table', help="The output format",
    type=click.Choice(['table', 'json'], case_sensitive=False), show_default=True
)
CREATE_FORMATS = click.option(
    '-fmt', '--format', 'format_',  default='row', help="The output format",
    type=click.Choice(['row', 'yaml', 'json'], case_sensitive=False), show_default=True
)
GET_FORMATS = click.option(
    '-fmt', '--format', 'format_',  default='yaml', help="The output format",
    type=click.Choice(['row', 'yaml', 'json'], case_sensitive=False), show_default=True
)

# Get/Set
KEY = click.argument('key', nargs=1, required=True, metavar='<key>')
SET_VALUE = click.argument('value', nargs=1, required=True, metavar='<value>')

# Authentication
BEARER = click.option(
    '--bearer', 'type_', flag_value='bearer', default=True,
    help="Sign in with email and password [default]"
)
TOKEN = click.option('--token', 'type_', flag_value='token', help="Sign in with a service token")
API_ENDPOINT = click.option(
    '--api', 'api_endpoint', default=Config().DEFAULT_API, show_default=True,
    metavar="<endpoint>", type=click.STRING, help="The API endpoint of UbiOps"
)
EMAIL_ARGUMENT = click.argument('email', required=True, metavar="<email>", nargs=1)
EMAIL_PROMPT = click.option(
    '-e', '--email', default=None, required=False, metavar="<email>", type=click.STRING,
    help="E-mail to sign in with. User will be prompted if not specified and <token> option is not given"
)
PASSWORD_PROMPT = click.option(
    '-p', '--password', default=None, required=False, metavar="<password/token>", type=click.STRING,
    help="Password to sign in with. User will be prompted if not specified. If <token> option is given, use a service "
         "token formatted like `\"Token 1abc2def3ghi4jkl5mno6pqr7stu8vwx9yz\"`."
)

# Projects & Organizations
PROJECT_NAME = click.argument('project_name', required=True, metavar='<name>', nargs=1)
ORGANIZATION_NAME_OPTIONAL = click.option(
    '-o', '--organization_name', default=None, required=False, metavar='<name>', help="The organization name"
)

# Deployment variables
DEPLOYMENT_NAME_ARGUMENT = click.argument('deployment_name', required=True, metavar='<deployment_name>', nargs=1)
DEPLOYMENT_NAME_OPTION = click.option(
    '-d', '--deployment_name', required=True, metavar='<name>', help="The deployment name"
)
DEPLOYMENT_NAME_OPTIONAL = click.option(
    '-d', '--deployment_name', required=False, metavar='<name>', default=None, help="The deployment name"
)
DEPLOYMENT_NAME_ZIP = click.option(
    '-d', '--deployment_name', required=False, default=None, help="The deployment name used in the ZIP filename",
    metavar='<name>'
)
DEPLOYMENT_NAME_OVERRULE = click.argument(
    'deployment_name', required=False, default=None, metavar='<deployment_name>', nargs=1
)
DEPLOYMENT_NAME_UPDATE = click.option(
    '-n', '--new_name', required=False, default=None, help="The new deployment name", metavar='<name>'
)
DEPLOYMENT_YAML_FILE = click.option(
    "-f", "--yaml_file", required=True, type=click.Path(), metavar='<path>',
    help="Path to a yaml file that contains at least the following fields: [%s]" % ", ".join(DEPLOYMENT_REQUIRED_FIELDS)
)
DEPLOYMENT_YAML_FILE_OPTIONAL = click.option(
    "-f", "--yaml_file", required=False, default=None, type=click.Path(),
    help="Path to a yaml file containing deployment details", metavar='<path>'
)
DEPLOYMENT_YAML_OUTPUT = click.option(
    '-o', '--output_path', required=False, default=None, metavar='<path>',
    help="Path to file or directory to store deployment yaml file"
)
DEPLOYMENT_LABELS_OPTIONAL = click.option(
    '-lb', '--labels', 'deployment_labels', required=False, default=None, type=str, metavar='<key1:value,key2:value>',
    multiple=True, help="Labels defined as key/value pairs"
)
LABELS_FILTER = click.option(
    '-lb', '--labels', required=False, default=None, type=str, multiple=True,
    metavar='<key1:value,key2:value>', help="Labels defined as key/value pairs"
)


# Deployment/pipeline version variables
VERSION_NAME_ARGUMENT = click.argument('version_name', required=True, metavar='<version_name>', nargs=1)
VERSION_NAME_OPTION = click.option('-v', '--version_name', required=True, metavar='<name>', help="The version name")
VERSION_NAME_OPTIONAL = click.option(
    '-v', '--version_name', required=False, metavar='<name>', default=None, help="The version name"
)
DEPLOYMENT_VERSION_OPTIONAL = click.option(
    '-dv', '--deployment_version_name', required=False, metavar='<name>', default=None,
    help="The deployment version name"
)
PIPELINE_VERSION_OPTIONAL = click.option(
    '-pv', '--pipeline_version_name', required=False, metavar='<name>', default=None, help="The pipeline version name"
)

VERSION_DEFAULT_UPDATE = click.option(
    '-default', '--default_version', required=False, default=None,
    help="The name of the version that should become the default", metavar='<name>'
)
VERSION_NAME_UPDATE = click.option(
    '-n', '--new_name', required=False, default=None, help="The new version name", metavar='<name>'
)
VERSION_NAME_ZIP = click.option(
    '-v', '--version_name', required=False, default=None, metavar='<name>',
    help="The version name used in the ZIP filename"
)
VERSION_NAME_OVERRULE = click.argument('version_name', required=False, default=None, metavar='<version_name>', nargs=1)
VERSION_YAML_FILE = click.option(
    "-f", "--yaml_file", required=False, default=None, type=click.Path(), metavar='<path>',
    help="Path to a yaml file that contains version options"
)
VERSION_YAML_OUTPUT = click.option(
    '-o', '--output_path', required=False, default=None, metavar='<path>',
    help="Path to file or directory to store version yaml file"
)

LANGUAGE = click.option(
    '-l', '--language', required=False, default=None, type=click.STRING, metavar='<string>',
    help="Programming language of code"
)
MEMORY_ALLOCATION = click.option(
    '-mem', '--memory_allocation', required=False, default=None, type=int, metavar='<int>',
    help="[DEPRECATED] The reserved memory allocation for the version - deprecated and will be overruled by "
         "`instance_type`"
)
INSTANCE_TYPE = click.option(
    '-inst', '--instance_type', required=False, default=None, type=click.STRING, metavar='<string>',
    help="Reserved instance type for the version"
)
MIN_INSTANCES = click.option(
    '-min', '--minimum_instances', required=False, default=None, type=int, metavar='<int>',
    help="Minimum number of instances"
)
MAX_INSTANCES = click.option(
    '-max', '--maximum_instances', required=False, default=None, type=int, metavar='<int>',
    help="Maximum number of instances"
)
MAX_IDLE_TIME = click.option(
    '-t', '--maximum_idle_time', required=False, default=None, type=int, metavar='<int>',
    help="Maximum idle time before shutting down instance (seconds)"
)
DEPLOYMENT_MODE_DEPRECATED = click.option(
    '-dm', '--deployment_mode', required=False, default=None,
    type=click.Choice(['express', 'batch'], case_sensitive=False),
    help="[DEPRECATED] The type of the deployment version"
)
RETENTION_MODE = click.option(
    '-rtm', '--request_retention_mode', required=False, default=None,
    type=click.Choice(['none', 'metadata', 'full'], case_sensitive=False),
    help="Mode of request retention for requests to the version"
)
RETENTION_TIME = click.option(
    '-rtt', '--request_retention_time', required=False, default=None, type=int, metavar='<int>',
    help="Number of seconds to store requests to the version"
)
MAX_QUEUE_SIZE_EXPRESS = click.option(
    '-qse', '--maximum_queue_size_express', required=False, default=None, type=int, metavar='<int>',
    help="Maximum number of queued express requests to the version"
)
MAX_QUEUE_SIZE_BATCH = click.option(
    '-qsb', '--maximum_queue_size_batch', required=False, default=None, type=int, metavar='<int>',
    help="Maximum number of queued batch requests to the version"
)
VERSION_STATIC_IP = click.option(
    '--static-ip', required=False, metavar='<bool>', default=False,
    help="Whether the deployment version should get a static IP"
)

VERSION_LABELS = click.option(
    '-lb', '--labels', 'version_labels', required=False, default=None, multiple=True, type=str,
    metavar='<key1:value,key2:value>', help="Labels defined as key/value pairs"
)
VERSION_DESCRIPTION = click.option(
    '-desc', '--version_description', required=False, metavar='<string>', help="The version description"
)

# Deployment package variables
PACKAGE_DIR = click.option(
    "-dir", "--directory", required=True, type=click.Path(resolve_path=True), metavar='<path>',
    help="Path to a directory that contains at least a '%s.py'" % SYS_DEPLOYMENT_FILE_NAME_VALUE
)
IGNORE_FILE = click.option(
    '-i', '--ignore_file', 'ignore_file', required=False, default=None, metavar='<filename>',
    help="File name of ubiops-ignore file located in the root of the specified directory [default = .ubiops-ignore]"
)
DEPLOYMENT_FILE = click.option(
    '-deployment_py', '--deployment_file', required=False, default=None, type=click.STRING, metavar='<filename>',
    help="Name of deployment file which contains class Deployment. Must be located in the root of the deployment "
         "package directory"
)
ZIP_FILE = click.option(
    '-z', '--zip_path', required=True, type=click.Path(), metavar='<path>', help="Path to deployment version zip file"
)
STORE_ZIP = click.option(
    '--store_zip', required=False, default=False, is_flag=True,
    help="Whether you want to store the deployment package zip locally"
)

ZIP_OUTPUT_STORE = click.option(
    '-o', '--output_path', required=False, default=None, metavar='<path>',
    help="Path to file or directory to store local copy of deployment package zip"
)
ZIP_OUTPUT = click.option(
    '-o', '--output_path', required=False, default='', metavar='<path>',
    help="Path to file or directory to store deployment package zip"
)

# Deployment version revisions
REVISION_ID = click.argument('revision_id', required=True, metavar='<revision_id>', nargs=1)

# Deployment version builds
BUILD_ID = click.argument('build_id', required=True, metavar='<build_id>', nargs=1)
BUILD_ID_OPTIONAL = click.option(
    '-bid', '--build_id', required=False, default=None, metavar='<id>', help="The deployment version build ID"
)

# Requests
REQUEST_DATA = click.option('-d', '--data', required=True, help="The input data of the request", metavar='<string>')
REQUEST_DATA_UPDATE = click.option(
    '--data', required=False, help="The new input data of the request", metavar='<string>'
)
REQUEST_DATA_MULTI = click.option(
    '--data', required=False, help="The input data of the request", metavar='<string>', multiple=True
)
REQUEST_DATA_FILE = click.option(
    '-f', '--json_file', required=False, default=None, metavar='<path>',
    help="Path to json file containing the input data of the request"
)
REQUEST_BATCH = click.option(
    '--batch', required=False, default=False, is_flag=True,
    help="Whether you want to perform the request as batch request (async)"
)
REQUEST_ID_MULTI = click.option(
    '-id', '--request_id', required=True, metavar='<id>', multiple=True, help="The ID of the request"
)
REQUEST_ID_OPTIONAL = click.option(
    '-id', '--request_id', required=False, default=None, metavar='<id>', help="The ID of the deployment request"
)
PIPELINE_REQUEST_ID_OPTIONAL = click.option(
    '-pid', '--pipeline_request_id', required=False, default=None, metavar='<id>', help="The ID of the pipeline request"
)
REQUEST_TIMEOUT = click.option(
    '-t', '--timeout', required=False, default=None, metavar='[10-345600]', type=click.IntRange(10, 345600),
    help="Timeout in seconds"
)
REQUEST_DEPLOYMENT_TIMEOUT_DEPRECATED = click.option(
    '-t', '--timeout', required=False, default=300, type=click.IntRange(10, 3600), metavar='[10-3600]',
    show_default=True, help="Timeout in seconds"
)
REQUEST_PIPELINE_TIMEOUT_DEPRECATED = click.option(
    '-pt', '--pipeline_timeout', required=False, default=3600, type=click.IntRange(10, 7200), metavar='[10-7200]',
    show_default=True, help="Timeout for the entire pipeline request in seconds"
)
REQUEST_OBJECT_TIMEOUT = click.option(
    '-dt', '--deployment_timeout', required=False, default=None, type=click.IntRange(10, 3600), metavar='[10-3600]',
    help="Timeout for each deployment request in the pipeline in seconds"
)

# Requests list filters
REQUEST_LIMIT = click.option(
    '--limit', required=False, default=10, type=click.IntRange(1, 50), show_default=True,
    help="Limit of the number of requests. The maximum value is 50.", metavar='[1-50]'
)
REQUEST_SORT = click.option(
    '--sort', required=False, help="Direction of sorting on creation date", default='desc', show_default=True,
    type=click.Choice(['asc', 'desc'], case_sensitive=False)
)
REQUEST_FILTER_DEPLOYMENT_STATUS = click.option(
    '--status', required=False, help="Status of the request",
    type=click.Choice(
        ['pending', 'processing', 'failed', 'completed', 'cancelled_pending', 'cancelled'],
        case_sensitive=False
    )
)
REQUEST_FILTER_PIPELINE_STATUS = click.option(
    '--status', required=False, help="Status of the request", default=None,
    type=click.Choice(['pending', 'processing', 'failed', 'completed'], case_sensitive=False)
)
REQUEST_FILTER_SUCCESS = click.option(
    '--success', required=False, default=None, type=click.BOOL, metavar='[True|False]',
    help="A boolean value that indicates whether the request was successful"
)
REQUEST_FILTER_START_DATE = click.option(
    '--start_date', required=False, default=None, metavar='<datetime in iso-format>',
    help="Start date of the interval for which the requests are retrieved, "
         "looking at the creation date of the request. Formatted like '2020-01-01T00:00:00.000000Z'."
)
REQUEST_FILTER_END_DATE = click.option(
    '--end_date', required=False, default=None, metavar='<datetime in iso-format>',
    help="End date of the interval for which the requests are retrieved, "
         "looking at the creation date of the request. Formatted like '2020-01-01T00:00:00.000000Z'."
)
REQUEST_FILTER_SEARCH_ID = click.option(
    '--search_id', required=False, default=None, metavar='<name>',
    help="A string to search inside request ids. It will filter all request ids that contain this string."
)
REQUEST_FILTER_IN_PIPELINE = click.option(
    '--pipeline', required=False, default=None, type=click.BOOL, metavar='[True|False]',
    help="A boolean value that indicates whether the deployment request was part of a pipeline request"
)

# Blobs
BLOB_ID = click.argument('blob_id', required=True, metavar="<id>", nargs=1)
BLOB_PATH = click.option('-f', '--input_path', required=True, help="Path to file", metavar="<path>")
BLOB_OUTPUT = click.option(
    '-o', '--output_path', required=False, default="", metavar="<path>", help="Path to file or directory to store blob"
)
BLOB_TTL = click.option(
    '-ttl', '--time_to_live', 'ttl', required=False, default=259200, type=click.IntRange(1000, 259200),
    metavar="<seconds>", help="The time to live of the blob in seconds (default = 259200 seconds, 3 days)"
)

# Pipelines
PIPELINE_NAME_ARGUMENT = click.argument('pipeline_name', required=True, metavar='<pipeline_name>', nargs=1)
PIPELINE_NAME_OPTION = click.option('-p', '--pipeline_name', required=True, metavar='<name>', help="The pipeline name")
PIPELINE_NAME_OPTIONAL = click.option(
    '-p', '--pipeline_name', required=False, default=None, metavar='<name>', help="The pipeline name"
)
PIPELINE_NAME_OVERRULE = click.argument('pipeline_name', required=False, default=None, metavar='<name>', nargs=1)
PIPELINE_NAME_UPDATE = click.option('-n', '--new_name', required=False, default=None, help="The new pipeline name")

PIPELINE_YAML_FILE = click.option(
    "-f", "--yaml_file", required=True, type=click.Path(), metavar='<path>',
    help="Path to a yaml file that contains at least the following fields: [%s]" % ", ".join(PIPELINE_REQUIRED_FIELDS)
)
PIPELINE_YAML_FILE_UPDATE = click.option(
    "-f", "--yaml_file", required=False, default=None, type=click.Path(), metavar='<path>',
    help="Path to a yaml file that contains at least the following fields: [%s]" % ", ".join(PIPELINE_REQUIRED_FIELDS)
)
PIPELINE_YAML_OUTPUT = click.option(
    '-o', '--output_path', required=False, default=None, metavar='<path>',
    help="Path to file or directory to store pipeline yaml file"
)
PIPELINE_OBJECT_NAME = click.option(
    '-po', '--pipeline_object_name', required=False, default=None, metavar="<pipeline object name>",
    help="The pipeline object name"
)

# Environment variables
ENV_VAR_ID = click.argument('env_var_id', required=True, metavar="<id>", nargs=1)
ENV_VAR_NAME = click.argument('env_var_name', required=False, default=None, metavar="<name>", nargs=1)
ENV_VAR_NAME_UPDATE = click.option(
    '-n', '--new_name', required=False, default=False, help="The new environment variable name"
)
ENV_VAR_VALUE = click.option(
    '--value', 'env_var_value', required=False, default=None, metavar="<string>", help="Environment variable value"
)
ENV_VAR_SECRET = click.option(
    '--secret', required=False, default=False, is_flag=True, help="Store value as secret"
)
FROM_DEPLOYMENT_NAME = click.option(
    '-fd', '--from_deployment', required=True, metavar="<string>",
    help="The deployment name to copy the environment variables from"
)
FROM_VERSION_NAME = click.option(
    '-fv', '--from_version', required=False, metavar="<string>",
    help="The version name to copy the environment variables from. If None, the environment variables on deployment "
         "level are copied."
)
TO_DEPLOYMENT_NAME = click.option(
    '-td', '--to_deployment', required=True, metavar="<string>",
    help="The deployment name to copy the environment variables to"
)
TO_VERSION_NAME = click.option(
    '-tv', '--to_version', required=False, metavar="<string>",
    help="The version name to copy the environment variables to. If None, the environment variables are copied to "
         "deployment level."
)
ENV_VAR_YAML_FILE = click.option(
    "-f", "--yaml_file", required=False, default=None, type=click.Path(), metavar='<path>',
    help="Path to a yaml file that contains environment variables"
)

# Logs
SYSTEM = click.option(
    '--system', required=False, default=None, type=click.BOOL, metavar='[True|False]',
    help="Filter on logs generated by the system (true) or generated by user code (false)"
)
LEVEL = click.option(
    '--level', required=False, default=None, type=click.STRING, metavar='[info|error]',
    help="Filter on logs according to the level of the log"
)
START_DATE = click.option(
    '--start_date', required=False, default=None, metavar='<datetime in iso-format>',
    help="Start date of the interval for which the logs are retrieved. Formatted like '2020-01-01T00:00:00.000000Z'. "
         "[default = now]"
)
START_LOG = click.option(
    '--start_log', required=False, default=None, metavar='<id>',
    help="Identifier for log lines. If specified, it will act as a starting point for the interval in which to query "
         "the logs. This can be useful when making multiple queries to obtain consecutive logs. It will include the "
         "log having the log ID equal to the ID value in the response, regardless of whether the date_range is "
         "positive or negative."
)
LIMIT = click.option(
    '--limit', required=False, default=500, type=click.IntRange(1, 500), metavar='[1-500]',
    show_default=True, help="Limit of the logs response. The maximum value is 500."
)
DATE_RANGE = click.option(
    '--date_range', required=False, default=-86400, type=click.IntRange(-86400, 86400), show_default=True,
    help="Duration (seconds) of the interval for which the logs are retrieved. If it is positive, logs starting from "
         "the specified date / log ID (both inclusive) plus date range seconds towards the present time are returned. "
         "Otherwise, logs starting from the specified date / log ID (both inclusive) minus date range seconds towards "
         "the past are returned."
)
LOG_ID = click.argument('log_id', required=True, metavar='<id>', nargs=1)

# Audit events
AUDIT_LIMIT = click.option(
    '--limit', required=False, default=10, type=click.IntRange(1, 100), metavar='[1-100]',
    show_default=True, help="Limit of the audit events response. The maximum value is 100."
)
AUDIT_ACTION = click.option(
    '--action', required=False, default=None, show_default=True, help="Type of action",
    type=click.Choice(['create', 'update', 'delete', 'info'], case_sensitive=False)
)


# Scheduled requests
SCHEDULE_NAME = click.argument('schedule_name', required=True, metavar="<name>", nargs=1)
SCHEDULE_NAME_UPDATE = click.option(
    '-n', '--new_name', required=False, default=None, help="The new schedule name", metavar='<name>'
)
OBJECT_TYPE = click.option(
    '-ot', '--object_type', default="deployment", help="The object type", show_default=True,
    type=click.Choice(['deployment', 'pipeline'], case_sensitive=False)
)
OBJECT_NAME = click.option(
    '-on', '--object_name', required=True, metavar="[<deployment name>|<pipeline name>]", help="The object name"
)
OBJECT_VERSION = click.option(
    '-ov', '--object_version', required=False, metavar="<version name>",
    help="The version name. Only relevant for object_type='deployment'."
)
SCHEDULE = click.option(
    '-s', '--schedule', required=True, metavar="<0 0 1 * *>", help="Schedule in crontab format (in UTC)"
)
SCHEDULE_UPDATE = click.option(
    '-s', '--schedule', required=False, default=None, metavar="<0 0 1 * *>",
    help="New schedule in crontab format (in UTC)"
)
IS_ENABLED = click.option(
    '--enabled', required=False, default=True, type=click.BOOL, metavar='[True|False]', show_default=True,
    help="Boolean value indicating whether the created schedule is enabled or disabled"
)
IS_ENABLED_UPDATE = click.option(
    '--enabled', required=False, default=None, type=click.BOOL, metavar='[True|False]',
    help="Boolean value indicating whether the created schedule is enabled or disabled"
)

# Imports/exports
EXPORT_ID = click.argument('export_id', required=True, metavar='<export_id>', nargs=1)
EXPORT_DETAILS_YAML_OUTPUT = click.option(
    '-o', '--output_path', required=False, default=None, metavar='<path>',
    help="Path to file or directory to store export yaml file"
)
EXPORT_DETAILS_YAML_FILE = click.option(
    "-f", "--yaml_file", required=True, type=click.Path(), metavar='<path>',
    help="Path to a yaml file that contains the export details"
)
EXPORT_ZIP_OUTPUT = click.option(
    '-o', '--output_path', required=False, default='', metavar='<path>',
    help="Path to file or directory to store export zip"
)
EXPORT_STATUS_FILTER = click.option(
    '--status', required=False, default=None, type=str,  metavar='[pending|processing|completed|failed]',
    help="Status of the export"
)

IMPORT_ID = click.argument('import_id', required=True, metavar='<import_id>', nargs=1)
IMPORT_ZIP_FILE = click.option(
    '-z', '--zip_path', required=True, type=click.Path(), metavar='<path>', help="Path to import zip file"
)
IMPORT_SKIP_CONFIRMATION = click.option(
    '--skip_confirmation', required=False, default=False, is_flag=True,
    help="Whether you want to skip the confirmation step"
)
IMPORT_ZIP_OUTPUT = click.option(
    '-o', '--output_path', required=False, default='', metavar='<path>',
    help="Path to file or directory to store import zip"
)
IMPORT_CONFIRM_YAML_FILE = click.option(
    "-f", "--yaml_file", required=True, type=click.Path(), metavar='<path>',
    help="Path to a yaml file that contains the object selection for the import confirmation"
)
IMPORT_DETAILS_YAML_OUTPUT = click.option(
    '-o', '--output_path', required=False, default=None, metavar='<path>',
    help="Path to file or directory to store import yaml file"
)
IMPORT_STATUS_FILTER = click.option(
    '--status', required=False, default=None, type=str,
    metavar='[pending|scanning|confirmation|confirmation_pending|processing|completed|failed]',
    help="Status of the import"
)
