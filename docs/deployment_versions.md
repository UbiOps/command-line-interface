## ubiops deployment_versions

**Command:** `ubiops deployment_versions`

**Alias:** `ubiops versions`


<br/>

### ubiops deployment_versions list

**Command:** `ubiops deployment_versions list`

**Description:**

List the versions of a deployment.

The `<labels>` option can be used to filter on specific labels.

**Arguments:** - 

**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops deployment_versions get

**Command:** `ubiops deployment_versions get`

**Description:**

Get the version of a deployment.

If you specify the `<output_path>` option, this location will be used to store the
deployment version settings in a yaml file. You can either specify the `<output_path>`
as file or directory. If the specified `<output_path>` is a directory, the settings
will be stored in `version.yaml`.


Example of yaml content:
```
deployment_name: my-deployment
version_name: my-version
version_description: Version created via command line.
version_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
language: python3.7
memory_allocation: 2048
minimum_instances: 0
maximum_instances: 5
maximum_idle_time: 300
```

**Arguments:**

- [required] `version_name`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- `-o`/`--output_path`<br/>Path to file or directory to store version yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops deployment_versions create

**Command:** `ubiops deployment_versions create`

**Description:**

Create a version of a deployment.


It is possible to define the parameters using a yaml file.
For example:
```
deployment_name: my-deployment-name
version_name: my-deployment-version
version_description: Version created via command line.
version_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
language: python3.6
memory_allocation: 256
minimum_instances: 0
maximum_instances: 1
maximum_idle_time: 300
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
The version name can either be passed as command argument or specified inside the yaml file using `<version_name>`.

**Arguments:**

- `version_name`



**Options:**

- `-d`/`--deployment_name`<br/>The deployment name

- `-l`/`--language`<br/>Programming language of code

- `-mem`/`--memory_allocation`<br/>Memory allocation for deployment

- `-min`/`--minimum_instances`<br/>Minimum number of instances

- `-max`/`--maximum_instances`<br/>Maximum number of instances

- `-t`/`--maximum_idle_time`<br/>Maximum idle time before shutting down instance (seconds)

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-desc`/`--version_description`<br/>The version description

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains deployment options

- `-deployment_py`/`--deployment_file`<br/>Name of deployment file which contains class Deployment. Must be located in the root of the deployment package directory

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops deployment_versions update

**Command:** `ubiops deployment_versions update`

**Description:**

Update a version of a deployment.


It is possible to define the parameters using a yaml file.
For example:
```
version_description: Version created via command line.
version_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
memory_allocation: 256
minimum_instances: 0
maximum_instances: 1
maximum_idle_time: 300
```

You may want to change some deployment options, like, `<maximum_instances>` and
`<memory_allocation>`. You can do this by either providing the options in a yaml file
and passing the file path as `<yaml_file>`, or passing the options as command options.
If both a `<yaml_file>` is set and options are given, the options defined by `<yaml_file>`
will be overwritten by the specified command options.

It's not possible to update the programming language of an existing deployment version.

**Arguments:**

- [required] `version_name`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- `-n`/`--new_name`<br/>The new version name

- `-deployment_py`/`--deployment_file`<br/>Name of deployment file which contains class Deployment. Must be located in the root of the deployment package directory

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains deployment options

- `-mem`/`--memory_allocation`<br/>Memory allocation for deployment

- `-min`/`--minimum_instances`<br/>Minimum number of instances

- `-max`/`--maximum_instances`<br/>Maximum number of instances

- `-t`/`--maximum_idle_time`<br/>Maximum idle time before shutting down instance (seconds)

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-desc`/`--version_description`<br/>The version description

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops deployment_versions delete

**Command:** `ubiops deployment_versions delete`

**Description:**

Delete a version of a deployment.

**Arguments:**

- [required] `version_name`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
