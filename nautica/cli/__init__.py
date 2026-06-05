import click

class AliasedGroup(click.Group):
    def command(self, *args, aliases: list[str] = None, **kwargs):
        decorator = super().command(*args, **kwargs)
        def wrapper(func):
            cmd = decorator(func)
            for alias in (aliases or []):
                self.add_command(cmd, name=alias)
            return cmd
        return wrapper


@click.group(cls=AliasedGroup)
def cli(): ...