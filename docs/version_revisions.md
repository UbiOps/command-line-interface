## ubiops version_revisions

**Command:** `ubiops version_revisions`

**Alias:** `ubiops revisions`


<br/>

### ubiops version_revisions list

**Command:** `ubiops version_revisions list`

**Description:**

List the revisions of a deployment version.

**Arguments:** - 

**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- [required] `-v`/`--version_name`<br/>The version name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops version_revisions get

**Command:** `ubiops version_revisions get`

**Description:**

Get a revision of a deployment version.

**Arguments:**

- [required] `revision_id`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- [required] `-v`/`--version_name`<br/>The version name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops version_revisions download

**Command:** `ubiops version_revisions download`

**Description:**

Download a revision of a deployment version.

The `<output_path>` option will be used as output location of the zip file. If not specified,
the current directory will be used. If the `<output_path>` is a directory, the zip will be
saved in `[deployment_name]_[deployment_version]_[datetime.now()].zip`.

**Arguments:**

- [required] `revision_id`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- [required] `-v`/`--version_name`<br/>The version name

- `-o`/`--output_path`<br/>Path to file or directory to store deployment package zip

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops version_revisions upload

**Command:** `ubiops version_revisions upload`

**Description:**

Create a revision of a deployment version by uploading a ZIP.

Please, specify the deployment package `<zip_path>` that should be uploaded.

**Arguments:** - 

**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- [required] `-v`/`--version_name`<br/>The version name

- [required] `-z`/`--zip_path`<br/>Path to deployment version zip file

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops version_revisions wait

**Command:** `ubiops version_revisions wait`

**Description:**

Wait for a deployment revision to be ready

**Arguments:**

- [required] `revision_id`



**Options:**

- [required] `-d`/`--deployment_name`<br/>The deployment name

- [required] `-v`/`--version_name`<br/>The version name

- `-t`/`--timeout`<br/>Timeout in seconds for the operation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
