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

Get the pipeline structure: input_type, objects and connections between the objects (attachments).

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
objects:
  - name: object1
    reference_name: my-deployment-name
    reference_version: my-deployment-version
attachments:
  - destination_name: object1
    sources:
      - source_name: pipeline_start
        mapping:
          - source_field_name: my-pipeline-param1
            destination_field_name: my-deployment-param1
```

Possible input/output types: [structured, plain]. Possible data_types: [blob, int, string, double,
bool, array_string, array_int, array_double].

All object references must exist. Connect the objects in the pipeline using attachments.
Please, connect the start of the pipeline to your first object. You can do this by creating an attachment with a
source with 'source_name: pipeline_start' and the name of your first object as destination 'destination_name: ...'.

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

If you only want to update the name of the pipeline, use the new_name option.
If you want to update anything else (and the pipeline name), please use a yaml file to define the new pipeline.

**Arguments:**

- [required] `pipeline_name`



**Options:**

- `-n`/`--new_name`<br/>The new pipeline name

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains at least the following fields: [input_type]

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

### ubiops pipelines request

**Command:** `ubiops pipelines request`

**Description:**

Create a pipeline request and retrieve the result.

For structured input, specify the data as JSON formatted string. For example:
`ubiops pipelines request <my-deployment> -v <my-version> --data "{\"param1\": 1, \"param2\": \"two\"}"`

**Arguments:**

- [required] `pipeline_name`



**Options:**

- [required] `-d`/`--data`<br/>The input data of the request

- `-pt`/`--pipeline_timeout`<br/>Timeout for the entire pipeline request in seconds

- `-dt`/`--deployment_timeout`<br/>Timeout for each deployment request in the pipeline in seconds

- `-fmt`/`--format`<br/>The output format


<br/>


***
<br/>

### ubiops pipelines batch_requests

**Command:** `ubiops pipelines batch_requests`


<br/>

#### ubiops pipelines batch_requests create

**Command:** `ubiops pipelines batch_requests create`

**Description:**

Create a pipeline batch request and retrieve request IDs to collect the results later.

Multiple data inputs can be specified at ones by using the '--data' options multiple times:
`ubiops pipelines batch_requests create <my-pipeline> --data <input-1> --data <input-2> --data <input-3>`

For structured input, specify each data input as JSON formatted string. For example:
`ubiops pipelines batch_requests create <my-pipeline> --data "{\"param1\": 1, \"param2\": \"two\"}"`

**Arguments:**

- [required] `pipeline_name`



**Options:**

- [required] `--data`<br/>The input data of the request<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

#### ubiops pipelines batch_requests get

**Command:** `ubiops pipelines batch_requests get`

**Description:**

Get the results of one or more pipeline batch requests.

Multiple request ids can be specified at ones by using the '-id' options multiple times:
`xenia pipelines batch_requests get <my-pipeline> -id <id-1> -id <id-2> -id <id-3>`

**Arguments:**

- [required] `pipeline_name`



**Options:**

- [required] `-id`/`--request_id`<br/>The ID of the request<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

#### ubiops pipelines batch_requests list

**Command:** `ubiops pipelines batch_requests list`

**Description:**

List pipeline batch requests.

**Arguments:**

- [required] `pipeline_name`



**Options:**

- `--offset`

- `--limit`<br/>Limit of the number of requests. The maximum value is 50.

- `-fmt`/`--format`<br/>The output format


<br/>
