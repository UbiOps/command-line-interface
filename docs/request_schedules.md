## ubiops request_schedules

**Command:** `ubiops request_schedules`

**Alias:** `ubiops schedules`


<br/>

### ubiops request_schedules list

**Command:** `ubiops request_schedules list`

**Description:**

List request schedules in project.

The `<labels>` option can be used to filter on specific labels.

**Arguments:** - 

**Options:**

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `table`, `json`


<br/>

### ubiops request_schedules get

**Command:** `ubiops request_schedules get`

**Description:**

Get a request schedule.

If you specify the `<output_path>` option, this location will be used to store the
request schedule settings in a yaml file. You can either specify the `<output_path>` as
file or directory. If the specified `<output_path>` is a directory, the settings
will be stored in `request_schedule.yaml`.


Example of yaml content:
```
request_schedule_name: my-schedule
object_type: deployment
object_name: my-deployment
object_version: my-version
schedule: 0 8 * * 1
request_data: '{"input": "1"}'
timeout: 14400
enabled: true
request_schedule_description: Request schedule created via command line.
request_schedule_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
```

**Arguments:**

- [required] `request_schedule_name`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store request schedule yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `row`, `yaml`, `json`


<br/>

### ubiops request_schedules create

**Command:** `ubiops request_schedules create`

**Description:**

Create a request schedule. The request schedule will create a batch request to your deployment/pipeline according to
the defined schedule.


It is possible to define the parameters using a yaml file.
For example:
```
request_schedule_name: my-schedule
object_type: deployment
object_name: my-deployment
object_version: my-version
schedule: 0 8 * * 1
request_data: '{"input": "1"}'
timeout: 14400
enabled: true
request_schedule_description: Request schedule created via command line.
request_schedule_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
The request schedule name can either be passed as command argument or specified inside the yaml file using
`<request_schedule_name>`.

**Arguments:**

- `request_schedule_name`



**Options:**

- `-ot`/`--object_type`<br/>The type of the object to create a request for, default is 'deployment'

- `-on`/`--object_name`<br/>The name of the object to create a request for

- `-ov`/`--object_version`<br/>The name of the version of the object to create a request for. Don't specify to use the default version.

- `-d`/`--data`<br/>The input data of the request

- `-s`/`--schedule`<br/>Schedule in crontab format (in UTC)

- `-t`/`--timeout`<br/>Timeout in seconds

- `--enabled`<br/>Boolean value indicating whether the created schedule is enabled or disabled, default is enabled

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-desc`/`--request_schedule_description`<br/>The request schedule description

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains request schedule details

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `row`, `yaml`, `json`


<br/>

### ubiops request_schedules update

**Command:** `ubiops request_schedules update`

**Description:**

Update a request schedule.


It is possible to define the parameters using a yaml file or passing the options as command options.
For example:
```
request_schedule_name: my-schedule
object_type: deployment
object_name: my-deployment
object_version: my-version
schedule: 0 8 * * 1
request_data: '{"input": "1"}'
timeout: 14400
enabled: true
request_schedule_description: Request schedule created via command line.
request_schedule_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
```

If both a `<yaml_file>` is set and options are given, the options defined by `<yaml_file>` will be overwritten by
the specified command options.

**Arguments:**

- [required] `request_schedule_name`



**Options:**

- `-n`/`--new_name`<br/>The new schedule name

- `-d`/`--data`<br/>The input data of the request

- `-s`/`--schedule`<br/>Schedule in crontab format (in UTC)

- `-t`/`--timeout`<br/>Timeout in seconds

- `--enabled`<br/>Boolean value indicating whether the created schedule is enabled or disabled

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-desc`/`--request_schedule_description`<br/>The request schedule description

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains request schedule details

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops request_schedules delete

**Command:** `ubiops request_schedules delete`

**Description:**

Delete a request schedule.

**Arguments:**

- [required] `request_schedule_name`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
