
## ubiops complete

**Command:** `ubiops complete`

**Description:**

Get the completion script for your shell to enable shell completion.

Run the command below for your shell of choice to enable shell completion for the current shell session. Add the
command to your `~/.bashrc`, `~/.zshrc` or `~/.config/fish/config.fish` if you want to make it persistent.


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


```bash
ubiops complete bash > ~/.ubiops-complete.bash
```

And then add to your `~/.bashrc`:
```bash
. ~/.ubiops-complete.bash
```

Restart your shell for the change to take effect.

**Arguments:**

- [required] `shell`



**Options:** - 
<br/>
