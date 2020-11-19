import yaml
import json
import click
import dateutil.parser
from tabulate import tabulate
from datetime import datetime, date
from pkg.constants import SUCCESS_STATUSES, WARNING_STATUSES, ERROR_STATUSES


def format_status(status, success_green=False):
    """Format status with color."""
    if status in SUCCESS_STATUSES:
        if success_green:
            return click.style(status, fg='green')
        else:
            return status
    if status in WARNING_STATUSES:
        return click.style(status, fg='yellow')
    if status in ERROR_STATUSES:
        return click.style(status, fg='red')
    return status


def format_boolean(value):
    """Format boolean with color."""
    if type(value) == bool:
        if value:
            return click.style(str(value), fg='green')
        else:
            return click.style(str(value), fg='red')
    return value


def format_action(action):
    """Format status with color."""
    if action == 'create':
        return click.style(action, fg='blue')
    if action == 'update':
        return click.style(action, fg='yellow')
    if action == 'delete':
        return click.style(action, fg='red')
    return action


def format_labels(labels_dict):
    """Format labels dictionary as 'key:value,key2:value'."""

    if labels_dict is None:
        return ""

    labels = []
    for k, v in labels_dict.items():
        labels.append("%s:%s" % (k, str(v)))
    return ", ".join(labels)


def parse_datetime(dt):
    """Parse ISO formatted datetime-string."""
    try:
        return dateutil.parser.parse(dt)
    except TypeError:
        pass
    return str(dt)


def format_datetime(dt, fmt='%a %b %d %Y %H:%M:%S %Z'):
    """Format datetime human readable."""
    try:
        return dt.strftime(fmt)
    except TypeError:
        pass
    return str(dt)


def object_to_dict(obj):
    """Change object to dict."""
    attributes = [k[1:] for k in obj.__dict__.keys() if k.startswith('_')]
    dictionary = {}
    for attr in attributes:
        value = getattr(obj, attr)
        if type(value) == list:
            dictionary[attr] = [object_to_dict(j) for j in value]
        else:
            dictionary[attr] = value
    return dictionary


def format_json(items):
    items = format_datetime_attrs(items, prettify=False)
    if type(items) == list:
        return json.dumps([object_to_dict(i) for i in items])
    else:
        return json.dumps(object_to_dict(items))


def format_yaml(item, required_front=None, optional=None, required_end=None, rename=None, as_str=True):
    """Change object to dict in such a way that it can be used as yaml output.
    If as_str = True: print in yaml structure.
    If as_str = False: return dictionary, which can be used to write to yaml file."""

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

    def split_lower_level_attributes(attrs):
        """If a space is used in the attribute lists, the first part is the current attribute
        and after the space is a lower level attribute. This is useful when the item contains inner-items."""
        splitted = [(a.split(" ")[0], " ".join(a.split(" ")[1:]))
                    if len(a.split(" ")) > 1 else (a, None) for a in attrs]
        grouped = {}
        for attr, inner_attr in splitted:
            if attr in grouped:
                if inner_attr is not None:
                    grouped[attr].append(inner_attr)
            else:
                if inner_attr is None:
                    grouped[attr] = []
                else:
                    grouped[attr] = [inner_attr]
        grouped = {attr: None if len(inner_attr) == 0 else inner_attr for attr, inner_attr in grouped.items()}
        return grouped

    required_front = split_lower_level_attributes(required_front)
    optional = split_lower_level_attributes(optional)
    required_end = split_lower_level_attributes(required_end)

    def set_value_in_dict(k, v, results_dict):
        """Set key k (possibly renamed by 'rename') in results_dict to value v.
        If value v is of type list, format each item in list as dictionary too."""

        key_name = rename[k] if k in rename else k
        if key_name in results_dict:
            return

        if type(v) == list:
            inner_front = required_front[k] if k in required_front else None
            inner_optional = optional[k] if k in optional else None
            inner_end = required_end[k] if k in required_end else None
            inner_rename = {" ".join(rename_key.split(' ')[1:]): rename_value
                            for rename_key, rename_value in rename.items() if rename_key.startswith('%s ' % k)}
            results_dict[key_name] = [format_yaml(j, as_str=False, required_front=inner_front, optional=inner_optional,
                                                  required_end=inner_end, rename=inner_rename) for j in v]
        else:
            results_dict[key_name] = v

    dictionary = {}
    for i in required_front.keys():
        set_value_in_dict(i, getattr(item, i), dictionary)
    for i in optional.keys():
        if hasattr(item, i) and getattr(item, i) is not None:
            set_value_in_dict(i, getattr(item, i), dictionary)
    for i in required_end.keys():
        set_value_in_dict(i, getattr(item, i), dictionary)

    if as_str:
        return yaml.dump(dictionary, sort_keys=False)
    else:
        return dictionary


