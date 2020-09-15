
## ubiops projects
### ubiops projects list

**Description:**

List all your projects.

To select a project, use: `ubiops current_project set <project_name>`

**Arguments:** - 

**Options:**
- `-o`/`--organization_name`

  The organization name.
- `-fmt`/`--format`

  The output format.

### ubiops projects get

**Description:**

Get the details of a project.

**Arguments:**
- [required] `project_name`

**Options:**
- `-fmt`/`--format`

  The output format.

### ubiops projects create

**Description:**

Create a new project.

The created project will automatically become the current project.

When only one organization exists, it will automatically be selected.
When multiple organizations exist and the <organization_name> option is not provided, the user will be prompted
to choose the organization.

No organization yet? Please, use the user interface and follow the registration process or contact sales.

**Arguments:**
- [required] `project_name`

**Options:**
- `-o`/`--organization_name`

  The organization name.
- `-fmt`/`--format`

  The output format.

### ubiops projects delete

**Description:**

Delete a project.

**Arguments:**
- [required] `project_name`

**Options:**
- `-y`/`--assume_yes`

  Assume yes instead of asking for confirmation.
- `-q`/`--quiet`

  Suppress informational messages.

## ubiops current_project
### ubiops current_project get

**Description:**

Get your current project of the command line interface.

**Arguments:** - 

**Options:**
- `-fmt`/`--format`

  The output format.

### ubiops current_project set

**Description:**

Set your current project of the command line interface.

**Arguments:**
- [required] `project_name`

**Options:**
- `-fmt`/`--format`

  The output format.
