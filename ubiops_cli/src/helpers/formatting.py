import json

from datetime import datetime, date

import click
import dateutil.parser
import yaml

from tabulate import tabulate

from ubiops_cli.constants import SUCCESS_STATUSES, WARNING_STATUSES, ERROR_STATUSES


def format_status(status, success_green=False):
    """
    Format status with color; success (green|default), warning (yellow) and error (red)

    :param str status: the status to format
    :param bool success_green: whether to format success statuses with green color
    """

    if status in SUCCESS_STATUSES:
        if success_green:
            return click.style(status, fg='green')
        return status
    if status in WARNING_STATUSES:
        return click.style(status, fg='yellow')
    if status in ERROR_STATUSES:
        return click.style(status, fg='red')
    return status


def format_boolean(value):
    """
    Format boolean with color

    :param bool value: the boolean to format
    """

    if isinstance(value, bool):
        if value:
            return click.style(str(value), fg='green')
        return click.style(str(value), fg='red')
    return value


def format_action(action):
    """
    Format action with color

    :param str action: the action in the audit events
    """

    if action == 'create':
        return click.style(action, fg='blue')
    if action == 'update':
        return click.style(action, fg='yellow')
    if action == 'delete':
        return click.style(action, fg='red')
    return action


def format_labels(labels_dict):
    """
    Format labels dictionary as 'key:value,key2:value'

    :param dict labels_dict: the labels to format
    """

    if labels_dict is None:
        return ""

    labels = []
    for k, v in labels_dict.items():
        labels.append(f"{k}:{v}")
    return ", ".join(labels)


def parse_datetime(dt):
    """
    Parse ISO formatted datetime-string

    :param str dt: the datetime string to parse
    """

    try:
        return dateutil.parser.parse(dt)
    except TypeError:
        pass
    return str(dt)


def format_datetime(dt, fmt='%a %b %d %Y %H:%M:%S %Z'):
    """
    Format datetime human-readable

    :param datetime dt: the datetime to format
    :param str fmt: how to format it
    """

    if dt is None:
        return "-"

    try:
        return dt.strftime(fmt)
    except (AttributeError, TypeError):
        pass
    return str(dt)


def format_log(log, log_level):
    """
    Format log line with color depending on the log level (info or error)

    :param str log: the log to format
    :param str log_level: the log level to use; 'info' or 'error'
    """

    if log_level == 'error':
        return click.style(log, fg='red')
    return log


def object_to_dict(obj, skip_attributes=None):
    """
    Convert object to dict

    :param object obj: the object to convert
    :param list[str] skip_attributes: the object attributes to skip
    """

    if isinstance(obj, (str, dict)):
        return obj

    if skip_attributes is None:
        skip_attributes = []

    attributes = [k[1:] for k in obj.__dict__.keys() if k.startswith('_')]
    dictionary = {}
    for attr in attributes:
        if attr in skip_attributes:
            continue

        value = getattr(obj, attr)
        if isinstance(value, list):
            dictionary[attr] = [object_to_dict(j, skip_attributes=skip_attributes) for j in value]

        elif isinstance(value, (date, datetime)):
            dictionary[attr] = str(value)

        else:
            # Do not add values that are class instances
            try:
                value.__dict__.keys()
            except AttributeError:
                dictionary[attr] = value

    return dictionary


def format_json(items, skip_attributes=None):
    """
    Format object(s) as json/dict

    :param object|list[object] items: the item(s) to format
    """

    items = format_datetime_attrs(items, prettify=False)

    if isinstance(items, list):
        return json.dumps([object_to_dict(obj=i, skip_attributes=skip_attributes) for i in items])

    return json.dumps(object_to_dict(obj=items, skip_attributes=skip_attributes))


