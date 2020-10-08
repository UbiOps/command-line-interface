
## ubiops models
### ubiops models list

**Description:**

List all your models in your project.

**Arguments:** - 

**Options:**
- `-fmt`/`--format`

  The output format.

### ubiops models get

**Description:**

Get the model settings, like, input_type and output_type.

If you specify the <output_path> option, this location will be used to store the
model settings in a yaml file. You can either specify the <output_path> as file or
directory. If the specified <output_path> is a directory, the settings will be
stored in `model.yaml`.

**Arguments:**
- [required] `model_name`

**Options:**
- `-o`/`--output_path`

  Path to file or directory to store model yaml file.
- `-q`/`--quiet`

  Suppress informational messages.
- `-fmt`/`--format`

  The output format.

### ubiops models create

**Description:**

Create a new model.


Define the model parameters using a yaml file.
For example:
```
model_name: my-model-name
model_description: Model created via command line.
input_type: structured
input_fields:
  - name: param1
    data_type: int
  - name: param2
    data_type: string
output_type: plain
```

The model name can either be passed as argument or specified inside the yaml file. If it is both passed as argument
and specified inside the yaml file, the value passed as argument is used.

Possible input/output types: [structured, plain]. Possible data_types: [blob, int,
string, double, bool, array_string, array_int, array_double].

**Arguments:**
- `model_name`

**Options:**
- [required] `-f`/`--yaml_file`

  Path to a yaml file that contains at least the following fields: [input_type, output_type].
- `-fmt`/`--format`

  The output format.

### ubiops models update

**Description:**

Delete a model.

**Arguments:**
- [required] `model_name`

**Options:**
- `-n`/`--new_name`

  The new model name.
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops models delete

**Description:**

Delete a model.

**Arguments:**
- [required] `model_name`

**Options:**
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation.
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops models package

**Description:**

Package code to ZIP file which is ready to be deployed.

Please, specify the code <directory> that should be deployed. The files in this directory
will be zipped and uploaded. Subdirectories and files that shouldn't be contained in
the ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of
this file is assumed to be equal to the wellknown .gitignore file.

Use the <output_path> option to specify the output location of the zip file. If not specified,
the current directory will be used. If the <output_path> is a directory, the zip will be saved in
`[model_name]_[model_version]_[datetime.now()].zip`. Use the <assume_yes> option to overwrite
without confirmation if file specified in <output_path> already exists.

**Arguments:** - 

**Options:**
- `-m`/`--model_name`

  The model name used in the ZIP filename.
- `-v`/`--version_name`

  The model version name used in the ZIP filename.
- [required] `-d`/`--directory`

  Path to a directory that contains at least a 'model.py'.
- `-o`/`--output_path`

  Path to file or directory to store model package zip.
- `-i`/`--ignore_file`

  File name of ubiops-ignore file located in the root of the specified directory. [default = .ubiops-ignore]
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation.
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops models upload

**Description:**

Upload ZIP to a version of a model.

Please, specify the model package <zip_path> that should be uploaded.
Use the <overwrite> option to overwrite the model package on UbiOps if one already exists for this version.

**Arguments:**
- [required] `model_name`

**Options:**
- [required] `-v`/`--version_name`

  The model version name.
- [required] `-z`/`--zip_path`

  Path to model version zip file.
- `--overwrite`

  Whether you want to overwrite if exists.
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops models download

**Description:**

Get the version of a model.

The <output_path> option will be used as output location of the zip file. If not specified,
the current directory will be used. If the <output_path> is a directory, the zip will be
saved in `[model_name]_[model_version]_[datetime.now()].zip`.

**Arguments:**
- [required] `model_name`

**Options:**
- [required] `-v`/`--version_name`

  The model version name.
- `-o`/`--output_path`

  Path to file or directory to store model package zip.
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops models deploy

**Description:**

Deploy a new version of a model.

Please, specify the code <directory> that should be deployed. The files in this directory
will be zipped and uploaded. Subdirectories and files that shouldn't be contained in the
ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this
file is assumed to be equal to the wellknown .gitignore file.

If you want to store a local copy of the uploaded zip file, please use the <output_path> option.
The <output_path> option will be used as output location of the zip file. If the <output_path> is a
directory, the zip will be saved in `[model_name]_[model_version]_[datetime.now()].zip`. Use
the <assume_yes> option to overwrite without confirmation if file specified in <output_path> already exists.


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
The model name can either be passed as command argument or specified inside the yaml file using <model_name>.

**Arguments:**
- `model_name`

**Options:**
- `-v`/`--version_name`

  The model version name.
- [required] `-d`/`--directory`

  Path to a directory that contains at least a 'model.py'.
- `-model_py`/`--model_file`

  Name of model file which contains class Model. Must be located in the root of the model package directory.
- `-i`/`--ignore_file`

  File name of ubiops-ignore file located in the root of the specified directory. [default = .ubiops-ignore]
- `-o`/`--output_path`

  Path to file or directory to store local copy of model package zip.
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
- `--overwrite`

  Whether you want to overwrite if exists.
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation.
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops models request

**Description:**

Create a model request and retrieve the result.

For structured input, specify the data as JSON formatted string. For example:
`ubiops models request <my-model> -v <my-version> -d "{"param1": 1, "param2": "two"}"`

**Arguments:**
- [required] `model_name`

**Options:**
- [required] `-v`/`--version_name`

  The model version name.
- [required] `-d`/`--data`

  The input data of the request.
- `--timeout`

  Timeout in seconds.
- `-fmt`/`--format`

  The output format.

### ubiops models batch_requests
#### ubiops models batch_requests create

**Description:**

Create a model batch request and retrieve request IDs to collect the results later.

Multiple data inputs can be specified at ones by using the '-d' options multiple times:
`ubiops models batch_requests create <my-model> -v <my-version> -d <input-1> -d <input-2> -d <input-3>`

For structured input, specify each data input as JSON formatted string. For example:
`ubiops models batch_requests create <my-model> -v <my-version> -d "{"param1": 1, "param2": "two"}"`

**Arguments:**
- [required] `model_name`

**Options:**
- [required] `-v`/`--version_name`

  The model version name.
- [required] `-d`/`--data`

  The input data of the request.

  This option can be provided multiple times in a single command.
- `-fmt`/`--format`

  The output format.

#### ubiops models batch_requests get

**Description:**

Get the results of one or more model batch requests.

Multiple request ids can be specified at ones by using the '-id' options multiple times:
`ubiops models batch_requests get <my-model> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`

**Arguments:**
- [required] `model_name`

**Options:**
- [required] `-v`/`--version_name`

  The model version name.
- [required] `-id`/`--request_id`

  The ID of the request.

  This option can be provided multiple times in a single command.
- `-fmt`/`--format`

  The output format.

#### ubiops models batch_requests list

**Description:**

List model batch requests.

**Arguments:**
- [required] `model_name`

**Options:**
- [required] `-v`/`--version_name`

  The model version name.
- `--offset`
- `--limit`

  Limit of the number of requests. The maximum value is 50.
- `-fmt`/`--format`

  The output format.
