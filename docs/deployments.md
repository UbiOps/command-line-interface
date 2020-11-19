
## ubiops deployments

**Alias:**  ubiops dpl

### ubiops deployments list

**Description:**

List all your deployments in your project.

The <labels> option can be used to filter on specific labels.

**Arguments:** - 

**Options:**
- `-l`/`--labels`

  Labels defined as key/value pairs

  This option can be provided multiple times in a single command.
- `-fmt`/`--format`

  The output format

### ubiops deployments get

**Description:**

Get the deployment settings, like, input_type and output_type.

If you specify the <output_path> option, this location will be used to store the
deployment settings in a yaml file. You can either specify the <output_path> as file or
directory. If the specified <output_path> is a directory, the settings will be
stored in `deployment.yaml`.

**Arguments:**
- [required] `deployment_name`

**Options:**
- `-o`/`--output_path`

  Path to file or directory to store deployment yaml file
- `-q`/`--quiet`

  Suppress informational messages
- `-fmt`/`--format`

  The output format

### ubiops deployments create

**Description:**

Create a new deployment.


Define the deployment parameters using a yaml file.
For example:
```
deployment_name: my-deployment-name
deployment_description: Deployment created via command line.
deployment_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
input_type: structured
input_fields:
  - name: param1
    data_type: int
  - name: param2
    data_type: string
output_type: plain
```

The deployment name can either be passed as argument or specified inside the yaml
file. If it is both passed as argument and specified inside the yaml file, the value
passed as argument is used.

Possible input/output types: [structured, plain]. Possible data_types: [blob, int,
string, double, bool, array_string, array_int, array_double].

**Arguments:**
- `deployment_name`

**Options:**
- [required] `-f`/`--yaml_file`

  Path to a yaml file that contains at least the following fields: [input_type, output_type]
- `-fmt`/`--format`

  The output format

### ubiops deployments update

**Description:**

Update a deployment.

**Arguments:**
- [required] `deployment_name`

**Options:**
- `-n`/`--new_name`

  The new deployment name
- `-q`/`--quiet`

  Suppress informational messages

### ubiops deployments delete

**Description:**

Delete a deployment.

**Arguments:**
- [required] `deployment_name`

**Options:**
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation
- `-q`/`--quiet`

  Suppress informational messages

### ubiops deployments package

**Description:**

Package code to ZIP file which is ready to be deployed.

Please, specify the code <directory> that should be deployed. The files in this directory
will be zipped and uploaded. Subdirectories and files that shouldn't be contained in
the ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of
this file is assumed to be equal to the wellknown .gitignore file.

Use the <output_path> option to specify the output location of the zip file. If not specified,
the current directory will be used. If the <output_path> is a directory, the zip will be saved in
`[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use the <assume_yes> option to overwrite
without confirmation if file specified in <output_path> already exists.

**Arguments:** - 

**Options:**
- `-d`/`--deployment_name`

  The deployment name used in the ZIP filename
- `-v`/`--version_name`

  The version name used in the ZIP filename
- [required] `-dir`/`--directory`

  Path to a directory that contains at least a 'deployment.py'
- `-o`/`--output_path`

  Path to file or directory to store deployment package zip
- `-i`/`--ignore_file`

  File name of ubiops-ignore file located in the root of the specified directory [default = .ubiops-ignore]
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation
- `-q`/`--quiet`

  Suppress informational messages

### ubiops deployments upload

**Description:**

Upload ZIP to a version of a deployment.

Please, specify the deployment package <zip_path> that should be uploaded.
Use the <overwrite> option to overwrite the deployment package on UbiOps if one already exists for this version.

**Arguments:**
- [required] `deployment_name`

**Options:**
- [required] `-v`/`--version_name`

  The version name
- [required] `-z`/`--zip_path`

  Path to deployment version zip file
- `--overwrite`

  Whether you want to overwrite if exists
- `-q`/`--quiet`

  Suppress informational messages

### ubiops deployments download

**Description:**

Get the version of a deployment.

The <output_path> option will be used as output location of the zip file. If not specified,
the current directory will be used. If the <output_path> is a directory, the zip will be
saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`.

**Arguments:**
- [required] `deployment_name`

**Options:**
- [required] `-v`/`--version_name`

  The version name
