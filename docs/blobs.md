## ubiops blobs

**Command:** `ubiops blobs`


<br/>

### ubiops blobs list

**Command:** `ubiops blobs list`

**Description:**

List blobs in project.

**Arguments:** - 

**Options:**

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops blobs create

**Command:** `ubiops blobs create`

**Description:**

Upload a new blob.

**Arguments:** - 

**Options:**

- [required] `-f`/`--input_path`<br/>Path to file

- `-ttl`/`--time_to_live`<br/>The time to live of the blob in seconds (default = 259200 seconds, 3 days)

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops blobs get

**Command:** `ubiops blobs get`

**Description:**

Download an existing blob.

**Arguments:**

- [required] `blob_id`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store blob

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops blobs delete

**Command:** `ubiops blobs delete`

**Description:**

Delete a blob.

**Arguments:**

- [required] `blob_id`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
