
## ubiops environment_variables

**Alias:**  ubiops env

### ubiops environment_variables list

**Description:**

List environment variables.


- When deployment_name and version_name are provided: the environment variables will be listed on deployment
version level.
- When a deployment name is provided, but not a version name: the environment variables will be listed on
deployment level.
- When no deployment_name nor a version name is provided: the environment variables will be listed on project level.

**Arguments:** - 

**Options:**
- `-d`/`--deployment_name`

  The deployment name
- `-v`/`--version_name`

  The version name
- `-fmt`/`--format`

  The output format

### ubiops environment_variables create

**Description:**

Create an environment variable.


- When deployment_name and version_name are provided: the environment variable will be created on deployment
version level.
- When a deployment name is provided, but not a version name: the environment variable will be created on
deployment level.
- When no deployment_name nor a version name is provided: the environment variable will be created on project level.

**Arguments:**
- [required] `env_var_name`

**Options:**
- `--value`

  Environment variable value
- `--secret`

  Store value as secret
- `-d`/`--deployment_name`

  The deployment name
- `-v`/`--version_name`

  The version name
- `-fmt`/`--format`

  The output format

### ubiops environment_variables get

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
- `-d`/`--deployment_name`

  The deployment name
- `-v`/`--version_name`

  The version name
- `-fmt`/`--format`

  The output format

### ubiops environment_variables copy

**Description:**

Copy environment variables from one deployment (version) to another deployment (version).

**Arguments:** - 

**Options:**
- [required] `-fd`/`--from_deployment`

  The deployment name to copy the environment variables from
- `-fv`/`--from_version`

  The version name to copy the environment variables from. If None, the environment variables on deployment level are copied.
- [required] `-td`/`--to_deployment`

  The deployment name to copy the environment variables to
- `-tv`/`--to_version`

  The version name to copy the environment variables to. If None, the environment variables are copied to deployment level.
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation

### ubiops environment_variables update

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
- `-n`/`--new_name`

  The new environment variable name
- `--value`

  Environment variable value
- `--secret`

  Store value as secret
- `-d`/`--deployment_name`

  The deployment name
- `-v`/`--version_name`

  The version name
- `-q`/`--quiet`

  Suppress informational messages

### ubiops environment_variables delete

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
- `-d`/`--deployment_name`

  The deployment name
- `-v`/`--version_name`

  The version name
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation
- `-q`/`--quiet`

  Suppress informational messages
