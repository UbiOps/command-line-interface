## ubiops environment_tags

**Command:** `ubiops environment_tags`

**Alias:** `ubiops tags`


<br/>

### ubiops environment_tags list

**Command:** `ubiops environment_tags list`

**Description:**

List the tags of an environment.

**Arguments:** - 

**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `table`, `json`


<br/>

### ubiops environment_tags get

**Command:** `ubiops environment_tags get`

**Description:**

Get a tag of an environment.

**Arguments:**

- [required] `tag_name`



**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `row`, `yaml`, `json`


<br/>

### ubiops environment_tags create

**Command:** `ubiops environment_tags create`

**Description:**

Create a tag.


It is possible to define the parameters using a yaml file.
For example:
```
tag_name: my-tag-name
tag_supports_request_format: true
```

Those parameters can also be provided as command options. If both a `<yaml_file>` is set and options are given, the
options defined by `<yaml_file>` will be overwritten by the specified command options.

**Arguments:**

- `tag_name`



**Options:**

- `-e`/`--environment_name`<br/>The environment name

- `-requests`/`--supports_request_format`<br/>A boolean indicating whether the environment tag supports the request format

- `-f`/`--yaml_file`<br/>Path to a yaml file

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `row`, `yaml`, `json`


<br/>

### ubiops environment_tags update

**Command:** `ubiops environment_tags update`

**Description:**

Update a tag.

**Arguments:**

- [required] `tag_name`



**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-requests`/`--supports_request_format`<br/>A boolean indicating whether the environment tag supports the request format

- `--status`<br/>Update tag status to cancelled to cancel building a tag

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environment_tags delete

**Command:** `ubiops environment_tags delete`

**Description:**

Delete a tag.

**Arguments:**

- [required] `tag_name`



**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environment_tags build

**Command:** `ubiops environment_tags build`

**Description:**

Build a tag for an environment by uploading an archive file (Docker archive or environment package). Specify which
base environment and tag should be used for the build.

Please, specify the environment file `<archive_path>` that should be uploaded.

**Arguments:**

- [required] `tag_name`



**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-base_env`/`--base_environment_name`<br/>Base environment to use to build the tag

- `-base_tag`/`--base_environment_tag`<br/>Tag of the base environment to use to build the tag

- [required] `-a`/`-z`/`--archive_path`/`--zip_path`<br/>Path to environment archive file

- `-pb`/`--progress_bar`<br/>Whether to show a progress bar while uploading

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops environment_tags download

**Command:** `ubiops environment_tags download`

**Description:**

Download the environment package of an environment tag. Only relevant for tags that are build via UbiOps.

The `<output_path>` option will be used as output location of the archive file. If not specified,
the current directory will be used.

**Arguments:**

- [required] `tag_name`



**Options:**

- [required] `-e`/`--environment_name`<br/>The environment name

- `-o`/`--output_path`<br/>Path to file or directory to store the environment archive file

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