- `-o`/`--output_path`

  Path to file or directory to store deployment package zip
- `-q`/`--quiet`

  Suppress informational messages

### ubiops deployments deploy

**Description:**

Deploy a new version of a deployment.

Please, specify the code <directory> that should be deployed. The files in this directory
will be zipped and uploaded. Subdirectories and files that shouldn't be contained in the
ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this
file is assumed to be equal to the wellknown .gitignore file.

If you want to store a local copy of the uploaded zip file, please use the <output_path> option.
The <output_path> option will be used as output location of the zip file. If the <output_path> is a
directory, the zip will be saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use
the <assume_yes> option to overwrite without confirmation if file specified in <output_path> already exists.


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

Those parameters can also be provided as command options. If both a <yaml_file> is set and options are given,
the options defined by <yaml_file> will be overwritten by the specified command options. The deployment name can
either be passed as command argument or specified inside the yaml file using <deployment_name>.

**Arguments:**
- `deployment_name`

**Options:**
- `-v`/`--version_name`

  The version name
- [required] `-dir`/`--directory`

  Path to a directory that contains at least a 'deployment.py'
- `-deployment_py`/`--deployment_file`

  Name of deployment file which contains class Deployment. Must be located in the root of the deployment package directory
- `-i`/`--ignore_file`

  File name of ubiops-ignore file located in the root of the specified directory [default = .ubiops-ignore]
- `-o`/`--output_path`

  Path to file or directory to store local copy of deployment package zip
- `-f`/`--yaml_file`

  Path to a yaml file that contains deployment options
- `-l`/`--language`

  Programming language of code
- `-mem`/`--memory_allocation`

  Memory allocation for deployment
- `-min`/`--minimum_instances`

  Minimum number of instances
- `-max`/`--maximum_instances`

  Maximum number of instances
- `-t`/`--maximum_idle_time`

  Maximum idle time before shutting down instance (seconds)
- `-l`/`--labels`

  Labels defined as key/value pairs

  This option can be provided multiple times in a single command.
- `-desc`/`--version_description`

  The version description
- `--overwrite`

  Whether you want to overwrite if exists
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation
- `-q`/`--quiet`

  Suppress informational messages

### ubiops deployments request

**Description:**

Create a deployment request and retrieve the result.

For structured input, specify the data as JSON formatted string. For example:
`ubiops deployments request <my-deployment> -v <my-version> --data "{"param1": 1, "param2": "two"}"`

**Arguments:**
- [required] `deployment_name`

**Options:**
- [required] `-v`/`--version_name`

  The version name
- [required] `-d`/`--data`

  The input data of the request
- `--timeout`

  Timeout in seconds
- `-fmt`/`--format`

  The output format

### ubiops deployments batch_requests
#### ubiops deployments batch_requests create

**Description:**

Create a deployment batch request and retrieve request IDs to collect the results later.

Multiple data inputs can be specified at ones by using the '--data' options multiple times:
`ubiops deployments batch_requests create <my-deployment> -v <my-version> --data <input-1> --data <input-2> --data <input-3>`

For structured input, specify each data input as JSON formatted string. For example:
`ubiops deployments batch_requests create <my-deployment> -v <my-version> --data "{"param1": 1, "param2": "two"}"`

**Arguments:**
- [required] `deployment_name`

**Options:**
- [required] `-v`/`--version_name`

  The version name
- [required] `--data`

  The input data of the request

  This option can be provided multiple times in a single command.
- `-fmt`/`--format`

  The output format

#### ubiops deployments batch_requests get

**Description:**

Get the results of one or more deployment batch requests.

Multiple request ids can be specified at ones by using the '-id' options multiple times:
`ubiops deployments batch_requests get <my-deployment> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`

**Arguments:**
- [required] `deployment_name`

**Options:**
- [required] `-v`/`--version_name`

  The version name
- [required] `-id`/`--request_id`

  The ID of the request

  This option can be provided multiple times in a single command.
- `-fmt`/`--format`

  The output format

#### ubiops deployments batch_requests list

**Description:**

List deployment batch requests.

**Arguments:**
- [required] `deployment_name`

**Options:**
- [required] `-v`/`--version_name`

  The version name
- `--offset`
- `--limit`

  Limit of the number of requests. The maximum value is 50.
- `-fmt`/`--format`

  The output format
