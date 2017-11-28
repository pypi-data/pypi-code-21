import click

@click.group(invoke_without_command=True,
             context_settings=dict(allow_extra_args=True,
                                   ignore_unknown_options=True))
@click.argument("args", nargs=-1)
@click.pass_context
def cli(ctx, args):
    if ctx.invoked_subcommand is None:
        click.echo('I was invoked without subcommand')
        print ctx.params
        sync.main(args=ctx.params["args"])
        # ctx.invoke(sync, args=ctx.params["args"])
    else:
        click.echo('I am about to invoke %s' % ctx.invoked_subcommand)

@cli.command()
@click.option("-v", is_flag=True, default=False)
@click.argument("src", nargs=-1)
def sync(v, src):
    click.echo(v)
    click.echo('The subcommand')
    click.echo(src)

if __name__ == "__main__":
    cli()