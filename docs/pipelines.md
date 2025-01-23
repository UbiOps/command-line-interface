## ubiops pipelines

**Command:** `ubiops pipelines`

**Alias:** `ubiops ppl`


<br/>

### ubiops pipelines list

**Command:** `ubiops pipelines list`

**Description:**

List pipelines in project.

The <labels> option can be used to filter on specific labels.

**Arguments:** - 

**Options:**

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops pipelines get

**Command:** `ubiops pipelines get`

**Description:**

Get the pipeline settings, like, input_type and input_fields.

If you specify the <output_path> option, this location will be used to store the
pipeline structure in a yaml file. You can either specify the <output_path> as file or
directory. If the specified <output_path> is a directory, the settings will be
stored in `pipeline.yaml`.

**Arguments:**

- [required] `pipeline_name`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store pipeline yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops pipelines create

**Command:** `ubiops pipelines create`

**Description:**

Create a new pipeline.


Define the pipeline parameters using a yaml file.
For example:
```
pipeline_name: my-pipeline-name
pipeline_description: Pipeline created via command line.
pipeline_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
input_type: structured
input_fields:
  - name: my-pipeline-param1
    data_type: int
output_type: structured
output_fields:
  - name: my-pipeline-output1
    data_type: int
```

Possible input/output types: [structured, plain].
Possible data_types: [int, string, double, bool, dict, file, array_string, array_int, array_double, array_file].

**Arguments:**

- `pipeline_name`



**Options:**

- [required] `-f`/`--yaml_file`<br/>Path to a yaml file that contains at least the following fields: [input_type]

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops pipelines update

**Command:** `ubiops pipelines update`

**Description:**

Update a pipeline.

If you only want to update the name of the pipeline or the default pipeline version,
use the options `<new_name>` and `<default_version>`.
If you want to update the pipeline input/output type and fields, please use a yaml file to define the new pipeline.

Please note that it's only possible to update the input of a pipeline for pipelines that have no pipeline versions
with a connected pipeline start, that it's only possible to update the output of a pipeline for pipelines that have
no pipeline versions with a connected pipeline end.

**Arguments:**

- [required] `pipeline_name`



**Options:**

- `-n`/`--new_name`<br/>The new pipeline name

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains at least the following fields: [input_type]

- `-default`/`--default_version`<br/>The name of the version that should become the default

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops pipelines delete

**Command:** `ubiops pipelines delete`

**Description:**

Delete a pipeline.

**Arguments:**

- [required] `pipeline_name`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>


***
<br/>

### ubiops pipelines requests

**Command:** `ubiops pipelines requests`


<br/>

#### ubiops pipelines requests create

**Command:** `ubiops pipelines requests create`

**Description:**

Create a pipeline request. Use `--batch` to create a batch (asynchronous) request.
It's only possible to create a direct (synchronous) request to pipelines without 'batch' mode deployments. In
contrast, batch (asynchronous) requests can be made to any pipeline, independent on the deployment modes.

Pipeline requests are only stored for pipeline versions with `request_retention_mode` 'full' or 'metadata'.

Use the option `timeout` to specify the timeout of the pipeline request. The minimum value is 10 seconds.
The maximum value is 7200 (2 hours) for direct requests and 345600 (96 hours) for batch requests. The default value
is 3600 (1 hour) for direct requests and 14400 (4 hours) for batch requests.

Use the version option to make a request to a specific pipeline version:
`ubiops pipelines requests create <my-pipeline> -v <my-version> --data <input>`

If not specified, a request is made to the default version:
`ubiops pipelines requests create <my-pipeline> --data <input>`

Use `--batch` to make an asynchronous batch request:
`ubiops pipelines requests create <my-pipeline> --batch --data <input>`

Multiple data inputs can be specified at ones and send as batch by using the '--data' options multiple times:
`ubiops pipelines requests create <my-pipeline> --batch --data <input-1> --data <input-2> --data <input-3>`

For structured input, specify each data input as JSON formatted string. For example:
`ubiops pipelines requests create <my-pipeline> --data "{\"param1\": 1, \"param2\": \"two\"}"`

**Arguments:**

- [required] `pipeline_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- `--batch`<br/>Whether you want to perform the request as batch request (async)

- `-t`/`--timeout`<br/>Timeout in seconds

- `-dt`/`--deployment_timeout`<br/>[DEPRECATED] Timeout for each deployment request in the pipeline in seconds

- `--data`<br/>The input data of the request<br/>This option can be provided multiple times in a single command

- `-f`/`--json_file`<br/>Path to json file containing the input data of the request

- `-fmt`/`--format`<br/>The output format


<br/>

#### ubiops pipelines requests get

**Command:** `ubiops pipelines requests get`

**Description:**

Get one or more pipeline requests.
Pipeline requests are only stored for pipeline versions with `request_retention_mode` 'full' or 'metadata'.

Use the version option to get a request for a specific pipeline version.
If not specified, the request is retrieved for the default version.

Multiple request ids can be specified at ones by using the '-id' options multiple times:
`ubiops pipelines requests get <my-pipeline> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`

**Arguments:**

- [required] `pipeline_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- [required] `-id`/`--request_id`<br/>The ID of the request<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

#### ubiops pipelines requests list

**Command:** `ubiops pipelines requests list`

**Description:**

List pipeline requests.
Pipeline requests are only stored for pipeline versions with `request_retention_mode` 'full' or 'metadata'.

Use the version option to list the requests for a specific pipeline version.
If not specified, the requests are listed for the default version.

**Arguments:**

- [required] `pipeline_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- `--offset`<br/>The starting point: if offset equals 2, then the first 2 records will be omitted

- `--limit`<br/>Limit of the number of requests. The maximum value is 50.

- `--status`<br/>Status of the request

- `--start_date`<br/>Start date of the interval for which the requests are retrieved, looking at the creation date of the request. Formatted like '2020-01-01T00:00:00.000000Z'.

- `--end_date`<br/>End date of the interval for which the requests are retrieved, looking at the creation date of the request. Formatted like '2020-01-01T00:00:00.000000Z'.

- `--search_id`<br/>A string to search inside request ids. It will filter all request ids that contain this string.

- `-fmt`/`--format`<br/>The output format


<br/>