# pylint: disable=too-many-arguments
def format_yaml(item, required_front=None, optional=None, required_end=None, rename=None, as_str=True):
    """
    Change object to dict in such a way that it can be used as yaml output.
    If as_str = True: print in yaml structure.
    If as_str = False: return dictionary, which can be used to write to yaml file.

    :param object item: ubiops model to format as yaml, e.g., ubiops.models.DeploymentDetail
    :param list required_front: ubiops model attributes to show first.
        If the value is none, it will still be shown
    :param list optional: ubiops model attributes to show after the required_front.
        If the value is none, the attribute is ignored
    :param list required_end: ubiops model attributes to show after the optional attributes.
        If the value is none, it will still be shown
    :param dict rename: dictionary to rename attributes
    :param bool as_str: whether to format the yaml dict as string
    """

    if required_front is None and optional is None and required_end is None:
        required_front = [k[1:] for k in item.__dict__.keys() if k.startswith('_')]
    if required_front is None:
        required_front = []
    if optional is None:
        optional = []
    if required_end is None:
        required_end = []
    if rename is None:
        rename = {}

    required_front = _split_lower_level_attributes(required_front)
    optional = _split_lower_level_attributes(optional)
    required_end = _split_lower_level_attributes(required_end)

    def set_value_in_dict(key, value, results_dict):
        """
        Set key k (possibly renamed by 'rename') in results_dict to value v.
        If value v is of type list, format each item in list as dictionary too.

        :param str key: the key in the dict
        :param value: the value to put for the key
        :param dict results_dict: the dict to update
        """

        key_name = rename.get(key, key)
        if key_name in results_dict:
            return

        inner_front = required_front.get(key, None)
        inner_optional = optional.get(key, None)
        inner_end = required_end.get(key, None)
        inner_rename = {
            " ".join(rename_key.split(' ')[1:]): rename_value
            for rename_key, rename_value in rename.items()
            if rename_key.startswith(f"{key} ")
        }

        # Value is a list of ubiops models
        if isinstance(value, list):
            results_dict[key_name] = [
                format_yaml(
                    item=j,
                    as_str=False,
                    required_front=inner_front,
                    optional=inner_optional,
                    required_end=inner_end,
                    rename=inner_rename
                )
                for j in value
            ]
        # Value is an ubiops model
        elif inner_front or inner_optional or inner_end:
            results_dict[key_name] = format_yaml(
                item=value,
                as_str=False,
                required_front=inner_front,
                optional=inner_optional,
                required_end=inner_end,
                rename=inner_rename
            )
        else:
            results_dict[key_name] = value

    dictionary = {}
    for i in required_front.keys():
        set_value_in_dict(i, getattr(item, i), dictionary)
    for i in optional.keys():
        if hasattr(item, i) and getattr(item, i) is not None:
            set_value_in_dict(i, getattr(item, i), dictionary)
    for i in required_end.keys():
        set_value_in_dict(i, getattr(item, i), dictionary)

    if as_str:
        # Convert dictionary to yaml string, and remove last empty line
        return yaml.dump(dictionary, sort_keys=False).rstrip("\n")
    return dictionary


def format_datetime_attrs(items, prettify=True):
    """
    Change datetime attributes of object(s) to formatted string.
    If prettify = True: use format_datetime() to format datetime attribute values.
    If prettify = False: use str() to format datetime attribute values.

    :param object|list[object] items: the items to format which will be checked for datetime attributes
    :param bool prettify: whether to format datetime values to prettier strings
    """

    def _format_date_fields(obj):
        attrs = [k[1:] for k in obj.__dict__.keys() if k.startswith('_')]
        for attr in attrs:
            if hasattr(obj, attr) and isinstance(getattr(obj, attr), (date, datetime)):
                value = getattr(obj, attr)
                value = format_datetime(value) if prettify else str(value)
                setattr(obj, attr, value)

        return obj

    if isinstance(items, list):
        formatted = []
        for item in items:
            formatted.append(_format_date_fields(item))
    else:
        formatted = _format_date_fields(items)

    return formatted