def format_datetime_attrs(items, prettify=True):
    """Change datetime attributes of object(s) to formatted string.
    If prettify = True: use format_datetime() to format datetime attribute values.
    If prettify = False: use str() to format datetime attribute values."""
    def _format_date_fields(obj):
        attrs = [k[1:] for k in obj.__dict__.keys() if k.startswith('_')]
        for attr in attrs:
            if hasattr(obj, attr) and (type(getattr(obj, attr)) == datetime or type(getattr(obj, attr)) == date):
                value = getattr(obj, attr)
                value = format_datetime(value) if prettify else str(value)
                setattr(obj, attr, value)
        return obj

    if type(items) == list:
        formatted = []
        for item in items:
            formatted.append(_format_date_fields(item))
    else:
        formatted = _format_date_fields(items)

    return formatted


def print_list(items, attrs, project_name=None, rename_cols=None, sorting_col=None, fmt='table', pager=False):
    rename_cols = {} if rename_cols is None else rename_cols
    if fmt == 'json':
        click.echo(format_json(items))
    else:  # fmt == 'table'
        items = format_datetime_attrs(items)

        if len(items) > 0:
            header = [rename_cols[attr].upper() if attr in rename_cols else attr.upper()
                      for attr in attrs if hasattr(items[0], attr)]
            if project_name is not None:
                header.append('PROJECT_NAME')
        else:
            header = [rename_cols[attr].upper() if attr in rename_cols else attr.upper() for attr in attrs]

        table = []
        for i in items:
            row = []
            for attr in attrs:
                if hasattr(i, attr):
                    if attr == 'status':
                        row.append(format_status(getattr(i, attr)))
                    elif attr == 'enabled' or attr == 'success':
                        row.append(format_boolean(getattr(i, attr)))
                    elif attr == 'action':
                        row.append(format_action(getattr(i, attr)))
                    elif attr.endswith('labels'):
                        row.append(format_labels(getattr(i, attr)))
                    else:
                        row.append(getattr(i, attr))
            if project_name is not None:
                row.append(project_name)
            table.append(row)

        if sorting_col is not None:
            table = sorted(table, key=lambda x: x[sorting_col])

        if pager:
            click.echo_via_pager(tabulate(table, headers=header))
        else:
            click.echo(tabulate(table, headers=header))


def print_projects_list(projects, current, attrs, fmt='simple'):
    if fmt == 'simple':
        table = [[click.style('*', fg='yellow') if i.name == current else None, i.name] for i in projects]
        sorted_table = sorted(table, key=lambda x: x[1])
        click.echo(tabulate(sorted_table, tablefmt="plain"))
    else:
        print_list(projects, attrs, sorting_col=1, fmt=fmt)


def print_item(item, row_attrs, project_name=None, required_front=None, optional=None, required_end=None,
               rename=None, fmt='row'):
    if fmt == 'json':
        click.echo(format_json(item))
    elif fmt == 'yaml':
        click.echo(format_yaml(item, required_front=required_front, optional=optional,
                               required_end=required_end, rename=rename))
    else:  # fmt = 'row'
        print_list([item], row_attrs, project_name=project_name, rename_cols=rename, fmt='table')


def format_logs_reference(logs, extended=None):
    overview = ''
    total = len(logs)
    for i, log in enumerate(logs):
        overview += "Log: %s\n" % click.style(log.id, fg='yellow')
        overview += 'Date: %s\n' % format_datetime(parse_datetime(log.date))
        if extended:
            for attr in extended:
                if getattr(log, attr) is not None:
                    overview += '%s: %s\n' % (attr, getattr(log, attr))
        overview += '\n'
        overview += log.log
        if i + 1 < total:
            overview += '\n\n'
    return overview


def format_logs_oneline(logs):
    overview = ''
    total = len(logs)
    for i, log in enumerate(logs):
        overview += click.style(str(log.id), fg='yellow')
        overview += ' '
        overview += click.style(format_datetime(parse_datetime(log.date), '%H:%M:%S %Z'), fg='green')
        overview += ' '
        overview += log.log
        if i + 1 < total:
            overview += '\n'
    return overview


def format_requests_reference(requests, split_requests='\n\n'):
    overview = ''
    total = len(requests)
    for i, request in enumerate(requests):
        if hasattr(request, 'pipeline_object'):
            overview += 'Object: %s\n' % request.pipeline_object
        if hasattr(request, 'id') and request.id is not None:
            overview += "Id: %s\n" % click.style(str(request.id), fg='yellow')
        if hasattr(request, 'request_id') and request.request_id is not None:
            overview += "Request id: %s\n" % click.style(str(request.request_id), fg='yellow')
        if hasattr(request, 'time_created'):
            overview += 'Creation date: %s\n' % format_datetime(request.time_created)
        if hasattr(request, 'time_last_updated'):
            overview += 'Last updated date: %s\n' % format_datetime(request.time_last_updated)
        if hasattr(request, 'status'):
            overview += 'Status: %s' % format_status(request.status, success_green=True)
        elif hasattr(request, 'success'):
            if request.success:
                overview += 'Status: %s' % click.style('completed', fg='green')
            else:
                overview += 'Status: %s' % click.style('failed', fg='red')
        if hasattr(request, 'error_message') and request.error_message:
            overview += '\nError message: %s' % click.style(str(request.error_message), fg='red')
        if hasattr(request, 'request_data'):
            request_data = '-' if request.request_data is None else json.dumps(request.request_data)
            overview += '\nRequest data: %s' % request_data
        if hasattr(request, 'result'):
            request_result = '-' if request.result is None else json.dumps(request.result)
            overview += '\nResult: %s' % request_result
        if i+1 < total:
            overview += split_requests
    return overview


