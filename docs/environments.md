## ubiops environments

**Command:** `ubiops environments`

**Alias:** `ubiops envs`


<br/>

### ubiops environments list

**Command:** `ubiops environments list`

**Description:**

List all your environments in your project.

The `<labels>` option can be used to filter on specific labels.

**Arguments:** - 

**Options:**

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-env-type`/`--environment_type`<br/>Environment type. It can be either base or custom.

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops environments get

**Command:** `ubiops environments get`

**Description:**

Get the environment details.

If you specify the `<output_path>` option, this location will be used to store the
environment settings in a yaml file. You can either specify the `<output_path>` as
file or directory. If the specified `<output_path>` is a directory, the settings
will be stored in `environment.yaml`.


Example of yaml content:
```
environment_name: custom-environment
environment_display_name: Custom environment for Python 3.11
environment_description: Environment created via command line.
environment_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
base_environment: python3-11
```

**Arguments:**

- [required] `environment_name`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store environment yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops environments create

**Command:** `ubiops environments create`

**Description:**

Create an environment.


It is possible to define the parameters using a yaml file.
For example:
```
environment_name: my-environment-name
environment_display_name: Custom environment for Python 3.11
environment_description: Environment created via command line.
environment_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
environment_supports_request_format: true
base_environment: python3-11
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
The environment name can either be passed as command argument or specified inside the yaml file using
`<environment_name>`.

**Arguments:**

- `environment_name`



**Options:**

- `-base-env`/`--base_environment`<br/>Base environment to use for the environment

- `-requests`/`--supports_request_format`<br/>A boolean indicating whether the environment supports the request format

- `--display_name`/`--environment_display_name`<br/>Human readable name for the environment

- `-desc`/`--environment_description`<br/>The environment description

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-f`/`--yaml_file`<br/>Path to a yaml file

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops environments update

**Command:** `ubiops environments update`

**Description:**

Update an environment.


It is possible to define the parameters using a yaml file or passing the options as command options.
For example:
```

environment_name: my-environment-name
environment_display_name: Custom environment for Python 3.9
environment_description: Environment created via command line.
environment_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
```

If both a `<yaml_file>` is set and options are given, the options defined by `<yaml_file>` will be overwritten by
the specified command options.

**Arguments:**

- [required] `environment_name`



**Options:**

- `-n`/`--new_name`<br/>The new environment name

- `--display_name`/`--environment_display_name`<br/>Human readable name for the environment

- `-desc`/`--environment_description`<br/>The environment description

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-f`/`--yaml_file`<br/>Path to a yaml file

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environments delete

**Command:** `ubiops environments delete`

**Description:**

Delete an environment.

**Arguments:**

- [required] `environment_name`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environments wait

**Command:** `ubiops environments wait`

**Description:**

Wait for an environment to be ready.

**Arguments:**

- [required] `environment_name`



**Options:**

- `-t`/`--timeout`<br/>Timeout in seconds for the operation

- `--stream_logs`<br/>Stream logs while waiting

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environments package

**Command:** `ubiops environments package`

**Description:**

Package code to archive file which is ready to be deployed.

Please, specify the code `<directory>` that should be deployed. The files in this directory will be zipped.
Subdirectories and files that shouldn't be contained in the archive can be specified in an ignore file, which is by
default '.ubiops-ignore'. The structure of this file is assumed to be equal to the well-known .gitignore file.

Use the `<output_path>` option to specify the output location of the archive file. If not specified,
the current directory will be used. If the `<output_path>` is a directory, the archive will be saved as
`[environment_name]_[datetime.now()].zip`. Use the `<assume_yes>` option to overwrite without confirmation if file
specified in `<output_path>` already exists.

**Arguments:** - 

**Options:**

- `-e`/`--environment_name`<br/>The environment name used in the archive filename

- [required] `-dir`/`--directory`<br/>Path to a directory that contains the environment files

- `-o`/`--output_path`<br/>Path to file or directory to store the environment package archive file

- `-i`/`--ignore_file`<br/>File name of ubiops-ignore file located in the root of the specified directory [default = .ubiops-ignore]

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environments deploy

**Command:** `ubiops environments deploy`

**Description:**

Deploy an environment.

Please, either specify an `<archive_file>` or a code `<directory>` that should be deployed. If a directory is
used, the files in the directory will be zipped and uploaded. Subdirectories and files that shouldn't be contained
in the archive can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this file
is assumed to be equal to the well-known '.gitignore' file.

If you want to store a local copy of the uploaded archive file, please use the `<output_path>` option.
The `<output_path>` option will be used as output location of the file. If the `<output_path>` is a directory, the
archive will be saved as `[environment_name]_[datetime.now()].zip`. Use the `<assume_yes>` option to overwrite
without confirmation if file specified in `<output_path>` already exists.

It's not possible to update the base environment of an existing environment.


It is possible to define the parameters using a yaml file.
For example:
```
environment_name: my-environment-name
environment_display_name: Custom environment for Python 3.11
environment_description: Environment created via command line.
environment_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
environment_supports_request_format: true
base_environment: python3-11
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and options are given,
the options defined by `<yaml_file>` will be overwritten by the specified command options. The environment name can
either be passed as command argument or specified inside the yaml file using `<environment_name>`.

**Arguments:**

- `environment_name`



**Options:**

- `-dir`/`--directory`<br/>Path to a directory that contains the environment files

- `-a`/`--archive_path`<br/>Path to environment package archive file

- `-i`/`--ignore_file`<br/>File name of ubiops-ignore file located in the root of the specified directory [default = .ubiops-ignore]

- `-o`/`--output_path`<br/>Path to file or directory to store the environment package archive file

- `-f`/`--yaml_file`<br/>Path to a yaml file

- `-base-env`/`--base_environment`<br/>Base environment to use for the environment

- `-requests`/`--supports_request_format`<br/>A boolean indicating whether the environment supports the request format

- `--display_name`/`--environment_display_name`<br/>Human readable name for the environment

- `-desc`/`--environment_description`<br/>The environment description

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `--overwrite`<br/>Whether you want to overwrite if exists

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-pb`/`--progress_bar`<br/>Whether to show a progress bar while uploading

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
