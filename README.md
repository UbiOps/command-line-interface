# ubiops-cli
Command Line Interface to interact with the [UbiOps](https://ubiops.com) API (v2.1).

Includes:
- Managing projects
- Managing deployments
- Deploying new deployment versions
- Managing pipelines
- Making requests

For more information, please visit [https://ubiops.com/docs](https://ubiops.com/docs)

## Requirements.

Python 3.5+

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
If you successfully installed ubiops-cli but `ubiops --version` gives the following error: `ubiops: command not found`, 
you are likely missing the directory in you PATH variable where PIP installs scripts. You could solve this by adding 
the directory to your PATH variable. Please, visit 
https://packaging.python.org/tutorials/installing-packages/#installing-to-the-user-site for more information.
- Linux and macOS: `~/.local/bin`
- Windows: something like `C:\Users\Username\AppData\Roaming\Python36\Scripts`

## Getting Started

Please follow the installation procedure and then run the following:

Show the version of ubiops-cli:

```bash
ubiops --version
```

### Signin & signout

Signin using your credentials:

```bash
ubiops signin
```

Signin using a service token:

```bash
ubiops signin --token
```

Show if you are authorized:

```bash
ubiops status
```

Signout:

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
ubiops current_project set <MY_PROJECT_NAME>
```

Show your deployments:

```bash
ubiops deployments list
```

## Documentation

Category | Documentation reference
---- | ---- 
Authentication | [docs/authentication.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/authentication.md)
Projects | [docs/projects.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/projects.md)
Config | [docs/config.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/config.md)
Deployments | [docs/deployments.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/deployments.md)
Deployment Versions | [docs/deployment_versions.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/deployment_versions.md)
Pipelines | [docs/pipelines.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/pipelines.md)
Blobs | [docs/blobs.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/blobs.md)
Environment Variables | [docs/environment_variables.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/environment_variables.md)
Logs | [docs/logs.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/logs.md)
Audit Events | [docs/audit_events.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/audit_events.md)
Schedules | [docs/schedules.md](https://github.com/UbiOps/command-line-interface/tree/master/docs/schedules.md)


### Attribution
This software uses the library [ignorance](https://github.com/snark/ignorance) by Steve Cook - see [license](https://github.com/UbiOps/command-line-interface/blob/master/pkg/ignore/LICENSE).
