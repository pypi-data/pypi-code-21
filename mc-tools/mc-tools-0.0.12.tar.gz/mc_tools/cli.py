import click


@click.group(name="mua")
def cli():
    pass

# Init subcommands
import mc_tools.ya_disk_publish.publish