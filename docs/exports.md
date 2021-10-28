## ubiops exports

**Command:** `ubiops exports`


<br/>

### ubiops exports list

**Command:** `ubiops exports list`

**Description:**

List all your exports in your project.

The `<status>` option can be used to filter on specific statuses.

**Arguments:** - 

**Options:**

- `--status`<br/>Status of the export

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops exports get

**Command:** `ubiops exports get`

**Description:**

Get the details of an export.

If you specify the `<output_path>` option, this location will be used to store the
export details in a yaml file. You can either specify the `<output_path>` as file or
directory. If the specified `<output_path>` is a directory, the settings will be
stored in `export.yaml`.

**Arguments:**

- [required] `export_id`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store export yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops exports create

**Command:** `ubiops exports create`

**Description:**

Create a new export.


Define the export objects parameters using a yaml file.
For example:
```
deployments:
  deployment-1:
    versions:
      v1:
        environment_variables:
          deployment_version_env_var_1:
            include_value: True
          deployment_version_env_var_2:
            include_value: False
      v2: {}
    environment_variables:
       deployment_env_var:
         include_value: False
pipelines:
  pipeline-1:
    versions:
      v1: {}
      v2: {}
environment_variables:
  project_env_var:
    include_value: False
```

**Arguments:** - 

**Options:**

- [required] `-f`/`--yaml_file`<br/>Path to a yaml file that contains the export details

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops exports delete

**Command:** `ubiops exports delete`

**Description:**

Delete an export.

**Arguments:**

- [required] `export_id`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops exports download

**Command:** `ubiops exports download`

**Description:**

Download an export.

The `<output_path>` option will be used as output location of the zip file. If not specified,
the current directory will be used. If the `<output_path>` is a directory, the zip will be
saved in `export_[export_id]_[datetime.now()].zip`.

**Arguments:**

- [required] `export_id`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store export zip

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
