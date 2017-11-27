import requests
import click
import os
import sys
import json
import yaml
import requests
import urllib3
from .client import Client

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def options_from_eqdelimstring(opts):
    options = {}
    for x in opts:
        key, value = x.split('=')
        options[key] = yaml.load(value)
    return options

@click.group()
def yad():
    pass

@yad.command()
@click.argument('workflow')
@click.option('-t','--toplevel', help = 'toplevel', default = None)
@click.option('--local/--remote', default = False)
@click.option('-c','--config', help = 'config file', default = None)
@click.option('-p','--parameter', help = 'output', multiple = True)
@click.option('-f','--parameter_file', help = 'output')
@click.option('--json-output/--human-readable', default = False, help = 'JSON output?')
@click.option('-i','--input', help = 'input')
@click.option('-o','--output', help = 'output', multiple = True)
def submit(workflow,toplevel,json_output,local,input,config, output,parameter, parameter_file):
    if parameter_file:
        parameters = yaml.load(open(parameter_file))
    else:
        parameters = {}
    parameters.update(**options_from_eqdelimstring(parameter))

    c = Client(config)
    response = c.submit(workflow,toplevel,parameters,input,output,local)

    if not json_output:
        click.secho('submitted workflow. Monitor it at  {}/monitor/{}'.format(c.config['server'],response['jobguid']))
    else:
        click.echo(json.dumps(response))

@yad.command()
@click.argument('workflow_id')
@click.option('-c','--config', help = 'config file', default = None)
def status(config, workflow_id):
    c = Client(config)
    status = c.status(workflow_id)
    click.echo(json.dumps(status))

@yad.command()
@click.argument('workflow_id')
@click.argument('resultfile')
@click.option('-c','--config', help = 'config file', default = None)
@click.option('-o','--output')
@click.option('--stdout/--no-stdout')
def get(config,workflow_id,resultfile, output, stdout):
    c = Client(config)
    c.get(workflow_id,resultfile, output, sys.stdout if stdout else None)

@yad.command()
@click.argument('filepath')
@click.option('-c','--config', help = 'config file', default = None)
def upload(filepath, config):
    c = Client(config)
    response = c.upload(filepath)
    click.secho('\n')
    click.secho('uploaded file id is: {}'.format(response['file_id']))

@yad.command()
@click.option('-s','--server', help = 'server', default = None)
@click.option('-c','--config', help = 'config file', default = None)
def login(server,config):

    c = Client(config)

    click.secho('''
yadage service
--------------
Hi, if you already have a API key for {server}
please enter it below.

If not, please visit {server}/profile (make sure
you are logged in or click 'Login' on the upper right
hand side) and click 'Generate API Key'
'''.format(server = c.config['server']))
    auth_token = click.prompt('Please enter your API key', hide_input = True)

    c.login(server,auth_token)

@yad.command()
@click.argument('jobid')
@click.option('--json-lines/--no-json', default = False)
@click.option('-s','--server', help = 'server', default = None)
@click.option('-t','--topic', help = 'topic', default = 'run')
@click.option('-c','--config', help = 'config file', default = None)
def job_logs(jobid,server,config,json_lines,topic):
    c = Client(config)
    for l in c.job_logs(jobid,json_lines,topic):
        click.secho(l)

@yad.command()
@click.argument('wflowid')
@click.option('--json-lines/--no-json', default = False)
@click.option('-s','--server', help = 'server', default = None)
@click.option('-t','--topic', help = 'topic', default = 'log')
@click.option('-c','--config', help = 'config file', default = None)
def wflow_logs(wflowid,server,config,json_lines,topic):
    c = Client(config)
    c.wflow_logs(wflowid,json_lines,topic)
