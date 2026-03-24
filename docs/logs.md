
## ubiops logs

**Command:** `ubiops logs`

**Description:**

Get the logs of your project.

If start < end, the logs are searched forward.
If start > end, the logs are searched backward.


Use the `query` option to filter logs.
e.g. text search:
```
--query '|= "text"'
```
e.g. Deployment filters:
```
--query '| deployment_name="deployment-1" | deployment_version="v1"'
```
e.g. Pipeline filters:
```
--query '| pipeline_name="pipeline-1" | pipeline_version="v1"'
```
e.g. Text search + request filters
```
--query '|= "text" | deployment_request_id="request-id-1"'
```


Available line filters:
- `|=` for exact string match
- `|~` for regex match
- `!=` for negative exact string match (matched logs will be excluded)
- `!~` for negative regex match (matched logs will be excluded)


Available label filters (come after `|`):
- `=` for exact match
- `=~` for regex match
- `!=` for negative exact match (matched logs will be excluded)
- `!~` for negative regex match (matched logs will be excluded)


Label filters can be chained using connectors `and` (equivalent to `|`) and `or`.
e.g. Specific deployment version
```
--query '| deployment_name="my-deployment" and deployment_version="v1"'
```
e.g. All logs of request 1 and request 2
```
--query '| deployment_request_id="request-id-1" or deployment_request_id="request-id-2"'
```

**Arguments:** - 

**Options:**

- `--start`<br/>Start of the interval for which the logs are retrieved [default = now]

- `--end`<br/>End of the interval for which the logs are retrieved [default = yesterday]

- `--query`/`-q`<br/>Query to filter logs, see command description for examples

- `--limit`/`-n`<br/>Limit of the logs response. The maximum value is 5000.

- `--no_pager`<br/>Return logs directly without pager

- `-fmt`/`--format`<br/>The output format<br/>Allowed values: `oneline`, `reference`, `extended`, `json`


<br/>
