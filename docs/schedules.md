
## ubiops schedules
### ubiops schedules list

**Description:**

List request schedules in project.

**Arguments:** - 

**Options:**
- `-fmt`/`--format`

  The output format.

### ubiops schedules create

**Description:**

Create a new request schedule.

**Arguments:**
- [required] `schedule_name`

**Options:**
- `-ot`/`--object_type`

  The object type.
- [required] `-on`/`--object_name`

  The object name.
- `-ov`/`--object_version`

  The version name. Only relevant for object_type='model'.
- [required] `-d`/`--data`

  The input data of the request.
- [required] `-s`/`--schedule`

  Schedule in crontab format (in UTC)
- `--batch`

  Boolean value indicating whether the request will be performed as batch request (true) or as direct request (false)
- `--timeout`

  Timeout in seconds. This field is not used for batch requests.
- `--enabled`

  Boolean value indicating whether the created schedule is enabled or disabled.
- `-fmt`/`--format`

  The output format.

### ubiops schedules update

**Description:**

Update a request schedule.

**Arguments:**
- [required] `schedule_name`

**Options:**
- `-n`/`--new_name`

  The new schedule name.
- `-d`/`--data`

  The new input data of the request.
- `-s`/`--schedule`

  New schedule in crontab format (in UTC)
- `--batch`

  Boolean value indicating whether the request will be performed as batch request (true) or as direct request (false)
- `--timeout`

  Timeout in seconds. This field is not used for batch requests.
- `--enabled`

  Boolean value indicating whether the created schedule is enabled or disabled.
- `-fmt`/`--format`

  The output format.

### ubiops schedules get

**Description:**

Get a request schedule.

**Arguments:**
- [required] `schedule_name`

**Options:**
- `-fmt`/`--format`

  The output format.

### ubiops schedules delete

**Description:**

Delete a request schedule.

**Arguments:**
- [required] `schedule_name`

**Options:**
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation.
- `-q`/`--quiet`

  Suppress informational messages.
