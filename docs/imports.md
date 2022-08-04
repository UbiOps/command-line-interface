## ubiops imports

**Command:** `ubiops imports`


<br/>

### ubiops imports list

**Command:** `ubiops imports list`

**Description:**

List all your imports in your project.

The `<status>` option can be used to filter on specific statuses.

**Arguments:** - 

**Options:**

- `--status`<br/>Status of the import

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops imports get

**Command:** `ubiops imports get`

**Description:**

Get the details of an import.

If you specify the `<output_path>` option, this location will be used to store the
import details in a yaml file. You can either specify the `<output_path>` as file or
directory. If the specified `<output_path>` is a directory, the settings will be
stored in `import.yaml`.

**Arguments:**

- [required] `import_id`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store import yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops imports create

**Command:** `ubiops imports create`

**Description:**

Create a new import by uploading a ZIP.

Please, specify the import file `<zip_path>` that should be uploaded.

**Arguments:** - 

**Options:**

- [required] `-z`/`--zip_path`<br/>Path to import zip file

- `--skip_confirmation`<br/>Whether you want to skip the confirmation step

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops imports confirm

**Command:** `ubiops imports confirm`

**Description:**

Confirm (and update) an import by selecting the objects in the import.


Define the import object selection using a yaml file.
For example:
```
deployments:
  deployment-1:
    description: My deployment
    labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    input_type: structured
    output_type: structured
    input_fields:
      - name: input
        data_type: int
    output_fields:
      - name: output
        data_type: int
    default_version: v1
    versions:
      v1:
        zip: "deployments/deployment_deployment-1/versions/deployment_deployment-1_version_v1.zip"
        description:
        language: python3.8
        maximum_idle_time: 300
        minimum_instances: 0
        maximum_instances: 5
        memory_allocation: 512
        request_retention_mode: full
        request_retention_time: 604800
        environment_variables:
          deployment_version_env_var_1:
            value: env_var_value_1
            secret: True
          deployment_version_env_var_2:
            value: env_var_value_2
            secret: False
      v2: {}
pipelines:
  pipeline-1:
    description: My pipeline
    labels:
      my-key-1: my-label-1
      my-key-2: my-label-2
    input_type: structured
    output_type: structured
    input_fields:
      - name: input
        data_type: int
    output_fields:
      - name: output
        data_type: int
    default_version: v1
    versions:
      v1:
        description:
        labels:
        request_retention_mode: full
        request_retention_time: 604800
        objects:
          - name: obj-1
            reference_name: deployment-1
            reference_type: deployment
            reference_version: v1
        attachments:
          - sources:
            - mapping:
              - source_field_name: input
                destination_field_name: input
              source_name: pipeline_start
            destination_name: obj-1
          - sources:
            - mapping:
              - source_field_name: input
                destination_field_name: output
              source_name: obj-1
            destination_name: pipeline_end
      v2: {}
```

**Arguments:**

- [required] `import_id`



**Options:**

- [required] `-f`/`--yaml_file`<br/>Path to a yaml file that contains the object selection for the import confirmation

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops imports delete

**Command:** `ubiops imports delete`

**Description:**

Delete an import.

**Arguments:**

- [required] `import_id`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops imports download

**Command:** `ubiops imports download`

**Description:**

Download an import.

The `<output_path>` option will be used as output location of the zip file. If not specified,
the current directory will be used. If the `<output_path>` is a directory, the zip will be
saved in `import_[import_id]_[datetime.now()].zip`.

**Arguments:**

- [required] `import_id`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store import zip

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
