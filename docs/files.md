## ubiops files

**Command:** `ubiops files`


<br/>
### ubiops files signedurl

**Command:** `ubiops files signedurl`


<br/>

#### ubiops files signedurl create

**Command:** `ubiops files signedurl create`

**Description:**

Generate a signed url to upload a file.

**Arguments:**

- [required] `file_name`



**Options:**

- `-b`/`--bucket_name`<br/>The bucket name

- `-fmt`/`--format`<br/>The output format


<br/>

#### ubiops files signedurl get

**Command:** `ubiops files signedurl get`

**Description:**

Generate a signed url to download a file.

**Arguments:**

- [required] `file_name`



**Options:**

- `-b`/`--bucket_name`<br/>The bucket name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops files list

**Command:** `ubiops files list`

**Description:**

List files in a bucket.

If formatted as table it will only show the file name, size and time_created.

If formatted as json the response will show the continuation_token and prefixes as well.

**Arguments:** - 

**Options:**

- `-b`/`--bucket_name`<br/>The bucket name

- `-p`/`--prefix`<br/>Prefix to filter files

- `-d`/`--delimiter`<br/>Delimiter used with prefix to emulate hierarchy to filter files. If not provided shows all files including prefix. If provided only shows current level of hierarchy

- `--limit`<br/>The maximum number of files returned, default is 100

- `--continuation-token`<br/>A token that indicates the start point of the returned the files

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops files get

**Command:** `ubiops files get`

**Description:**

Get the details of a file in the bucket.

**Arguments:**

- [required] `file_name`



**Options:**

- `-b`/`--bucket_name`<br/>The bucket name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops files delete

**Command:** `ubiops files delete`

**Description:**

Delete a file from a bucket.

**Arguments:**

- [required] `file_name`



**Options:**

- `-b`/`--bucket_name`<br/>The bucket name

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops files upload

**Command:** `ubiops files upload`

**Description:**

Upload a file to a bucket.

**Arguments:**

- `file_name`



**Options:**

- [required] `-f`/`--source_file`<br/>Path of file to upload

- `-b`/`--bucket_name`<br/>The bucket name

- `-pb`/`--progress_bar`<br/>Whether the show a progress bar while uploading

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops files download

**Command:** `ubiops files download`

**Description:**

Download a file from a bucket. Provide either file_name or file_uri (e.g. 'ubiops-file://default/my-file.jpg').

**Arguments:**

- `file_name`



**Options:**

- `-b`/`--bucket_name`<br/>The bucket name

- `-u`/`--uri`<br/>UbiOps URI of the file to download, e.g. 'ubiops-file://default/my-file.jpg'

- `-o`/`--output_path`<br/>Path to file or directory to store downloaded file

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