def format_requests_oneline(requests):
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
        elif hasattr(request, 'success'):
            if request.success:
                overview += click.style('completed ', fg='green')
            else:
                overview += click.style('failed ', fg='red')
        if hasattr(request, 'request_data'):
            overview += '-' if request.request_data is None else json.dumps(request.request_data)
            overview += ' '
        if hasattr(request, 'result'):
            overview += '-' if request.result is None else json.dumps(request.result)
        if hasattr(request, 'error_message') and request.error_message:
            overview += ' '
            overview += click.style(str(request.error_message), fg='red')
        if i+1 < total:
            overview += '\n'
    return overview


def format_pipeline_requests_reference(pipeline_requests):
    overview = ''
    total = len(pipeline_requests)
    for j, pipeline_request in enumerate(pipeline_requests):
        if hasattr(pipeline_request, 'id') and pipeline_request.id is not None:
            overview += "Pipeline request id: %s\n" % click.style(str(pipeline_request.id), fg='yellow')
        elif hasattr(pipeline_request, 'pipeline_request_id') and pipeline_request.pipeline_request_id is not None:
            overview += "Pipeline request id: %s\n" % click.style(str(pipeline_request.pipeline_request_id),
                                                                  fg='yellow')
        if hasattr(pipeline_request, 'pipeline'):
            overview += 'Pipeline: %s\n' % pipeline_request.pipeline
        if hasattr(pipeline_request, 'time_created'):
            overview += 'Creation date: %s\n' % format_datetime(pipeline_request.time_created)
        if hasattr(pipeline_request, 'status'):
            overview += 'Status: %s' % format_status(pipeline_request.status, success_green=True)
        if hasattr(pipeline_request, 'error_message') and pipeline_request.error_message:
            overview += '\nError message: %s' % click.style(str(pipeline_request.error_message), fg='red')
        if hasattr(pipeline_request, 'request_data'):
            request_data = '-' if pipeline_request.request_data is None else json.dumps(pipeline_request.request_data)
            overview += '\nPipeline request data: %s' % request_data

        if hasattr(pipeline_request, 'deployment_requests'):
            if pipeline_request.deployment_requests is not None:
                overview += '\n'
                deployment_requests = format_requests_reference(pipeline_request.deployment_requests, split_requests='\n')
                deployment_requests = "\n".join(["\n - %s" % line if line.startswith('Object') else "   %s" % line
                                           for line in deployment_requests.split("\n")])
                overview += deployment_requests

        if j+1 < total:
            overview += '\n\n'
    return overview


def format_pipeline_requests_oneline(pipeline_requests):
    overview = ''
    total = len(pipeline_requests)
    for j, pipeline_request in enumerate(pipeline_requests):
        if hasattr(pipeline_request, 'id') and pipeline_request.id is not None:
            overview += click.style(str(pipeline_request.id), fg='yellow')
            overview += ' '
        if hasattr(pipeline_request, 'pipeline_request_id') and pipeline_request.pipeline_request_id is not None:
            overview += click.style(str(pipeline_request.pipeline_request_id), fg='yellow')
            overview += ' '
        if hasattr(pipeline_request, 'pipeline'):
            overview += pipeline_request.pipeline
            overview += ' '
        if hasattr(pipeline_request, 'time_created'):
            overview += format_datetime(pipeline_request.time_created)
            overview += ' '
        if hasattr(pipeline_request, 'status'):
            overview += format_status(pipeline_request.status, success_green=True)
            overview += ' '
        if hasattr(pipeline_request, 'error_message') and pipeline_request.error_message:
            overview += ' '
            overview += click.style(str(pipeline_request.error_message), fg='red')

        if hasattr(pipeline_request, 'request_data'):
            request_data = '-' if pipeline_request.request_data is None else json.dumps(pipeline_request.request_data)
            overview += request_data

        if hasattr(pipeline_request, 'deployment_requests'):
            if pipeline_request.deployment_requests is not None:
                deployment_requests = format_requests_oneline(pipeline_request.deployment_requests)
                lines = deployment_requests.split("\n")
                if len(lines) > 0 and len(lines[0]) > 0:
                    overview += '\n'
                    deployment_requests = "\n".join([" - %s" % line for line in lines])
                overview += deployment_requests
        if j+1 < total:
            overview += '\n'
    return overview
