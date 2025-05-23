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
environment: python3-8
instance_type_group_name: 2048 MB + 0.5 vCPU
scaling_strategy: default
minimum_instances: 0
maximum_instances: 5
instance_processes: 1
maximum_idle_time: 300
request_retention_mode: none
request_retention_time: 604800
maximum_queue_size_express: 100
maximum_queue_size_batch: 100000
has_request_method: true
has_requests_method: false
static_ip: false
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
environment: python3-8
instance_type_group_name: 2048 MB + 0.5 vCPU
scaling_strategy: default
minimum_instances: 0
maximum_instances: 1
instance_processes: 1
maximum_idle_time: 300
request_retention_mode: none
request_retention_time: 604800
maximum_queue_size_express: 100
maximum_queue_size_batch: 100000
static_ip: false
ports:
- public_port: 2222
  deployment_port: 2222
  protocol: tcp
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and
options are given, the options defined by `<yaml_file>` will be overwritten by the specified command options.
The version name can either be passed as command argument or specified inside the yaml file using `<version_name>`.

The `ports` to open up for the version can be provided as list of fields `public_port`, `deployment_port` and
`protocol` inside the yaml file, or one port can be given via command options `--public_port`, `--deployment_port`
and `--port_protocol`. Only one of the options (yaml or command options) can be used, not both.

**Arguments:**

- `version_name`



**Options:**

- `-d`/`--deployment_name`<br/>The deployment name

- `-e`/`--environment`<br/>Environment for the version

- `-inst`/`--instance_type`<br/>[DEPRECATED] Reserved instance type for the version

- `--instance_type_group_id`<br/>ID of the reserved instance type group for the version

- `-inst_group`/`--instance_type_group_name`<br/>Name of the reserved instance type group for the version

- `--scaling_strategy`<br/>Scaling strategy to use for scaling the instances for the version

- `-min`/`--minimum_instances`<br/>Minimum number of instances

- `-max`/`--maximum_instances`<br/>Maximum number of instances

- `--instance_processes`<br/>Number of instance processes (usually 1)

- `-t`/`--maximum_idle_time`<br/>Maximum idle time before shutting down instance (seconds)

- `-rtm`/`--request_retention_mode`<br/>Mode of request retention for requests to the version

- `-rtt`/`--request_retention_time`<br/>Number of seconds to store requests to the version

- `-qse`/`--maximum_queue_size_express`<br/>Maximum number of queued express requests to the version

- `-qsb`/`--maximum_queue_size_batch`<br/>Maximum number of queued batch requests to the version

- `--static-ip`/`--static_ip`<br/>Whether the deployment version should get a static IP

- `--public_port`<br/>Public port to open up to

- `--deployment_port`<br/>Deployment port to open up

- `--port_protocol`<br/>Protocol to use for port forwarding

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-desc`/`--version_description`<br/>The version description

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains version options

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
instance_type_group_name: 2048 MB + 0.5 vCPU
scaling_strategy: default
minimum_instances: 0
maximum_instances: 1
instance_processes: 1
maximum_idle_time: 300
request_retention_mode: none
request_retention_time: 604800
maximum_queue_size_express: 100
maximum_queue_size_batch: 100000
static_ip: false
ports:
- public_port: 2222
  deployment_port: 2222
  protocol: tcp
```

You may want to change some deployment options, like, `<maximum_instances>` and
`<instance_type_group_name>`. You can do this by either providing the options in a yaml file
and passing the file path as `<yaml_file>`, or passing the options as command options.
If both a `<yaml_file>` is set and options are given, the options defined by `<yaml_file>`
will be overwritten by the specified command options.

The `ports` to open up for the version can be provided as list of fields `public_port`, `deployment_port` and
`protocol` inside the yaml file, or one port can be given via command options `--public_port`, `--deployment_port`
and `--port_protocol`. Only one of the options (yaml or command options) can be used, not both. Use a yaml file with
empty `ports` list to remove already existing opened ports.

**Arguments:**

- [required] `version_name`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- `-n`/`--new_name`<br/>The new version name

- `-deployment_py`/`--deployment_file`<br/>Name of deployment file which contains class Deployment. Must be located in the root of the deployment package directory

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains version options

- `-e`/`--environment`<br/>Environment for the version

- `-inst`/`--instance_type`<br/>[DEPRECATED] Reserved instance type for the version

- `--instance_type_group_id`<br/>ID of the reserved instance type group for the version

- `-inst_group`/`--instance_type_group_name`<br/>Name of the reserved instance type group for the version

- `--scaling_strategy`<br/>Scaling strategy to use for scaling the instances for the version

- `-min`/`--minimum_instances`<br/>Minimum number of instances

- `-max`/`--maximum_instances`<br/>Maximum number of instances

- `--instance_processes`<br/>Number of instance processes (usually 1)

- `-t`/`--maximum_idle_time`<br/>Maximum idle time before shutting down instance (seconds)

- `-rtm`/`--request_retention_mode`<br/>Mode of request retention for requests to the version

- `-rtt`/`--request_retention_time`<br/>Number of seconds to store requests to the version

- `-qse`/`--maximum_queue_size_express`<br/>Maximum number of queued express requests to the version

- `-qsb`/`--maximum_queue_size_batch`<br/>Maximum number of queued batch requests to the version

- `--static-ip`/`--static_ip`<br/>Whether the deployment version should get a static IP

- `--public_port`<br/>Public port to open up to

- `--deployment_port`<br/>Deployment port to open up

- `--port_protocol`<br/>Protocol to use for port forwarding

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

### ubiops deployment_versions wait

**Command:** `ubiops deployment_versions wait`

**Description:**

Wait for a deployment version to be ready.

To wait for a specific revision of the version, pass `--revision_id`:
`ubiops versions wait v1 -d deployment-1 --revision_id=ced676ab-423b-4469-97e7-e5179515affb`

**Arguments:**

- [required] `version_name`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- `-rid`/`--revision_id`<br/>The deployment version revision ID

- `-t`/`--timeout`<br/>Timeout in seconds for the operation

- `--stream_logs`<br/>Stream logs while waiting

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
