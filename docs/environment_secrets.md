## ubiops environment_secrets

**Command:** `ubiops environment_secrets`

**Alias:** `ubiops secrets`


<br/>

### ubiops environment_secrets create

**Command:** `ubiops environment_secrets create`

**Description:**

Create an environment secret.

Use `--overwrite` flag to update the environment secret if it already exists.


It is possible to create multiple environment secrets at once by passing a yaml file.
The structure of this file is assumed to look like:
```
environment_secrets:
  - name: env_secret_1
    value: value_1
  - name: env_secret_2
    value: value_2
  - name: env_secret_3
    value: value_3
```

**Arguments:** - 

**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-n`/`--env_secret_name`<br/>The name of the environment secret

- `-v`/`--env_secret_value`<br/>The value of the environment secret

- `-f`/`--yaml_file`<br/>Path to a yaml file that contains environment secrets

- `--overwrite`<br/>Whether you want to overwrite if exists

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `row`, `yaml`, `json`


<br/>

### ubiops environment_secrets list

**Command:** `ubiops environment_secrets list`

**Description:**

List environment secrets.

**Arguments:** - 

**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `table`, `json`


<br/>

### ubiops environment_secrets get

**Command:** `ubiops environment_secrets get`

**Description:**

Get an environment secret.

**Arguments:** - 

**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-id`/`--env_secret_id`<br/>The ID of the environment secret

- `-n`/`--env_secret_name`<br/>The name of the environment secret

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `row`, `yaml`, `json`


<br/>

### ubiops environment_secrets update

**Command:** `ubiops environment_secrets update`

**Description:**

Update an environment secret.

**Arguments:** - 

**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- [required] `-id`/`--env_secret_id`<br/>The ID of the environment secret

- `-n`/`--env_secret_name`<br/>The name of the environment secret

- `-v`/`--env_secret_value`<br/>The value of the environment secret

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environment_secrets delete

**Command:** `ubiops environment_secrets delete`

**Description:**

Delete an environment secret.

**Arguments:** - 

**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- [required] `-id`/`--env_secret_id`<br/>The ID of the environment secret

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environment_secrets copy

**Command:** `ubiops environment_secrets copy`

**Description:**

Copy all environment secrets from one environment to another.

**Arguments:** - 

**Options:**

- [required] `-s`/`--source_name`<br/>The name of the environment to copy environment secrets from

- [required] `-t`/`--target_name`<br/>The name of the environment to copy environment secrets to

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `table`, `json`


<br/>
