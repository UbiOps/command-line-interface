## ubiops environment_variables

**Command:** `ubiops environment_variables`

**Alias:** `ubiops env`


<br/>

### ubiops environment_variables list

**Command:** `ubiops environment_variables list`

**Description:**

List environment variables.


- When deployment_name and version_name are provided: the environment variables will be listed on deployment
version level.
- When a deployment name is provided, but not a version name: the environment variables will be listed on
deployment level.
- When no deployment_name nor a version name is provided: the environment variables will be listed on project level.

**Arguments:** - 

**Options:**

- `-d`/`--deployment_name`<br/>The deployment name

- `-v`/`--version_name`<br/>The version name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops environment_variables create

**Command:** `ubiops environment_variables create`

**Description:**

Create an environment variable.


- When deployment_name and version_name are provided: the environment variable will be created on deployment
version level.
- When a deployment name is provided, but not a version name: the environment variable will be created on
deployment level.
- When no deployment_name nor a version name is provided: the environment variable will be created on project level.


It is possible to create multiple environment variables at ones by passing a yaml file.
The structure of this file is assumed to look like:
```
environment_variables:
  - name: env_var_1
    value: value_1
  - name: env_var_2
    value: value_2
    secret: true
  - name: env_var_3
    value: value_3
    secret: true
```
The 'secret' parameter is optional, and is `false` by default.

**Arguments:**

- `env_var_name`



**Options:**

- `--value`<br/>Environment variable value

- `--secret`<br/>Store value as secret

- `-d`/`--deployment_name`<br/>The deployment name

- `-v`/`--version_name`<br/>The version name

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains environment variables

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops environment_variables get

**Command:** `ubiops environment_variables get`

**Description:**

Get an environment variable.


- When deployment_name and version_name are provided: the environment variable will be collected on deployment
version level.
- When a deployment name is provided, but not a version name: the environment variable will be collected on
deployment level.
- When no deployment_name nor a version name is provided: the environment variable will be collected on
project level.

**Arguments:**

- [required] `env_var_id`



**Options:**

- `-d`/`--deployment_name`<br/>The deployment name

- `-v`/`--version_name`<br/>The version name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops environment_variables copy

**Command:** `ubiops environment_variables copy`

**Description:**

Copy environment variables from one deployment (version) to another deployment (version).

**Arguments:** - 

**Options:**

- [required] `-fd`/`--from_deployment`<br/>The deployment name to copy the environment variables from

- `-fv`/`--from_version`<br/>The version name to copy the environment variables from. If None, the environment variables on deployment level are copied.

- [required] `-td`/`--to_deployment`<br/>The deployment name to copy the environment variables to

- `-tv`/`--to_version`<br/>The version name to copy the environment variables to. If None, the environment variables are copied to deployment level.

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation


<br/>

### ubiops environment_variables update

**Command:** `ubiops environment_variables update`

**Description:**

Update an environment variable.


- When deployment_name and version_name are provided: the environment variable will be updated on deployment
version level.
- When a deployment name is provided, but not a version name: the environment variable will be updated on
deployment level.
- When no deployment_name nor a version name is provided: the environment variable will be updated on
project level.

**Arguments:**

- [required] `env_var_id`



**Options:**

- `-n`/`--new_name`<br/>The new environment variable name

- `--value`<br/>Environment variable value

- `--secret`<br/>Store value as secret

- `-d`/`--deployment_name`<br/>The deployment name

- `-v`/`--version_name`<br/>The version name

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environment_variables delete

**Command:** `ubiops environment_variables delete`

**Description:**

Delete an environment variable.


- When deployment_name and version_name are provided: the environment variable will be deleted on deployment
version level.
- When a deployment name is provided, but not a version name: the environment variable will be deleted on
deployment level.
- When no deployment_name nor a version name is provided: the environment variable will be deleted on
project level.

**Arguments:**

- [required] `env_var_id`



**Options:**

- `-d`/`--deployment_name`<br/>The deployment name

- `-v`/`--version_name`<br/>The version name

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
