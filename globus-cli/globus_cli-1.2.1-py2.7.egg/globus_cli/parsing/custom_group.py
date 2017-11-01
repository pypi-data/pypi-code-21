import click

from globus_cli.safeio import safeprint
from globus_cli.parsing.shared_options import common_options


class GlobusCommandGroup(click.Group):
    """
    This is a click.Group with any customizations which we deem necessary
    *everywhere*.

    In particular, at present it provides a better form of handling for
    no_args_is_help. If that flag is set, helptext will be triggered not only
    off of cases where there are no arguments at all, but also cases where
    there are options, but no subcommand (positional arg) is given.
    """
    def invoke(self, ctx):
        # if no subcommand was given (but, potentially, flags were passed),
        # ctx.protected_args will be empty
        # improves upon the built-in detection given on click.Group by
        # no_args_is_help , since that treats options (without a subcommand) as
        # being arguments and blows up with a "Missing command" failure
        # for reference to the original version (as of 2017-02-26):
        # https://github.com/pallets/click/blob/02ea9ee7e864581258b4902d6e6c1264b0226b9f/click/core.py#L1039-L1052
        if self.no_args_is_help and not ctx.protected_args:
            safeprint(ctx.get_help())
            ctx.exit()
        return super(GlobusCommandGroup, self).invoke(ctx)


def globus_group(*args, **kwargs):
    """
    Wrapper over click.group which sets GlobusCommandGroup as the Class

    Caution!
    Don't get snake-bitten by this. `globus_group` is a decorator which MUST
    take arguments. It is not wrapped in our common detect-and-decorate pattern
    to allow it to be used bare -- that wouldn't work (unnamed groups? weird
    stuff)
    """
    def inner_decorator(f):
        f = click.group(*args, cls=GlobusCommandGroup, **kwargs)(f)
        f = common_options(f)
        return f
    return inner_decorator
