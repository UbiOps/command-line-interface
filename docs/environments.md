## ubiops environments

**Command:** `ubiops environments`

**Alias:** `ubiops envs`


<br/>

### ubiops environments list

**Command:** `ubiops environments list`

**Description:**

List all your environments in your project.

The `<labels>` option can be used to filter on specific labels. The `<system>` option can be used to filter
(with system=true) on system environments, or (with system=false) on custom environments.

**Arguments:** - 

**Options:**

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `--system`<br/>Filter on system or non-system environments

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `table`, `json`


<br/>

### ubiops environments get

**Command:** `ubiops environments get`

**Description:**

Get the environment details.

If you specify the `<output_path>` option, this location will be used to store the
environment details in a yaml file. You can either specify the `<output_path>` as
file or directory. If the specified `<output_path>` is a directory, the settings
will be stored in `environment.yaml`.


Example of yaml content:
```
environment_name: custom-environment
environment_description: Environment created via command line.
environment_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
```

**Arguments:**

- [required] `environment_name`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store environment yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `row`, `yaml`, `json`


<br/>

### ubiops environments create

**Command:** `ubiops environments create`

**Description:**

Create an environment.


It is possible to define the parameters using a yaml file.
For example:
```
environment_name: my-environment-name
environment_description: Environment created via command line.
environment_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
The environment name can either be passed as command argument or specified inside the yaml file using
`<environment_name>`.

**Arguments:**

- `environment_name`



**Options:**

- `-desc`/`--environment_description`<br/>The environment description

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-f`/`--yaml_file`<br/>Path to a yaml file

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `row`, `yaml`, `json`


<br/>

### ubiops environments update

**Command:** `ubiops environments update`

**Description:**

Update an environment.


It is possible to define the parameters using a yaml file or passing the options as command options.
For example:
```
environment_name: my-environment-name
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

Wait for an environment tag to be ready.

**Arguments:**

- [required] `environment_name`



**Options:**

- `-tag`/`--tag_name`<br/>The environment tag

- `-t`/`--timeout`<br/>Timeout in seconds for the operation

- `--stream_logs`<br/>Stream logs while waiting

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environments package

**Command:** `ubiops environments package`

**Description:**

Package code to a ZIP archive which is ready to be deployed.

Please, specify the code `<directory>` that should be deployed. The files in this directory will be zipped.
Subdirectories and files that shouldn't be contained in the archive can be specified in an ignore file, which is by
default '.ubiops-ignore'. The structure of this file is assumed to be equal to the well-known .gitignore file.

Use the `<output_path>` option to specify the output location of the archive file. If not specified,
the current directory will be used. If the `<output_path>` is a directory, the archive will be saved as
`[environment_name]_[tag_name]_[datetime.now()].zip`. Use the `<assume_yes>` option to overwrite without
confirmation if file specified in `<output_path>` already exists.

Use `<paths_only>` option to retrieve a list of file paths that would be contained in the ZIP instead of actually
zipping. This is especially useful in combination with `git diff`. That way you can easily check for code changes to
any of the files that would be part of the environment package, respecting the given ignore file.

**Arguments:** - 

**Options:**

- `-e`/`--environment_name`<br/>The environment name used in the archive filename

- `-t`/`--tag_name`<br/>The tag name used in the archive filename

- [required] `-dir`/`--directory`<br/>Path to a directory that contains the environment files

- `-o`/`--output_path`<br/>Path to file or directory to store the environment archive file

- `-i`/`--ignore_file`<br/>File name of ubiops-ignore file located in the root of the specified directory [default = .ubiops-ignore]

- `--paths_only`<br/>Whether to only return the file paths that would be part of the ZIP, instead of actually zipping

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environments deploy

**Command:** `ubiops environments deploy`

**Description:**

Deploy a new tag for an environment.

Please, either specify an `<archive_file>` or a code `<directory>` that should be deployed. If a directory is
used, the files in the directory will be zipped and uploaded. Subdirectories and files that shouldn't be contained
in the archive can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this file
is assumed to be equal to the well-known '.gitignore' file.

If you want to store a local copy of the uploaded archive file, please use the `<output_path>` option.
The `<output_path>` option will be used as output location of the file. If the `<output_path>` is a directory, the
archive will be saved as `[environment_name]_[tag_name]_[datetime.now()].zip`. Use the `<assume_yes>` option to
overwrite without confirmation if file specified in `<output_path>` already exists.

It's not possible to update an existing tag with status 'available'.


It is possible to define the parameters using a yaml file.
For example:
```
environment_name: my-environment-name
tag_name: my-tag-name
tag_supports_request_format: true
base_environment_name: ubiops-ubuntu24-04-python3-13
base_environment_tag: v1
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and options are given,
the options defined by `<yaml_file>` will be overwritten by the specified command options. The tag name can
either be passed as command option or specified inside the yaml file using `<tag_name>`.

**Arguments:**

- `environment_name`



**Options:**

- `-tag`/`--tag_name`<br/>The environment tag

- `-dir`/`--directory`<br/>Path to a directory that contains the environment files

- `-a`/`--archive_path`<br/>Path to environment archive file

- `-i`/`--ignore_file`<br/>File name of ubiops-ignore file located in the root of the specified directory [default = .ubiops-ignore]

- `-o`/`--output_path`<br/>Path to file or directory to store the environment archive file

- `-requests`/`--supports_request_format`<br/>A boolean indicating whether the environment tag supports the request format

- `-base_env`/`--base_environment_name`<br/>Base environment to use to build the tag

- `-base_tag`/`--base_environment_tag`<br/>Tag of the base environment to use to build the tag

- `-f`/`--yaml_file`<br/>Path to a yaml file

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-pb`/`--progress_bar`<br/>Whether to show a progress bar while uploading

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `row`, `yaml`, `json`


<br/>
