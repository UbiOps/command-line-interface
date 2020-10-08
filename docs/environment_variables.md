
## ubiops environment_variables
### ubiops environment_variables list

**Description:**

List environment variables.


- When model_name and version_name are provided: the environment variables will be listed on model version level.
- When a model name is provided, but not a version name: the environment variables will be listed on model level.
- When no model_name nor a version name is provided: the environment variables will be listed on project level.

**Arguments:** - 

**Options:**
- `-m`/`--model_name`

  The model name.
- `-v`/`--version_name`

  The model version name.
- `-fmt`/`--format`

  The output format.

### ubiops environment_variables create

**Description:**

Create an environment variable.


- When model_name and version_name are provided: the environment variable will be created on model version level.
- When a model name is provided, but not a version name: the environment variable will be created on model level.
- When no model_name nor a version name is provided: the environment variable will be created on project level.

**Arguments:**
- [required] `env_var_name`

**Options:**
- `--value`

  Environment variable value.
- `--secret`

  Store value as secret.
- `-m`/`--model_name`

  The model name.
- `-v`/`--version_name`

  The model version name.
- `-fmt`/`--format`

  The output format.

### ubiops environment_variables get

**Description:**

Get an environment variable.


- When model_name and version_name are provided: the environment variable will be collected on model version level.
- When a model name is provided, but not a version name: the environment variable will be collected on model level.
- When no model_name nor a version name is provided: the environment variable will be collected on project level.

**Arguments:**
- [required] `env_var_id`

**Options:**
- `-m`/`--model_name`

  The model name.
- `-v`/`--version_name`

  The model version name.
- `-fmt`/`--format`

  The output format.

### ubiops environment_variables update

**Description:**

Update an environment variable.


- When model_name and version_name are provided: the environment variable will be updated on model version level.
- When a model name is provided, but not a version name: the environment variable will be updated on model level.
- When no model_name nor a version name is provided: the environment variable will be updated on project level.

**Arguments:**
- [required] `env_var_id`

**Options:**
- `-n`/`--new_name`

  The new environment variable name.
- `--value`

  Environment variable value.
- `--secret`

  Store value as secret.
- `-m`/`--model_name`

  The model name.
- `-v`/`--version_name`

  The model version name.
- `-q`/`--quiet`

  Suppress informational messages.

### ubiops environment_variables delete

**Description:**

Delete an environment variable.


- When model_name and version_name are provided: the environment variable will be deleted on model version level.
- When a model name is provided, but not a version name: the environment variable will be deleted on model level.
- When no model_name nor a version name is provided: the environment variable will be deleted on project level.

**Arguments:**
- [required] `env_var_id`

**Options:**
- `-m`/`--model_name`

  The model name.
- `-v`/`--version_name`

  The model version name.
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation.
- `-q`/`--quiet`

  Suppress informational messages.
