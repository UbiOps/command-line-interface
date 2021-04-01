## ubiops pipeline_versions

**Command:** `ubiops pipeline_versions`

**Alias:** `ubiops pversions`


<br/>

### ubiops pipeline_versions list

**Command:** `ubiops pipeline_versions list`

**Description:**

List the versions of a pipeline.

The `<labels>` option can be used to filter on specific labels.

**Arguments:** - 

**Options:**

- [required] `-p`/`--pipeline_name`<br/>The pipeline name

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops pipeline_versions get

**Command:** `ubiops pipeline_versions get`

**Description:**

Get the pipeline version structure: input_type, version, objects and connections between the objects (attachments).

If you specify the `<output_path>` option, this location will be used to store the
pipeline version settings in a yaml file. You can either specify the `<output_path>`
as file or directory. If the specified `<output_path>` is a directory, the settings
will be stored in `version.yaml`.


Example of yaml content:
```
pipeline_name: my-pipeline-name
input_type: structured
input_fields:
  - name: my-pipeline-param1
    data_type: int
version_name: my-version-name
version_description: Version created via command line.
version_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
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

**Arguments:**

- [required] `version_name`



**Options:**

- [required] `-p`/`--pipeline_name`<br/>The pipeline name

- `-o`/`--output_path`<br/>Path to file or directory to store version yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops pipeline_versions create

**Command:** `ubiops pipeline_versions create`

**Description:**

Create a version of a pipeline.


It is possible to define the parameters using a yaml file.
For example:
```
pipeline_name: my-pipeline-name
version_name: my-pipeline-version
version_description: Version created via command line.
version_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
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

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
The version name can either be passed as command argument or specified inside the yaml file using `<version_name>`.

**Arguments:**

- `version_name`



**Options:**

- `-p`/`--pipeline_name`<br/>The pipeline name

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-desc`/`--version_description`<br/>The version description

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains version options

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops pipeline_versions update

**Command:** `ubiops pipeline_versions update`

**Description:**

Update a version of a pipeline.


It is possible to define the parameters using a yaml file.
For example:
```
version_description: Version created via command line.
version_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
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

You can update version parameters by either providing the options in a yaml file
and passing the file path as `<yaml_file>`, or passing the options as command options.
If both a `<yaml_file>` is set and options are given, the options defined by `<yaml_file>`
will be overwritten by the specified command options.

**Arguments:**

- [required] `version_name`



**Options:**

- [required] `-p`/`--pipeline_name`<br/>The pipeline name

- `-n`/`--new_name`<br/>The new version name

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-desc`/`--version_description`<br/>The version description

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains version options

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops pipeline_versions delete

**Command:** `ubiops pipeline_versions delete`

**Description:**

Delete a version of a pipeline.

**Arguments:**

- [required] `version_name`



**Options:**

- [required] `-p`/`--pipeline_name`<br/>The pipeline name

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
