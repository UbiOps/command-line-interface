import click
import copy


class CustomGroup(click.Group):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aliases = []

    def add_command(self, *args, **kwargs):
        """Behaves the same as `click.Group.group()` except if passed
        a list of names, all after the first will be aliases for the first.
        """

        if isinstance(args[0].name, list):
            for n in args[0].name[1:]:
                self.aliases.append(n)
                alias = copy.deepcopy(args[0])
                alias.short_help = "Alias for '%s'" % click.style(args[0].name[0], underline=True)
                self.commands[n] = alias

            original = copy.deepcopy(args[0])
            original_name = args[0].name[0]
            self.commands[original_name] = original
        else:
            self.commands[args[0].name] = args[0]