# pylint: disable=too-many-arguments
# pylint: disable=too-many-branches
def print_list(items, attrs, rename_cols=None, json_skip=None, sorting_col=None, sorting_reverse=False, fmt='table',
               pager=False):
    """
    Print a list of ubiops models returned from the client library

    :param list[object] items: the items to print
    :param list[str] attrs: the attributes to print for each ubiops model
    :param dict rename_cols: if provided, attributes to rename in the columns of the table, in the form of;
        <attribute name>: <column name>
    :param list[str] json_skip: the attributes to skip when formatting to json, used to skip deprecated attributes
    :param int sorting_col: index of the attributes list to sort on
    :param bool sorting_reverse: whether to sort the column in descending order, ascending otherwise
    :param str fmt: how the object should be formatted; 'json', 'yaml' or 'row'
    :param bool pager: whether to
    """

    rename_cols = {} if rename_cols is None else rename_cols
    if fmt == 'json':
        click.echo(format_json(items, skip_attributes=json_skip))
    else:  # fmt == 'table'
        if sorting_col is not None:
            items = sorted(items, key=lambda x: getattr(x, attrs[sorting_col], ''), reverse=sorting_reverse)

        items = format_datetime_attrs(items)

        if len(items) > 0:
            header = [
                rename_cols[attr].upper() if attr in rename_cols else attr.upper()
                for attr in attrs if hasattr(items[0], attr)
            ]
        else:
            header = [
                rename_cols[attr].upper() if attr in rename_cols else attr.upper()
                for attr in attrs
            ]

        table = []
        for i in items:
            row = []
            for attr in attrs:
                if hasattr(i, attr):
                    if attr == 'status':
                        row.append(format_status(getattr(i, attr)))
                    elif attr in ['enabled', 'success']:
                        row.append(format_boolean(getattr(i, attr)))
                    elif attr == 'action':
                        row.append(format_action(getattr(i, attr)))
                    elif attr.endswith('labels'):
                        row.append(format_labels(getattr(i, attr)))
                    elif attr == 'log':
                        row.append(format_log(log=getattr(i, attr), log_level=getattr(i, 'level')))
                    # Do not show log level in the output
                    elif attr == 'level':
                        continue
                    else:
                        row.append(getattr(i, attr))
            table.append(row)

        if pager:
            click.echo_via_pager(tabulate(table, headers=header))
        else:
            click.echo(tabulate(table, headers=header))


def print_projects_list(projects, current, attrs, fmt='simple'):
    """
    Print the projects returned from the client library

    :param list[object] projects: the projects to print
    :param str current: the name of the current project
    :param list[str] attrs: the project attributes to print
    :param str fmt: how the projects should be formatted; 'simple', 'json' or 'table'
    """

    if fmt == 'simple':
        table = [
            [
                # Print yellow star in front of current project
                click.style(text='*', fg='yellow') if getattr(i, 'name') == current else None,
                getattr(i, 'name')
            ] for i in projects
        ]
        sorted_table = sorted(table, key=lambda x: x[1])
        click.echo(tabulate(sorted_table, tablefmt="plain"))
    else:
        print_list(projects, attrs, sorting_col=1, fmt=fmt)


# pylint: disable=too-many-arguments
def print_item(item, row_attrs, required_front=None, optional=None, required_end=None, rename=None, json_skip=None,
               fmt='row'):
    """
    Print an ubiops model returned from the client library

    :param object item: the item to print
    :param list[str] row_attrs: the object attributes to print as a row of a table
    :param list[str] required_front: the object attributes that should be printed first and are required; if they are
        not given or None, they will be printed as none
    :param list[str] optional: the object attributes that should be printed after the required_front attributes and are
        optoinal; if they are not given or None, they will be excluded
    :param list[str] required_end: the object attributes that should be printed last and are required; if they are not
        given or None, they will be printed as none
    :param dict rename: if provided, attributes to rename in the form of; <attribute name>: <renamed key>
    :param list[str] json_skip: the attributes to skip when formatting to json, used to skip deprecated attributes
    :param str fmt: how the object should be formatted; 'json', 'yaml' or 'row'
    """

    if fmt == 'json':
        click.echo(
            format_json(item, skip_attributes=json_skip)
        )
    elif fmt == 'yaml':
        click.echo(
            format_yaml(
                item=item,
                required_front=required_front,
                optional=optional,
                required_end=required_end,
                rename=rename
            )
        )
    elif fmt == 'row':
        print_list(items=[item], attrs=row_attrs, rename_cols=rename, fmt='table')
    else:
        raise NotImplementedError


def format_logs_reference(logs, extended=None):
    """
    Format logs to multiple lines

    :param list[object] logs: the logs to format
    :param list[str] extended: set of extra attributes to show apart from the log and date
    """

    overview = ''
    total = len(logs)
    for i, log in enumerate(logs):
        overview += f"Log: {click.style(log.id, fg='yellow')}\n"
        overview += f"Date: {format_datetime(parse_datetime(log.date))}\n"
        if extended:
            for attr in extended:
                if getattr(log, attr) is not None:
                    overview += f"{attr}: {getattr(log, attr)}\n"
        overview += '\n'

        # Change the color of the log depending on the log level
        if log.level == 'error':
            # Change the color of all lines if the log contains multiple lines
            log_lines = log.log.split('\n')
            log_line = '\n'.join([click.style(item, fg='red') for item in log_lines])
            overview += log_line
        else:
            overview += log.log

        if i + 1 < total:
            overview += '\n\n'
    return overview


