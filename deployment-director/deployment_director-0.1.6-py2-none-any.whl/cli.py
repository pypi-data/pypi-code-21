import click
import yaml

from DeploymentDirector import DeploymentDirector

@click.command()
@click.option('--ci-name', help='Name of the CI product deployment director is running under', envvar='CI_NAME')
@click.option('--dry-run', '-n', help='Do not actually execute any actions, just print them out')
@click.option('--verbose', '-v', count=True)
@click.argument('rules_file', type=click.File('r'))
def main(rules_file, **options):
  rules = yaml.load(rules_file)
  dd = DeploymentDirector(rules, options=options)
  dd.run_deployment()
  