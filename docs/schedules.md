## ubiops schedules

**Command:** `ubiops schedules`


<br/>

### ubiops schedules list

**Command:** `ubiops schedules list`

**Description:**

List request schedules in project.

**Arguments:** - 

**Options:**

- `-fmt`/`--format`<br/>The output format

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command


<br/>

### ubiops schedules create

**Command:** `ubiops schedules create`

**Description:**

Create a new request schedule.
A batch request will be created to your deployment/pipeline according to the defined schedule.

**Arguments:**

- [required] `schedule_name`



**Options:**

- `-ot`/`--object_type`<br/>The object type

- [required] `-on`/`--object_name`<br/>The object name

- `-ov`/`--object_version`<br/>The version name. Only relevant for object_type='deployment'.

- [required] `-d`/`--data`<br/>The input data of the request

- [required] `-s`/`--schedule`<br/>Schedule in crontab format (in UTC)

- `-t`/`--timeout`<br/>Timeout in seconds

- `--enabled`<br/>Boolean value indicating whether the created schedule is enabled or disabled

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops schedules update

**Command:** `ubiops schedules update`

**Description:**

Update a request schedule.

**Arguments:**

- [required] `schedule_name`



**Options:**

- `-n`/`--new_name`<br/>The new schedule name

- `--data`<br/>The new input data of the request

- `-s`/`--schedule`<br/>New schedule in crontab format (in UTC)

- `-t`/`--timeout`<br/>Timeout in seconds

- `--enabled`<br/>Boolean value indicating whether the created schedule is enabled or disabled

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops schedules get

**Command:** `ubiops schedules get`

**Description:**

Get a request schedule.

**Arguments:**

- [required] `schedule_name`



**Options:**

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops schedules delete

**Command:** `ubiops schedules delete`

**Description:**

Delete a request schedule.

**Arguments:**

- [required] `schedule_name`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
