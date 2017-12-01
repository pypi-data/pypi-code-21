import click


class HiddenOption(click.Option):
    """
    HiddenOption -- absent from Help text.

    Supported in latest and greatest version of Click, but not old versions, so
    use generic 'cls=HiddenOption' to get the desired behavior.
    """
    def get_help_record(self, ctx):
        """
        Has "None" as its help record. All that's needed.
        """
        return
