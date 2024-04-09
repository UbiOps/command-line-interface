## ubiops deployments

**Command:** `ubiops deployments`

**Alias:** `ubiops dpl`


<br/>

### ubiops deployments list

**Command:** `ubiops deployments list`

**Description:**

List all your deployments in your project.

The `<labels>` option can be used to filter on specific labels.

**Arguments:** - 

**Options:**

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops deployments get

**Command:** `ubiops deployments get`

**Description:**

Get the deployment settings, like, input_type and output_type.

If you specify the `<output_path>` option, this location will be used to store the
deployment settings in a yaml file. You can either specify the `<output_path>` as file or
directory. If the specified `<output_path>` is a directory, the settings will be
stored in `deployment.yaml`.

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store deployment yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops deployments create

**Command:** `ubiops deployments create`

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

- [required] `-f`/`--yaml_file`<br/>Path to a yaml file that contains at least the following fields: [input_type, output_type]

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops deployments update

**Command:** `ubiops deployments update`

**Description:**

Update a deployment.

If you only want to update the name of the deployment or the default deployment version,
use the options `<new_name>` and `<default_version>`.
If you want to update the deployment input/output fields, description or labels, please use a yaml file to define
the new deployment.


For example:
```
deployment_description: Deployment created via command line.
deployment_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
input_fields:
  - name: param1
    data_type: int
  - name: param2
    data_type: string
output_fields:
  - name: param1
    data_type: int
  - name: param2
    data_type: string
```

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-n`/`--new_name`<br/>The new deployment name

- `-default`/`--default_version`<br/>The name of the version that should become the default

- `-f`/`--yaml_file`<br/>Path to a yaml file containing deployment details

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops deployments delete

**Command:** `ubiops deployments delete`

**Description:**

Delete a deployment.

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops deployments package

**Command:** `ubiops deployments package`

**Description:**

Package code to ZIP file which is ready to be deployed.

Please, specify the code `<directory>` that should be deployed. The files in this directory will be zipped.
Subdirectories and files that shouldn't be contained in the ZIP can be specified in an ignore file, which is by
default '.ubiops-ignore'. The structure of this file is assumed to be equal to the well-known .gitignore file.

Use the `<output_path>` option to specify the output location of the zip file. If not specified,
the current directory will be used. If the `<output_path>` is a directory, the zip will be saved in
`[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use the `<assume_yes>` option to overwrite
without confirmation if file specified in `<output_path>` already exists.

**Arguments:** - 

**Options:**

- `-d`/`--deployment_name`<br/>The deployment name used in the ZIP filename

- `-v`/`--version_name`<br/>The version name used in the ZIP filename

- [required] `-dir`/`--directory`<br/>Path to a directory that contains at least a 'deployment.py'

- `-o`/`--output_path`<br/>Path to file or directory to store deployment package zip

- `-i`/`--ignore_file`<br/>File name of ubiops-ignore file located in the root of the specified directory [default = .ubiops-ignore]

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops deployments upload

**Command:** `ubiops deployments upload`

**Description:**

Upload ZIP to a version of a deployment.

Please, specify the deployment package `<zip_path>` that should be uploaded.
Use the `<overwrite>` option to overwrite the deployment package on UbiOps if one already exists for this version.

**Arguments:**

- [required] `deployment_name`



**Options:**

- [required] `-v`/`--version_name`<br/>The version name

- [required] `-z`/`--zip_path`<br/>Path to deployment version zip file

- `--overwrite`<br/>Whether you want to overwrite if exists

- `-pb`/`--progress_bar`<br/>Whether the show a progress bar while uploading

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops deployments download

**Command:** `ubiops deployments download`

**Description:**

Get the version of a deployment.

The `<output_path>` option will be used as output location of the zip file. If not specified,
the current directory will be used. If the `<output_path>` is a directory, the zip will be
saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`.

**Arguments:**

- [required] `deployment_name`



**Options:**

- [required] `-v`/`--version_name`<br/>The version name

- `-o`/`--output_path`<br/>Path to file or directory to store deployment package zip

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops deployments deploy

**Command:** `ubiops deployments deploy`

**Description:**

Deploy a new version of a deployment.

Please, specify the code `<directory>` that should be deployed. The files in this directory
will be zipped and uploaded. Subdirectories and files that shouldn't be contained in the
ZIP can be specified in an ignore file, which is by default '.ubiops-ignore'. The structure of this
file is assumed to be equal to the well-known '.gitignore' file.

If you want to store a local copy of the uploaded zip file, please use the `<output_path>` option.
The `<output_path>` option will be used as output location of the zip file. If the `<output_path>` is a
directory, the zip will be saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`. Use
the `<assume_yes>` option to overwrite without confirmation if file specified in `<output_path>` already exists.


It is possible to define the parameters using a yaml file.
For example:
```
deployment_name: my-deployment-name
version_name: my-deployment-version
version_description: Version created via command line.
version_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
environment: python3-8
instance_type: 2048mb
minimum_instances: 0
maximum_instances: 1
maximum_idle_time: 300
request_retention_mode: none
request_retention_time: 604800
maximum_queue_size_express: 100
maximum_queue_size_batch: 100000
static_ip: false
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and options are given,
the options defined by `<yaml_file>` will be overwritten by the specified command options. The deployment name can
either be passed as command argument or specified inside the yaml file using `<deployment_name>`.

**Arguments:**

- `deployment_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- [required] `-dir`/`--directory`<br/>Path to a directory that contains at least a 'deployment.py'

- `-deployment_py`/`--deployment_file`<br/>Name of deployment file which contains class Deployment. Must be located in the root of the deployment package directory

- `-i`/`--ignore_file`<br/>File name of ubiops-ignore file located in the root of the specified directory [default = .ubiops-ignore]

- `-o`/`--output_path`<br/>Path to file or directory to store local copy of deployment package zip

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains version options

- `-e`/`--environment`<br/>Environment for the version

- `-inst`/`--instance_type`<br/>Reserved instance type for the version

- `-min`/`--minimum_instances`<br/>Minimum number of instances

- `-max`/`--maximum_instances`<br/>Maximum number of instances

- `-t`/`--maximum_idle_time`<br/>Maximum idle time before shutting down instance (seconds)

- `-rtm`/`--request_retention_mode`<br/>Mode of request retention for requests to the version

- `-rtt`/`--request_retention_time`<br/>Number of seconds to store requests to the version

- `-qse`/`--maximum_queue_size_express`<br/>Maximum number of queued express requests to the version

- `-qsb`/`--maximum_queue_size_batch`<br/>Maximum number of queued batch requests to the version

- `--static-ip`<br/>Whether the deployment version should get a static IP

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-desc`/`--version_description`<br/>The version description

- `--overwrite`<br/>Whether you want to overwrite if exists

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-pb`/`--progress_bar`<br/>Whether the show a progress bar while uploading

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>


***
<br/>

### ubiops deployments requests

**Command:** `ubiops deployments requests`


<br/>

#### ubiops deployments requests create

**Command:** `ubiops deployments requests create`

**Description:**

Create a deployment request and retrieve request IDs to collect the results later.
Use the option `timeout` to specify the timeout of the request. The minimum value is 10 seconds. The maximum value
is 3600 (1 hour) for direct (synchronous) requests and 345600 (96 hours) for batch (asynchronous) requests.
The default value is 300 (5 minutes) for direct requests and 14400 (4 hours) for batch requests.

Use the version option to make a request to a specific deployment version:
`ubiops deployments requests create <my-deployment> -v <my-version> --data <input>`

If not specified, a request is made to the default version:
`ubiops deployments requests create <my-deployment> --data <input>`

Use `--batch` to make an asynchronous batch request:
`ubiops deployments requests create <my-deployment> --batch --data <input>`

Multiple data inputs can be specified at ones and send as batch by using the '--data' options multiple times:
`ubiops deployments requests create <my-deployment> --batch --data <input-1> --data <input-2> --data <input-3>`

For structured input, specify data input as JSON formatted string. For example:
`ubiops deployments requests create <my-deployment> --data "{\"param1\": 1, \"param2\": \"two\"}"`

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- `--batch`<br/>Whether you want to perform the request as batch request (async)

- `--data`<br/>The input data of the request<br/>This option can be provided multiple times in a single command

- `-f`/`--json_file`<br/>Path to json file containing the input data of the request

- `-t`/`--timeout`<br/>Timeout in seconds

- `-fmt`/`--format`<br/>The output format


<br/>

#### ubiops deployments requests get

**Command:** `ubiops deployments requests get`

**Description:**

Get one or more stored deployment requests.
Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

Use the version option to get a request for a specific deployment version.
If not specified, the request is retrieved for the default version.

Multiple request ids can be specified at ones by using the '-id' options multiple times:
`ubiops deployments requests get <my-deployment> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- [required] `-id`/`--request_id`<br/>The ID of the request<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

#### ubiops deployments requests list

**Command:** `ubiops deployments requests list`

**Description:**

List stored deployment requests.
Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

Use the version option to list the requests for a specific deployment version.
If not specified, the requests are listed for the default version.

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- `--offset`<br/>The starting point: if offset equals 2, then the first 2 records will be omitted

- `--limit`<br/>Limit of the number of requests. The maximum value is 50.

- `--sort`<br/>Direction of sorting on creation date

- `--status`<br/>Status of the request

- `--success`<br/>[DEPRECATED] A boolean value that indicates whether the request was successful

- `--start_date`<br/>Start date of the interval for which the requests are retrieved, looking at the creation date of the request. Formatted like '2020-01-01T00:00:00.000000Z'.

- `--end_date`<br/>End date of the interval for which the requests are retrieved, looking at the creation date of the request. Formatted like '2020-01-01T00:00:00.000000Z'.

- `--search_id`<br/>A string to search inside request ids. It will filter all request ids that contain this string.

- `--pipeline`<br/>A boolean value that indicates whether the deployment request was part of a pipeline request

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops deployments request

**Command:** `ubiops deployments request`

**Description:**

[DEPRECATED] Create a deployment request and retrieve the result.

Use the version option to make a request to a specific deployment version:
`ubiops deployments request <my-deployment> -v <my-version> --data <input>`

If not specified, a request is made to the default version:
`ubiops deployments request <my-deployment> --data <input>`

For structured input, specify the data as JSON formatted string. For example:
`ubiops deployments request <my-deployment> --data "{\"param1\": 1, \"param2\": \"two\"}"`

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- [required] `-d`/`--data`<br/>The input data of the request

- `-t`/`--timeout`<br/>Timeout in seconds

- `-fmt`/`--format`<br/>The output format


<br/>


***
<br/>

### ubiops deployments batch_requests

**Command:** `ubiops deployments batch_requests`


<br/>

#### ubiops deployments batch_requests create

**Command:** `ubiops deployments batch_requests create`

**Description:**

[DEPRECATED] Create a deployment batch request and retrieve request IDs to collect the results later.
Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

Use the option `timeout` to specify the timeout of the request. The minimum value is 10 seconds. The maximum value
is 345600 (96 hours). The default value is 14400 (4 hours).

Use the version option to make a batch request to a specific deployment version:
`ubiops deployments batch_requests create <my-deployment> -v <my-version> --data <input>`

If not specified, a batch request is made to the default version:
`ubiops deployments batch_requests create <my-deployment> --data <input>`

Multiple data inputs can be specified at ones by using the '--data' options multiple times:
`ubiops deployments batch_requests create <my-deployment> --data <input-1> --data <input-2> --data <input-3>`

For structured input, specify each data input as JSON formatted string. For example:
`ubiops deployments batch_requests create <my-deployment> --data "{\"param1\": 1, \"param2\": \"two\"}"`

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- `--data`<br/>The input data of the request<br/>This option can be provided multiple times in a single command

- `-t`/`--timeout`<br/>Timeout in seconds

- `-fmt`/`--format`<br/>The output format


<br/>

#### ubiops deployments batch_requests get

**Command:** `ubiops deployments batch_requests get`

**Description:**

[DEPRECATED] Get the results of one or more deployment batch requests.
Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

Use the version option to get a batch request for a specific deployment version.
If not specified, the batch request is retrieved for the default version.

Multiple request ids can be specified at ones by using the '-id' options multiple times:
`ubiops deployments batch_requests get <my-deployment> -v <my-version> -id <id-1> -id <id-2> -id <id-3>`

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- [required] `-id`/`--request_id`<br/>The ID of the request<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

#### ubiops deployments batch_requests list

**Command:** `ubiops deployments batch_requests list`

**Description:**

[DEPRECATED] List deployment batch requests.
Deployment requests are only stored for deployment versions with `request_retention_mode` 'full' or 'metadata'.

Use the version option to list the batch requests for a specific deployment version.
If not specified, the batch requests are listed for the default version.

**Arguments:**

- [required] `deployment_name`



**Options:**

- `-v`/`--version_name`<br/>The version name

- `--offset`<br/>The starting point: if offset equals 2, then the first 2 records will be omitted

- `--limit`<br/>Limit of the number of requests. The maximum value is 50.

- `-fmt`/`--format`<br/>The output format


<br/>
