import click

@click.command()
@click.argument('project', required=True)
@click.option('-s', '--sample', default=0, help='')
def parse_command(sample, project):
    print(project, sample)


def main():
    parse_command()