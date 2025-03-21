## ubiops logs

**Command:** `ubiops logs`


<br/>

### ubiops logs list

**Command:** `ubiops logs list`

**Description:**

Get the logs of your project.

Use the command options as filters.

**Arguments:** - 

**Options:**

- `-d`/`--deployment_name`<br/>The deployment name

- `-dv`/`--deployment_version_name`<br/>The deployment version name

- `-p`/`--pipeline_name`<br/>The pipeline name

- `-pv`/`--pipeline_version_name`<br/>The pipeline version name

- `-po`/`--pipeline_object_name`<br/>The pipeline object name

- `-bid`/`--build_id`<br/>The deployment version build ID

- `-id`/`--request_id`<br/>The ID of the deployment request

- `-pid`/`--pipeline_request_id`<br/>The ID of the pipeline request

- `--system`<br/>Filter on logs generated by the system (true) or generated by user code (false)

- `--level`<br/>Filter on logs according to the level of the log

- `--start_date`<br/>Start date of the interval for which the logs are retrieved. Formatted like '2020-01-01T00:00:00.000000Z'. [default = now]

- `--start_log`<br/>Identifier for log lines. If specified, it will act as a starting point for the interval in which to query the logs. This can be useful when making multiple queries to obtain consecutive logs. It will include the log having the log ID equal to the ID value in the response, regardless of whether the date_range is positive or negative.

- `--date_range`<br/>Duration (seconds) of the interval for which the logs are retrieved. If it is positive, logs starting from the specified date / log ID (both inclusive) plus date range seconds towards the present time are returned. Otherwise, logs starting from the specified date / log ID (both inclusive) minus date range seconds towards the past are returned.

- `--limit`<br/>Limit of the logs response. The maximum value is 500.

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops logs get

**Command:** `ubiops logs get`

**Description:**

Get more details of a log:
- date
- deployment_name
- deployment_version_name
- pipeline_name
- pipeline_version_name
- pipeline_object_name
- deployment_request_id
- pipeline_request_id
- system (boolean)
- level
- build_id

**Arguments:**

- [required] `log_id`



**Options:**

- `-fmt`/`--format`<br/>The output format


<br/>
