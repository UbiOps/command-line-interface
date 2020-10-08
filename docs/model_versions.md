
## ubiops model_versions
### ubiops model_versions list

**Description:**

List the versions of a model.

**Arguments:** - 

**Options:**
- [required] `-m`/`--model_name`

  The model name.
- `-fmt`/`--format`

  The output format.

### ubiops model_versions get

**Description:**

Get the version of a model.

If you specify the <output_path> option, this location will be used to store the
model version settings in a yaml file. You can either specify the <output_path> as file or
directory. If the specified <output_path> is a directory, the settings will be
stored in `version.yaml`.


Example of yaml content:
```
version_name: my-version
model_name: my-model
language: python3.7
memory_allocation: 2048
minimum_instances: 0
maximum_instances: 5
maximum_idle_time: 300
```

**Arguments:**
- [required] `version_name`

**Options:**
- [required] `-m`/`--model_name`

  The model name.
- `-o`/`--output_path`

  Path to file or directory to store version yaml file.
- `-q`/`--quiet`

  Suppress informational messages.
- `-fmt`/`--format`

  The output format.

### ubiops model_versions create

**Description:**

Create a version of a model.


It is possible to define the parameters using a yaml file.
For example:
```
version_name: my-model-version
model_name: my-model-name
language: python3.6
memory_allocation: 256
minimum_instances: 0
maximum_instances: 1
maximum_idle_time: 300
```

Those parameters can also be provided as command options. If both a <yaml_file> is set and
options are given, the options defined by <yaml_file> will be overwritten by the specified command options.
The version name can either be passed as command argument or specified inside the yaml file using <version_name>.

**Arguments:**
- `version_name`

**Options:**
- `-m`/`--model_name`

  The model name.
- `-l`/`--language`

  Programming language of code.
- `-mem`/`--memory_allocation`

  Memory allocation for model.
- `-min`/`--minimum_instances`

  Minimum number of instances.
- `-max`/`--maximum_instances`

  Maximum number of instances.
- `-t`/`--maximum_idle_time`

  Maximum idle time before shutting down instance (seconds).
- `-f`/`--yaml_file`

  Path to a yaml file that contains deployment options
- `-model_py`/`--model_file`

  Name of model file which contains class Model. Must be located in the root of the model package directory.
- `-fmt`/`--format`

  The output format.

### ubiops model_versions update

**Description:**

Update a version of a model.

You may want to change some deployment options, like, programming <language> and
<memory_allocation>. You can do this by either providing the options in a yaml file
and passing the file path as <yaml_file>, or passing the options as command options.
If both a <yaml_file> is set and options are given, the options defined by <yaml_file>
will be overwritten by the specified command options.

**Arguments:**
- [required] `version_name`

**Options:**
- [required] `-m`/`--model_name`

  The model name.
- `-n`/`--new_name`

  The new model version name.
- `-model_py`/`--model_file`

  Name of model file which contains class Model. Must be located in the root of the model package directory.
- `-f`/`--yaml_file`

  Path to a yaml file that contains deployment options
- `-l`/`--language`

  Programming language of code.
- `-mem`/`--memory_allocation`

  Memory allocation for model.
- `-min`/`--minimum_instances`

  Minimum number of instances.
- `-max`/`--maximum_instances`

  Maximum number of instances.
- `-t`/`--maximum_idle_time`

  Maximum idle time before shutting down instance (seconds).
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops model_versions delete

**Description:**

Delete a version of a model.

**Arguments:**
- [required] `version_name`

**Options:**
- [required] `-m`/`--model_name`

  The model name.
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation.
- `-q`/`--quiet`

  Suppress informational messages.
