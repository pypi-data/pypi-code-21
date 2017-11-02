import requests
import click
import os
import json
import yaml

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def default_config():
    return {
        'server' : 'https://yadage.cern.ch'
    }

def load_config(configfile = None):
    config = default_config()
    configfile = configfile or os.path.expanduser('~/.ydgsvc.json')
    if os.path.exists(configfile):
        config.update(**json.load(open(configfile)))
    return config

def options_from_eqdelimstring(opts):
    options = {}
    for x in opts:
        key, value = x.split('=')
        options[key] = yaml.load(value)
    return options

def headers(config):
    auth_token = os.environ.get('YAD_TOKEN')
    if not auth_token:
        auth_token = config.get('auth_token')
    if not auth_token:
        raise RuntimeError('could not find auth token, either set YAD_TOKEN or edit ~/.ydgsvc.json')

    return {
        'Authorization': 'Bearer {}'.format(auth_token),
        'Content-Type': 'application/json'
    }

@click.group()
def yad():
    pass

@yad.command()
@click.argument('workflow')
@click.argument('toplevel')
@click.option('-c','--config', help = 'config file', default = None)
@click.option('-p','--parameter', help = 'output', multiple = True)
@click.option('-f','--parameter_file', help = 'output')
@click.option('-o','--output', help = 'output', multiple = True)
def submit(workflow,toplevel,config, output,parameter, parameter_file):
    cfg = load_config(config)

    if parameter_file:
        parameters = yaml.load(open(parameter_file))
    else:
        parameters = {}
    parameters.update(**options_from_eqdelimstring(parameter))

    wflowname = 'submit'
    if not output:
        raise RuntimeError('need some outputs')
    outputs = ','.join(output)

    inputURL = ''

    submit_url = '{}/workflow_submit'.format(cfg['server'])
    submission_data = {
      "outputs": outputs, "workflow": workflow, "toplevel": toplevel,
      "inputURL": inputURL,
      "preset_pars": parameters,
      "wflowname": wflowname
    }
    r = requests.post(submit_url,
        data = json.dumps(submission_data),
        headers = headers(cfg),
        verify=False
    )
    if not r.ok:
        raise RuntimeError('submission failed %s', r.content)
    click.echo(json.dumps(r.json()))

@yad.command()
@click.argument('workflow_id')
@click.option('-c','--config', help = 'config file', default = None)
def status(config, workflow_id):
    cfg = load_config(config)
    status_url = '{}/jobstatus/{}'.format(cfg['server'],workflow_id)
    r = requests.get(status_url, verify = False, headers = headers(cfg))
    if not r.ok:
        raise RuntimeError('submission failed %s', r.content)
    click.echo(json.dumps(r.json()))


# Thanks SO
# https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
def download_file(url,local_filename, request_opts):
    local_filename = local_filename or url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True, **request_opts)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename

@yad.command()
@click.argument('workflow_id')
@click.argument('resultfile')
@click.option('-c','--config', help = 'config file', default = None)
@click.option('-o','--output')
def get(config,workflow_id,resultfile, output):
    cfg = load_config(config)
    result_url = '{}/results/{}/{}'.format(cfg['server'],workflow_id,resultfile)
    download_file(result_url, output, request_opts = dict(
        verify = False,
        headers = headers(cfg)
    ))
    download_file
