## ubiops buckets

**Command:** `ubiops buckets`


<br/>

### ubiops buckets list

**Command:** `ubiops buckets list`

**Description:**

List buckets in project.

**Arguments:** - 

**Options:**

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops buckets get

**Command:** `ubiops buckets get`

**Description:**

Retrieve details of a bucket in a project.

If you specify the `<output_path>` option, this location will be used to store the
bucket settings in a yaml file. You can either specify the `<output_path>`
as file or directory. If the specified `<output_path>` is a directory, the settings
will be stored in `bucket.yaml`.

Bucket credentials are never returned by the UbiOps API.


Example of yaml content:
```
bucket_name: my-bucket
provider: amazon_s3
configuration:
  region: eu-central-1
  bucket: my-bucket
bucket_description: Bucket created via command line.
bucket_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
ttl: 3600
```

**Arguments:**

- [required] `bucket_name`



**Options:**

- `-o`/`--output_path`<br/>Path to file or directory to store bucket yaml file

- `-q`/`--quiet`<br/>Suppress informational messages

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops buckets create

**Command:** `ubiops buckets create`

**Description:**

Create a new bucket.


Define the bucket parameters using a yaml file.
For example:
```
bucket_name: my-bucket
bucket_description: Bucket created via command line.
bucket_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
provider: amazon_s3
credentials:
  access_key: my-access-key
  secret_key: my-secret-key
configuration:
  region: eu-central-1
  bucket: my-bucket
ttl: 3600
```

The bucket name can either be passed as argument or specified inside the yaml
file. If it is both passed as argument and specified inside the yaml file, the value
passed as argument is used.

Possible providers: [ubiops, google_cloud_storage, amazon_s3, azure_blob_storage].

**Arguments:**

- `bucket_name`



**Options:**

- `-p`/`--provider`<br/>Provider of the bucket

- `--credentials`<br/>A JSON string for credentials to connect to the bucket

- `--configuration`<br/>A JSON string for additional configuration details for the bucket

- `-desc`/`--bucket_description`<br/>The bucket description

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-ttl`/`--time_to_live`<br/>The time to live of the file in seconds (default = None)

- `-f`/`--yaml_file`<br/>Path to a yaml file

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops buckets update

**Command:** `ubiops buckets update`

**Description:**

Update a bucket.


It is possible to define the parameters using a yaml file. Note that the bucket_name and provider cannot be changed.
For example:
```
bucket_description: Bucket created via command line.
bucket_labels:
  my-key-1: my-label-1
  my-key-2: my-label-2
ttl: 3600
```

**Arguments:**

- `bucket_name`



**Options:**

- `-p`/`--provider`<br/>Provider of the bucket

- `-desc`/`--bucket_description`<br/>The bucket description

- `-lb`/`--labels`<br/>Labels defined as key/value pairs<br/>This option can be provided multiple times in a single command

- `-ttl`/`--time_to_live`<br/>The time to live of the file in seconds (default = None)

- `-f`/`--yaml_file`<br/>Path to a yaml file

- `-fmt`/`--format`<br/>The output format

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>

### ubiops buckets delete

**Command:** `ubiops buckets delete`

**Description:**

Delete a bucket.

**Arguments:**

- [required] `bucket_name`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>
