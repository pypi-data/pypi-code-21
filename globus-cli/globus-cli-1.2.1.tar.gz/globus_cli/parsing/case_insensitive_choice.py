import click


class CaseInsensitiveChoice(click.Choice):
    """
    Customized Choice type to get case-insensitive options without changing the
    click tokenizer to make *everything* lowercase.
    I've requested that support for this be added to `click` itself, which
    would obsolete this module: https://github.com/pallets/click/issues/569
    """
    def convert(self, value, param, ctx):
        if value is None:
            return None
        return super(CaseInsensitiveChoice, self).convert(
            value.lower(), param, ctx)
