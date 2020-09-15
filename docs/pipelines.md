
## ubiops pipelines
### ubiops pipelines list

**Description:**

List pipelines in project.

**Arguments:** - 

**Options:**
- `-fmt`/`--format`

  The output format.

### ubiops pipelines get

**Description:**

Get the pipeline structure: input_type, objects and connections between the objects (attachments).

If you specify the <output_path> option, this location will be used to store the
pipeline structure in a yaml file. You can either specify the <output_path> as file or
directory. If the specified <output_path> is a directory, the settings will be
stored in `pipeline.yaml`.

**Arguments:**
- [required] `pipeline_name`

**Options:**
- `-o`/`--output_path`

  Path to file or directory to store pipeline yaml file.
- `-q`/`--quiet`

  Suppress informational messages.
- `-fmt`/`--format`

  The output format.

### ubiops pipelines create

**Description:**

Create a new pipeline.


Define the pipeline parameters using a yaml file.
For example:
```
pipeline_name: my-pipeline-name
pipeline_description: Pipeline created via command line.
input_type: structured
input_fields:
  - name: my-pipeline-param1
    data_type: int
objects:
  - name: object1
    reference_type: model
    reference_name: my-model-name
    reference_version: my-model-version
attachments:
  - source_name: pipeline_start
    destination_name: object1
    mapping:
    - source_field_name: my-pipeline-param1
      destination_field_name: my-model-param1
```

Possible input/output types: [structured, plain]. Possible data_types: [blob, int, string, double,
bool, array_string, array_int, array_double].

All object references must exist. Connect the objects in the pipeline using attachments.
Please, connect the start of the pipeline to your first object. You can do this by creating an attachment with
'source_name: pipeline_start' and the name of your first object as destination 'destination_name: ...'.

**Arguments:**
- `pipeline_name`

**Options:**
- [required] `-f`/`--yaml_file`

  Path to a yaml file that contains at least the following fields: [input_type].
- `-fmt`/`--format`

  The output format.

### ubiops pipelines update

**Description:**

Update a pipeline.

If you only want to update the name of the pipeline, use the new_name option.
If you want to update anything else (and the pipeline name), please use a yaml file to define the new pipeline.

**Arguments:**
- [required] `pipeline_name`

**Options:**
- `-n`/`--new_name`

  The new pipeline name.
- `-f`/`--yaml_file`

  Path to a yaml file that contains at least the following fields: [input_type].
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops pipelines delete

**Description:**

Delete a pipeline.

**Arguments:**
- [required] `pipeline_name`

**Options:**
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation.
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops pipelines request

**Description:**

Create a pipeline request and retrieve the result.

For structured input, specify the data as JSON formatted string. For example:
`ubiops pipelines request <my-model> -v <my-version> -d "{"param1": 1, "param2": "two"}"`

**Arguments:**
- [required] `pipeline_name`

**Options:**
- [required] `-d`/`--data`

  The input data of the request.
- `-fmt`/`--format`

  The output format.

### ubiops pipelines batch_requests
#### ubiops pipelines batch_requests create

**Description:**

Create a pipeline batch request and retrieve request IDs to collect the results later.

Multiple data inputs can be specified at ones by using the '-d' options multiple times:
`ubiops pipelines batch_requests create <my-pipeline> -d <input-1> -d <input-2> -d <input-3>`

For structured input, specify each data input as JSON formatted string. For example:
`ubiops pipelines batch_requests create <my-pipeline> -d "{"param1": 1, "param2": "two"}"`

**Arguments:**
- [required] `pipeline_name`

**Options:**
- [required] `-d`/`--data`

  The input data of the request.

  This option can be provided multiple times in a single command.
- `-fmt`/`--format`

  The output format.

#### ubiops pipelines batch_requests get

**Description:**

Get the results of one or more pipeline batch requests.

Multiple request ids can be specified at ones by using the '-id' options multiple times:
`xenia pipelines batch_requests get <my-pipeline> -id <id-1> -id <id-2> -id <id-3>`

**Arguments:**
- [required] `pipeline_name`

**Options:**
- [required] `-id`/`--request_id`

  The ID of the request.

  This option can be provided multiple times in a single command.
- `-fmt`/`--format`

  The output format.

#### ubiops pipelines batch_requests list

**Description:**

List pipeline batch requests.

**Arguments:**
- [required] `pipeline_name`

**Options:**
- `--offset`
- `--limit`

  Limit of the number of requests. The maximum value is 50.
- `-fmt`/`--format`

  The output format.
