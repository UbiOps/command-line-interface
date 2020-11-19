
## ubiops blobs
### ubiops blobs list

**Description:**

List blobs in project.

**Arguments:** - 

**Options:**
- `-fmt`/`--format`

  The output format

### ubiops blobs create

**Description:**

Upload a new blob.

**Arguments:** - 

**Options:**
- [required] `-f`/`--input_path`

  Path to file
- `-ttl`/`--time_to_live`

  The time to live of the blob in seconds (default = 259200 seconds, 3 days)
- `-fmt`/`--format`

  The output format

### ubiops blobs get

**Description:**

Download an existing blob.

**Arguments:**
- [required] `blob_id`

**Options:**
- `-o`/`--output_path`

  Path to file or directory to store blob
- `-q`/`--quiet`

  Suppress informational messages

### ubiops blobs delete

**Description:**

Delete a blob.

**Arguments:**
- [required] `blob_id`

**Options:**
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation
- `-q`/`--quiet`

  Suppress informational messages
