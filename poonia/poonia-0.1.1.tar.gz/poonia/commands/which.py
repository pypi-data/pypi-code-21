import click
import os, sys, glob

@click.command(help='Search PATH')
@click.argument('file')
def which(file):
    click.echo(sys.path)