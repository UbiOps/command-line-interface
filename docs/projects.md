## ubiops projects

**Command:** `ubiops projects`

**Alias:** `ubiops prj`


<br/>

### ubiops projects list

**Command:** `ubiops projects list`

**Description:**

List all your projects.

To select a project, use: `ubiops current_project set <project_name>`

**Arguments:** - 

**Options:**

- `-o`/`--organization_name`<br/>The organization name

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops projects get

**Command:** `ubiops projects get`

**Description:**

Get the details of a project.

**Arguments:**

- [required] `project_name`



**Options:**

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops projects create

**Command:** `ubiops projects create`

**Description:**

Create a new project.

The created project will automatically become the current project.

When only one organization exists, it will automatically be selected.
When multiple organizations exist and the `<organization_name>` option is not provided, the user will be prompted
to choose the organization.

No organization yet? Please, use the user interface and follow the registration process or contact sales.

Use the `<overwrite>` flag to not fail when the project already exists. The project will still automatically become
the current project.

**Arguments:**

- [required] `project_name`



**Options:**

- `-o`/`--organization_name`<br/>The organization name

- `--overwrite`<br/>Whether you want to overwrite if exists

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops projects delete

**Command:** `ubiops projects delete`

**Description:**

Delete a project.

**Arguments:**

- [required] `project_name`



**Options:**

- `-y`/`--assume_yes`<br/>Assume yes instead of asking for confirmation

- `-q`/`--quiet`<br/>Suppress informational messages


<br/>


***
<br/>

## ubiops current_project

**Command:** `ubiops current_project`

**Alias:** `ubiops cprj`


<br/>

### ubiops current_project get

**Command:** `ubiops current_project get`

**Description:**

Get your current CLI project.

**Arguments:** - 

**Options:**

- `-fmt`/`--format`<br/>The output format


<br/>

### ubiops current_project set

**Command:** `ubiops current_project set`

**Description:**

Set your current CLI project.

**Arguments:**

- [required] `project_name`



**Options:**

- `-fmt`/`--format`<br/>The output format


<br/>
