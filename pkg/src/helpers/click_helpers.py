import click
import copy



class CustomGroup(click.Group):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alias_to_original = {}
        self.original_to_aliases = {}

    def add_command(self, *args, **kwargs):
        if isinstance(args[0].name, list):
            original_name = args[0].name[0]

            # Define aliases
            self.original_to_aliases[original_name] = args[0].name[1:]
            for n in args[0].name[1:]:
                self.alias_to_original[n] = original_name

            self.commands[original_name] = args[0]
        else:
            self.commands[args[0].name] = args[0]

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        # Handle alias
        if cmd_name in self.alias_to_original:
            return click.Group.get_command(self, ctx, self.alias_to_original[cmd_name])

    def format_commands(self, ctx, formatter):
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if cmd.hidden:
                continue

            commands.append((subcommand, cmd))

        # Allow for 3 times the default spacing
        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                # Add (aliases) in Commands help overview
                if subcommand in self.original_to_aliases:
                    subcommand = "%s (%s)" % (subcommand, ", ".join(self.original_to_aliases[subcommand]))
                rows.append((subcommand, help))

            if rows:
                with formatter.section("Commands"):
                    formatter.write_dl(rows)
