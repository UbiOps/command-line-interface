# ubiops-cli

Command Line Interface to interact with the [UbiOps](https://ubiops.com) API (v2.1).

Includes:

- Managing projects
- Managing deployments
- Managing versions
- Managing pipelines
- Managing schedules
- Managing buckets and files
- Managing environment variables
- ZIP folder and deploy
- Making requests
- View logs
- View audit events


For more information, please visit [https://ubiops.com/docs](https://ubiops.com/docs)


## Examples

An example notebook can be found <a target="_blank" href="https://github.com/UbiOps/command-line-interface/blob/master/examples/quickstart-simple-CLI.ipynb">here</a>.


## Requirements

Python 3.6+


## Installation & Usage

```bash
pip install ubiops-cli
```

Then use the package like this:
```bash
ubiops --version
```

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

Sign in using your credentials:
```bash
ubiops signin
```

Sign in using a service token:
```bash
ubiops signin --token
```

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
Config | [docs/config.md](docs/config.md)
Deployments | [docs/deployments.md](docs/deployments.md)
Deployment Versions | [docs/deployment_versions.md](docs/deployment_versions.md)
Version Revisions | [docs/version_revisions.md](docs/version_revisions.md)
Version Builds | [docs/version_builds.md](docs/version_builds.md)
Environments | [docs/environments.md](docs/environments.md)
Environment Revisions | [docs/environment_revisions.md](docs/environment_revisions.md)
Environment Builds | [docs/environment_builds.md](docs/environment_builds.md)
Pipelines | [docs/pipelines.md](docs/pipelines.md)
Pipeline Versions | [docs/pipeline_versions.md](docs/pipeline_versions.md)
Blobs | [docs/blobs.md](docs/blobs.md)
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
This software uses the library [ignorance](https://github.com/snark/ignorance) by Steve Cook - see [license](https://github.com/UbiOps/command-line-interface/blob/master/ubiops_cli/ignore/LICENSE).