def format_logs_oneline(logs):
    """
    Format logs to single lines

    :param list[object] logs: the logs to format
    """

    overview = ''
    total = len(logs)
    for i, log in enumerate(logs):
        overview += click.style(str(log.id), fg='yellow')
        overview += ' '
        overview += click.style(format_datetime(parse_datetime(log.date), '%Y-%m-%d %H:%M:%S %Z'), fg='green')
        overview += ' '

        # Change the color of the log depending on the log level
        if log.level == 'error':
            # Change the color of all lines if the log contains multiple lines
            log_lines = log.log.split('\n')
            log_line = '\n'.join([click.style(item, fg='red') for item in log_lines])
            overview += log_line
        else:
            overview += log.log
        if i + 1 < total:
            overview += '\n'

    return overview


# pylint: disable=too-many-branches
def format_requests_reference(requests, split_requests='\n\n'):
    """
    Format object requests in a pipeline request with references

    :param list[object] requests: the pipeline object requests to format
    :param str split_requests: string with which the requests are separated in the formatted string
    """

    overview = ''
    total = len(requests)

    for i, request in enumerate(requests):
        if hasattr(request, 'pipeline_object'):
            overview += f"Object: {request.pipeline_object}\n"

        if hasattr(request, 'id') and request.id is not None:
            overview += f"Request id: {click.style(str(request.id), fg='yellow')}\n"

        if hasattr(request, 'time_created'):
            overview += f"Creation date: {format_datetime(request.time_created)}\n"

        if hasattr(request, 'time_started'):
            overview += f"Start date: {format_datetime(request.time_started)}\n"

        if hasattr(request, 'time_completed'):
            overview += f"Completion date: {format_datetime(request.time_completed)}\n"

        if hasattr(request, 'operator'):
            overview += f"Operator: {request.operator}\n"

        if hasattr(request, 'deployment'):
            overview += f"Deployment: {request.deployment}\n"

        if hasattr(request, 'pipeline'):
            overview += f"Pipeline: {request.pipeline}\n"

        if hasattr(request, 'version'):
            overview += f"Version: {request.version}\n"

        if hasattr(request, 'status'):
            overview += f"Status: {format_status(status=request.status, success_green=True)}"

        if hasattr(request, 'error_message') and request.error_message:
            overview += f"\nError message: {click.style(str(request.error_message), fg='red')}"

        if hasattr(request, 'request_data'):
            request_data = '-' if request.request_data is None else json.dumps(request.request_data)
            overview += f"\nRequest data: {request_data}"

        if hasattr(request, 'result'):
            request_result = '-' if request.result is None else json.dumps(request.result)
            overview += f"\nResult: {request_result}"

        if i + 1 < total:
            overview += split_requests

    return overview


def format_requests_oneline(requests):
    """
    Format object requests in a pipeline request in one line

    :param list[object] requests: the pipeline object requests to format
    """

    overview = ''
    total = len(requests)

    for i, request in enumerate(requests):
        if hasattr(request, 'id') and request.id is not None:
            overview += click.style(str(request.id), fg='yellow')
            overview += ' '

        elif hasattr(request, 'request_id') and request.request_id is not None:
            overview += click.style(str(request.request_id), fg='yellow')
            overview += ' '

        if hasattr(request, 'pipeline_object'):
            overview += request.pipeline_object
            overview += ' '

        if hasattr(request, 'status'):
            overview += format_status(request.status, success_green=True)
            overview += ' '

        if hasattr(request, 'request_data'):
            overview += '-' if request.request_data is None else json.dumps(request.request_data)
            overview += ' '

        if hasattr(request, 'result'):
            overview += '-' if request.result is None else json.dumps(request.result)

        if hasattr(request, 'error_message') and request.error_message:
            overview += ' '
            overview += click.style(text=str(request.error_message), fg='red')

        if i + 1 < total:
            overview += '\n'

    return overview


