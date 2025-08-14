try:  # >= Python 3.9
    from importlib import resources as impresources
except ImportError:  # <= Python 3.8
    import importlib_resources as impresources

import click

from ubiops_cli import complete
from ubiops_cli.src.helpers import options


@click.command(name="complete", short_help="Enable shell completion")
@options.SHELL
def commands(shell):
    """
    Get the completion script for your shell to enable shell completion.

    Run the command below for your shell of choice to enable shell completion for the current shell session. Add the
    command to your `~/.bashrc`, `~/.zshrc` or `~/.config/fish/config.fish` if you want to make it persistent.

    \b
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

    Please, be aware that if you run the ubiops-cli in a virtual environment, you should only enable shell completion
    after activating the virtual environment, or write the content to a file on your system such that it can be found
    without the virtual environment being activated. E.g. for Bash:

    \b
    ```bash
    ubiops complete bash > ~/.ubiops-complete.bash
    ```
    \b
    And then add to your `~/.bashrc`:
    ```bash
    . ~/.ubiops-complete.bash
    ```

    Restart your shell for the change to take effect.
    """

    script = f"ubiops-complete.{shell.lower()}"

    try:
        inp_file = impresources.files(complete) / script
        with inp_file.open("rb") as f:
            click.echo(f.read())
    except AttributeError:
        # <= Python 3.9, deprecated in Python 3.11
        click.echo(impresources.read_text(complete, script))
