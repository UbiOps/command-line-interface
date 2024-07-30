## ubiops instances

**Command:** `ubiops instances`


<br/>

### ubiops instances list

**Command:** `ubiops instances list`

**Description:**

List the instances running for a deployment version.

**Arguments:** - 

**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- [required] `-v`/`--version_name`<br/>The version name

- `--limit`<br/>The maximum number of instances returned, default is 50

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops instances get

**Command:** `ubiops instances get`

**Description:**

Get the details of a single instance running for a deployment version.

**Arguments:**

- [required] `instance_id`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- [required] `-v`/`--version_name`<br/>The version name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops instances events

**Command:** `ubiops instances events`

**Description:**

List the events of an instance running for a deployment version.

**Arguments:**

- [required] `instance_id`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- [required] `-v`/`--version_name`<br/>The version name

- `--limit`<br/>The maximum number of instances returned, default is 50

- `-fmt`/`--format`<br/>The output format


<br/>
