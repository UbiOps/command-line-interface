
## ubiops run_local

**Command:** `ubiops run_local`

**Description:**

Run a deployment locally and call its request function.

Use `-dir` to specify the deployment directory where the deployment.py is.

Use `--json_file` to use input data from a JSON file.

The input data must be a valid JSON string when using `--data`.

If the input data is plain, pass the `--plain` option. The input data will be sent as a string as it is provided.

Multiple data inputs can be specified at once and sent as batch by using the '--data' options multiple times:
`ubiops run_local -dir /path/to/deployment --data <input-1> --data <input-2> --data <input-3>`

For structured input, specify each data input as JSON formatted string. For example:
`ubiops run_local -dir /path/to/deployment --data "{\"param1\": 1, \"param2\": \"two\"}"`

**Arguments:** - 

**Options:**

- [required] `-dir`/`--directory`<br/>Path to a directory that contains at least a 'deployment.py'

- `--data`<br/>The input data of the request<br/>This option can be provided multiple times in a single command

- `-f`/`--json_file`<br/>Path to json file containing the input data of the request

- `--plain`<br/>Set the input data as plain text


<br/>
