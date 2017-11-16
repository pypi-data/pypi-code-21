# -*- coding: utf-8 -*-
import json

import click

from jawa.df import DexFile


@click.group()
def info():
    pass


@info.command(help='Display header information for DEX files.')
@click.argument('input', type=click.File('rb'))
def dex(input):
    df = DexFile(input)
    op = {
        'format': {
            'version': df.version,
            'little_endian': df.little_endian,
        },
        'verification': {
            'signature': ''.join(
                format(b, '02X') for b in
                df.signature
            ),
            'checksum': df.checksum,
        },
        'link_segment': {
            'offset': df.link_off,
            'size': df.link_size
        },
        'map_segment': {
            'offset': df.map_off
        }
    }

    click.echo(json.dumps(op, sort_keys=True, indent=2))
