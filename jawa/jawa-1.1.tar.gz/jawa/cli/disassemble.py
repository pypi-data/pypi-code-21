# -*- coding: utf-8 -*-
import click

from jawa.cf import ClassFile


@click.group()
def dism():
    pass


@dism.command(help=(
    'A mostly-compatible clone of the javap disassembler.'
))
@click.option('-v', '-verbose', is_flag=True)
@click.option(
    '-l',
    'tables',
    is_flag=True,
    help='Print line number and local variable tables'
)
@click.option(
    '-public',
    'scope',
    flag_value='public'
)
@click.option(
    '-protected',
    'scope',
    flag_value='protected'
)
@click.option(
    '-package',
    'scope',
    flag_value='package',
    default=True
)
@click.option(
    '-p',
    '-private',
    'scope',
    flag_value='private'
)
@click.option(
    '-c',
    'disassemble',
    is_flag=True
)
@click.option(
    '-s',
    is_flag=True
)
@click.option(
    '-constants',
    is_flag=True
)
@click.option(
    '-classpath',
    '-cp',
    type=click.Path(resolve_path=True)
)
@click.option(
    '-bootclasspath',
    type=click.Path(resolve_path=True)
)
@click.argument('classes', nargs=-1)
def javap(**args):
    for class_ in args['classes']:
        with open(class_, 'rb') as fin:
            cf = ClassFile(fin)
            _javap(cf, args)


def _javap(cf, args):
    flags = cf.access_flags.to_dict()
    flags = [k[4:] for k, v in flags.items() if v]

    click.echo(
        '{flags} {cf.this.name.value} '.format(
            cf=cf,
            flags=' '.join(flags)
        ),
        nl=False
    )
    if cf.super_.name.value != 'java/lang/Object':
        click.echo('extends {cf.super_.name.value} '.format(
            cf=cf
        ), nl=False)

    if cf.interfaces:
        click.echo('{what} {ifs} '.format(
            what='extends' if cf.access_flags.acc_interface else 'implements',
            ifs=', '.join(c.name.value for c in cf.interfaces)
        ), nl=False)

    click.echo('{')

    click.echo('}')