# pylint: disable=too-many-branches
def format_pipeline_requests_reference(pipeline_requests):
    """
    Format the given pipeline requests with references

    :param list[object] pipeline_requests: the pipeline requests to format
    """

    overview = ''
    total = len(pipeline_requests)

    for j, pipeline_request in enumerate(pipeline_requests):
        if hasattr(pipeline_request, 'id') and pipeline_request.id is not None:
            overview += f"Pipeline request id: {click.style(text=str(pipeline_request.id), fg='yellow')}\n"

        if hasattr(pipeline_request, 'pipeline'):
            overview += f"Pipeline: {pipeline_request.pipeline}\n"

        if hasattr(pipeline_request, 'version'):
            overview += f"Version: {pipeline_request.version}\n"

        if hasattr(pipeline_request, 'time_created'):
            overview += f"Creation date: {format_datetime(pipeline_request.time_created)}\n"

        if hasattr(pipeline_request, 'status'):
            overview += f"Status: {format_status(pipeline_request.status, success_green=True)}"

        if hasattr(pipeline_request, 'error_message') and pipeline_request.error_message:
            overview += f"\nError message: {click.style(str(pipeline_request.error_message), fg='red')}"

        if hasattr(pipeline_request, 'request_data'):
            request_data = '-' if pipeline_request.request_data is None else json.dumps(pipeline_request.request_data)
            overview += f"\nRequest data: {request_data}"

        if hasattr(pipeline_request, 'result'):
            request_result = '-' if pipeline_request.result is None else json.dumps(pipeline_request.result)
            overview += f"\nResult: {request_result}"

        object_requests = []
        if hasattr(pipeline_request, 'deployment_requests') and isinstance(pipeline_request.deployment_requests, list):
            object_requests.extend(pipeline_request.deployment_requests)
        if hasattr(pipeline_request, 'operator_requests') and isinstance(pipeline_request.operator_requests, list):
            object_requests.extend(pipeline_request.operator_requests)
        if hasattr(pipeline_request, 'pipeline_requests') and isinstance(pipeline_request.pipeline_requests, list):
            object_requests.extend(pipeline_request.pipeline_requests)

        # Sort object requests on sequence_id
        object_requests = sorted(object_requests, key=lambda k: k.sequence_id)

        if len(object_requests) > 0:
            overview += '\n'

            requests = format_requests_reference(object_requests, split_requests='\n')
            requests = "\n".join(
                [f"\n - {line}" if line.startswith('Object') else f"   {line}"
                 for line in requests.split("\n")]
            )
            overview += requests

        if j + 1 < total:
            overview += '\n\n'

    return overview


def format_pipeline_requests_oneline(pipeline_requests):
    """
    Format the given pipeline requests in oneline

    :param list[object] pipeline_requests: the pipeline requests to format
    """

    overview = ''
    total = len(pipeline_requests)
    for j, pipeline_request in enumerate(pipeline_requests):

        if hasattr(pipeline_request, 'id') and pipeline_request.id is not None:
            overview += click.style(str(pipeline_request.id), fg='yellow')
            overview += ' '

        if hasattr(pipeline_request, 'status'):
            overview += format_status(pipeline_request.status, success_green=True)
            overview += ' '

        if hasattr(pipeline_request, 'request_data'):
            request_data = '-' if pipeline_request.request_data is None else json.dumps(pipeline_request.request_data)
            overview += request_data

        if hasattr(pipeline_request, 'result'):
            overview += ' '
            result = '-' if pipeline_request.result is None else json.dumps(pipeline_request.result)
            overview += result

        if j + 1 < total:
            overview += '\n'

    return overview


def _split_lower_level_attributes(attrs):
    """
    If a space is used in the attribute lists, the first part is the current attribute
    and after the space is a lower level attribute. This is useful when the item contains inner-items.

    :param list[str] attrs: the list of attributes to split for lower level attributes
    """

    split_lower_levels = []
    for attribute in attrs:
        attribute_levels = attribute.split(" ")
        if len(attribute_levels) > 1:
            split_lower_levels.append((attribute_levels[0],  " ".join(attribute_levels[1:])))
        else:
            split_lower_levels.append((attribute, None))

    grouped = {}
    for attr, inner_attr in split_lower_levels:
        if attr in grouped:
            if inner_attr is not None:
                grouped[attr].append(inner_attr)
        else:
            if inner_attr is None:
                grouped[attr] = []
            else:
                grouped[attr] = [inner_attr]

    grouped = {
        attr: None
        if len(inner_attr) == 0 else inner_attr
        for attr, inner_attr in grouped.items()
    }
    return grouped
