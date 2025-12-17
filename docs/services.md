## ubiops services

**Command:** `ubiops services`


<br/>

### ubiops services list

**Command:** `ubiops services list`

**Description:**

List all your services in your project.

The `<labels>` option can be used to filter on specific labels. The `<deployment_version_ids>` option can be used to
filter on specific deployment versions.

**Arguments:** - 

**Options:**

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `--deployment_version_ids`<br/>Deployment version IDs to filter for. Separate multiple deployment version IDs with a comma (,).

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops services get

**Command:** `ubiops services get`

**Description:**

Get the service details.

If you specify the `<output_path>` option, this location will be used to store the
service settings in a yaml file. You can either specify the `<output_path>` as
file or directory. If the specified `<output_path>` is a directory, the settings
will be stored in `service.yaml`.


Example of yaml content:
```
service_name: my-service
service_description: Service created via command line.
service_labels:
    my-key-1: my-label-1
    my-key-2: my-label-2
```

**Arguments:**

- [required] `service_name`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store service yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops services create

**Command:** `ubiops services create`

**Description:**

Create a service.

Use `--overwrite` flag to update the service if it already exists.


Use a yaml file. For example:
```
service_name: my-service-name
service_description: Service created via command line.
service_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
service_deployment: my-deployment-name
service_version: my-deployment-version
port: 8080
authentication_required: true
authentication_method_token_enabled: true
request_logging_excluded_paths: "(health|status)$"
request_logging_excluded_extensions:
  - svg
  - tar
health_check:
  path: "/status"
rate_limit_token: 300
```

The service name can either be passed as command argument or specified inside the yaml file using
`<service_name>`.

**Arguments:**

- `service_name`



**Options:**

- [required] `-f`/`--yaml_file`<br/>Path to a yaml file that containing service details

- `--overwrite`<br/>Whether you want to overwrite if exists

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops services update

**Command:** `ubiops services update`

**Description:**

Update a service.

It is possible to define the updated parameter values using a yaml file. Or provide the `<new_name>` directly as
command option. When both a yaml file and command options are given, the command options are prioritized over the
yaml content.


For example:
```
service_name: new-name
service_description: Service created via command line.
service_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
service_deployment: my-deployment-name
service_version: my-deployment-version
port: 8080
authentication_required: true
authentication_method_token_enabled: true
request_logging_excluded_paths: "(health|status)$"
request_logging_excluded_extensions:
  - svg
  - tar
health_check:
  path: "/status"
rate_limit_token: 300
```

**Arguments:**

- [required] `service_name`



**Options:**

- `-n`/`--new_name`<br/>The new service name

- `-f`/`--yaml_file`<br/>Path to a yaml file containing service details

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops services delete

**Command:** `ubiops services delete`

**Description:**

Delete a service.

**Arguments:**

- [required] `service_name`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
