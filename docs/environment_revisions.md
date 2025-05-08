## ubiops environment_revisions

**Command:** `ubiops environment_revisions`

**Alias:** `ubiops env_revisions`


<br/>

### ubiops environment_revisions list

**Command:** `ubiops environment_revisions list`

**Description:**

List the revisions of an environment.

**Arguments:** - 

**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops environment_revisions get

**Command:** `ubiops environment_revisions get`

**Description:**

Get a revision of an environment.

**Arguments:**

- [required] `revision_id`



**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops environment_revisions download

**Command:** `ubiops environment_revisions download`

**Description:**

Download a revision of an environment.

The `<output_path>` option will be used as output location of the archive file. If not specified,
the current directory will be used. If the `<output_path>` is a directory, the archive will be
saved as `[environment_name]_[datetime.now()].zip`.

**Arguments:**

- [required] `revision_id`



**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-o`/`--output_path`<br/>Path to file or directory to store the environment package archive file

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environment_revisions upload

**Command:** `ubiops environment_revisions upload`

**Description:**

Create a revision of an environment by uploading an archive file.

Please, specify the environment package `<archive_path>` that should be uploaded.

**Arguments:** - 

**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- [required] `-a`/`-z`/`--archive_path`/`--zip_path`<br/>Path to environment package archive file

- `-pb`/`--progress_bar`<br/>Whether to show a progress bar while uploading

- `-fmt`/`--format`<br/>The output format


<br/>
