# ubiops-cli

Command Line Interface to interact with the [UbiOps](https://ubiops.com) API (v2.1).

Includes:

- Managing projects
- Managing deployments
- Managing versions
- Managing environments
- Managing pipelines
- Managing schedules
- Managing buckets and files
- Managing environment variables
- ZIP folder and deploy
- Making requests
- View logs
- View audit events
- Validate requirements.txt/ubiops.yaml
- Run your deployment package locally

For more information, please visit [https://ubiops.com/docs](https://ubiops.com/docs)


## Examples

An example notebook can be found <a target="_blank" href="https://github.com/UbiOps/command-line-interface/blob/master/examples/quickstart-simple-CLI.ipynb">here</a>.


## Requirements

Python 3.7+


## Installation & Usage

```bash
pip install ubiops-cli
```

Then use the package like this:
```bash
ubiops --version
```

### Shell completion

Optionally enable shell completion for your shell of choice.

Run the command below for your shell of choice to enable shell completion for the current shell session. Add the command
to your `~/.bashrc`, `~/.zshrc` or `~/.config/fish/config.fish` if you want to make it persistent.

- For Bash, add the following line to your `~/.bashrc`:
	```bash
	. <(ubiops complete bash)
	```

- For Zsh, add the following line to your `~/.zshrc`:
	```zsh
	. <(ubiops complete zsh)
	```

- For Fish, add the following line to your `~/.config/fish/config.fish`:
	```fish
	ubiops complete fish | .
	```

Restart your shell for the change to take effect.

Please, be aware that if you run the ubiops-cli in a virtual environment, you should only enable shell completion after
activating the virtual environment, or write the content to a file on your system such that it can be found without
the virtual environment being activated. E.g. for Bash:

```bash
ubiops complete bash > ~/.ubiops-complete.bash
```

And then add to your `~/.bashrc`:

```bash
. ~/.ubiops-complete.bash
```

Restart your shell for the change to take effect.


## Troubleshooting

#### Command not found

If you successfully installed ubiops-cli but `ubiops --version` gives the following error: `ubiops: command not found`, you are likely missing the directory in you PATH variable where PIP installs scripts. You could solve this by adding the directory to your PATH variable. Please, visit https://packaging.python.org/tutorials/installing-packages/#installing-to-the-user-site for more information.

- Linux and macOS: `~/.local/bin`
- Windows: something like `C:\Users\Username\AppData\Roaming\Python36\Scripts`


## Getting Started

Please follow the installation procedure and then run the following:

Show the version of ubiops-cli:
```bash
ubiops --version
```

### Sign in & sign out

The default API host url is https://api.ubiops.com/v2.1/ (UbiOps SaaS). For on-premises installations of UbiOps, set
your API url using the `--api` option in the signin commands below.

- Sign in using your credentials (username/password):
    ```bash
    ubiops signin --api https://api.ubiops.com/v2.1/
    ```

    You will be prompted to fill in your credentials (email + password). It's also possible to provide your email and
    password directly using the `--email` and `--password` options.

    A temporary access token is generated in the background, which provides you access for 3 hours.


- Sign in using a service token:
    ```bash
    ubiops signin --api https://api.ubiops.com/v2.1/ --token
    ```

    You will be prompted to fill in your token. It's also possible to provide your token directly using the `--password`
    option.


Show if you are authorized:
```bash
ubiops status
```

Sign out:
```bash
ubiops signout
```

### Managing resources

Show your projects:
```bash
ubiops projects list
```

Set a current project:
```bash
ubiops current_project set <project_name>
```

Show your deployments:
```bash
ubiops deployments list
```


## Documentation

Category | Documentation reference
---- | ---- 
Authentication | [docs/authentication.md](docs/authentication.md)
Projects | [docs/projects.md](docs/projects.md)
Complete | [docs/complete.md](docs/complete.md)
Config | [docs/config.md](docs/config.md)
Deployments | [docs/deployments.md](docs/deployments.md)
Deployment Versions | [docs/deployment_versions.md](docs/deployment_versions.md)
Version Revisions | [docs/version_revisions.md](docs/version_revisions.md)
Environments | [docs/environments.md](docs/environments.md)
Environment Revisions | [docs/environment_revisions.md](docs/environment_revisions.md)
Environment Builds | [docs/environment_builds.md](docs/environment_builds.md)
Instance Type Groups | [docs/instance_type_groups.md](docs/instance_type_groups.md)
Instance Types | [docs/instance_types.md](docs/instance_types.md)
Instances | [docs/instances.md](docs/instances.md)
Project Instances | [docs/project_instances.md](docs/project_instances.md)
Pipelines | [docs/pipelines.md](docs/pipelines.md)
Pipeline Versions | [docs/pipeline_versions.md](docs/pipeline_versions.md)
Buckets | [docs/buckets.md](docs/buckets.md)
Files | [docs/files.md](docs/files.md)
Environment Variables | [docs/environment_variables.md](docs/environment_variables.md)
Logs | [docs/logs.md](docs/logs.md)
Audit Events | [docs/audit_events.md](docs/audit_events.md)
Schedules | [docs/schedules.md](docs/schedules.md)
Exports | [docs/exports.md](docs/exports.md)
Imports | [docs/imports.md](docs/imports.md)
Validate | [docs/validate.md](docs/validate.md)
Run Local | [docs/run_local.md](docs/run_local.md)


### Attribution
This software uses the library [gitignorefile](https://github.com/excitoon/gitignorefile) by Vladimir Chebotarev - see [license](https://github.com/UbiOps/command-line-interface/blob/master/ubiops_cli/gitignorefile/LICENSE).
