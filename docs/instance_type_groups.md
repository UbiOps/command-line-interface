## ubiops instance_type_groups

**Command:** `ubiops instance_type_groups`


<br/>

### ubiops instance_type_groups list

**Command:** `ubiops instance_type_groups list`

**Description:**

List the instance type groups in your project.

**Arguments:** - 

**Options:**

- `--limit`<br/>The maximum number of instance type groups returned, default is 50

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops instance_type_groups get

**Command:** `ubiops instance_type_groups get`

**Description:**

Get the instance type group in your project.

If you specify the `<output_path>` option, this location will be used to store the
instance type group settings in a yaml file. You can either specify the `<output_path>`
as file or directory. If the specified `<output_path>` is a directory, the settings
will be stored in `instance_type_group.yaml`.


Example of yaml content:
```
name: my-instance-type-group
instance_types:
    - id: 2aae90dd-057b-4dfd-8502-f9074aa1be0f
      name: 256mb
      display_name: 256 MB + 0.062 vCPU
      cpu: 0.062
      memory: 256.0
      storage: 1024.0
      accelerator: 0
      credit_rate: 0.25
      dedicated_node: false
      priority: 0
      schedule_timeout: 300
```

**Arguments:**

- [required] `instance_type_group_id`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store instance type group yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops instance_type_groups create

**Command:** `ubiops instance_type_groups create`

**Description:**

Create an instance type group in your project.


Define the instance type group parameters using a yaml file.
For example:
```
name: my-instance-type-group-name
instance_types:
    - id: 2aae90dd-057b-4dfd-8502-f9074aa1be0f
      priority: 0
      schedule_timeout: 300
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
The instance type group name can either be passed as command argument or specified inside the yaml file using
`<name>`.

**Arguments:**

- `name`



**Options:**

- [required] `-f`/`--yaml_file`<br/>Path to a yaml file that contains at least the following fields: [name, instance_types]

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops instance_type_groups update

**Command:** `ubiops instance_type_groups update`

**Description:**

Update an instance type group.

If you only want to update the name of the instance type group, use the option `<new_name>`.
If you want to update the instance types, please use a yaml file to define the new instance type group.


For example:
```
name: my-instance-type-group-name
instance_types:
    - id: 2aae90dd-057b-4dfd-8502-f9074aa1be0f
      priority: 0
      schedule_timeout: 300
```

**Arguments:**

- [required] `instance_type_group_id`



**Options:**

- `-n`/`--new_name`<br/>The new instance type group name

- `-f`/`--yaml_file`<br/>Path to a yaml file containing instance type group details

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops instance_type_groups delete

**Command:** `ubiops instance_type_groups delete`

**Description:**

Delete an instance type group.

**Arguments:**

- [required] `instance_type_group_id`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
