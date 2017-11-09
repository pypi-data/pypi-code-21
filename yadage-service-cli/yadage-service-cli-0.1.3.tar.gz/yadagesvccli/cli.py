import requests
import click
import os
import json
import yaml
import requests
import shutil
import tempfile
from requests_toolbelt.multipart import encoder
from clint.textui.progress import Bar as ProgressBar

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def default_config():
    return {
        'server' : 'https://yadage.cern.ch'
    }

DEFAULT_CONFIGFILE = os.path.expanduser('~/.ydgsvc.json')


def load_config(configfile):
    config = default_config()
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

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

@click.group()
def yad():
    pass

@yad.command()
@click.argument('workflow')
@click.option('-t','--toplevel', help = 'toplevel', default = None)
@click.option('--local/--remote', default = False)
@click.option('-c','--config', help = 'config file', default = DEFAULT_CONFIGFILE)
@click.option('-p','--parameter', help = 'output', multiple = True)
@click.option('-f','--parameter_file', help = 'output')
@click.option('-i','--input', help = 'input')
@click.option('-o','--output', help = 'output', multiple = True)
def submit(workflow,toplevel,local,input,config, output,parameter, parameter_file):
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
    if input and not input.startswith('http'):
        if os.path.exists(input):
            if os.path.isdir(input):
                tmpfilename = tempfile.mktemp()
                shutil.make_archive(tmpfilename, 'zip', input)
                r = upload_file(tmpfilename+'.zip', cfg)
                os.remove(tmpfilename+'.zip')
            else:
                r = upload_file(input, cfg)
            inputURL = '{}/workflow_input/{}'.format(cfg['server'], r['file_id'])
            click.secho('uploaded file to {}'.format(inputURL))
        else:
            raise RuntimeError('not sure how to handle input')
    submit_url = '{}/workflow_submit'.format(cfg['server'])

    submission_data = {
      "outputs": outputs,
      "inputURL": inputURL,
      "preset_pars": parameters,
      "wflowname": wflowname
    }

    if local:
        import yadageschemas
        submission_data['workflow']=yadageschemas.load(workflow, toplevel or os.getcwd(), 'yadage/workflow-schema')
        submission_data['toplevel']=''
    else:
        submission_data['workflow']=workflow
        submission_data['toplevel']=toplevel

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
@click.option('-c','--config', help = 'config file', default = DEFAULT_CONFIGFILE)
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
@click.option('-c','--config', help = 'config file', default = DEFAULT_CONFIGFILE)
@click.option('-o','--output')
def get(config,workflow_id,resultfile, output):
    cfg = load_config(config)
    result_url = '{}/results/{}/{}'.format(cfg['server'],workflow_id,resultfile)
    download_file(result_url, output, request_opts = dict(
        verify = False,
        headers = headers(cfg)
    ))

@yad.command()
@click.argument('filepath')
@click.option('-c','--config', help = 'config file', default = DEFAULT_CONFIGFILE)
def upload(filepath, config):
    cfg = load_config(config)
    response = upload_file(filepath,cfg)
    click.secho('\n')
    click.secho('uploaded file id is: {}'.format(response['file_id']))


def upload_file(filepath,cfg):
    def create_callback(encoder):
        encoder_len = encoder.len
        bar = ProgressBar(expected_size=encoder_len, filled_char='=')

        def callback(monitor):
            bar.show(monitor.bytes_read)

        return callback

    e = encoder.MultipartEncoder(
        fields={'upload_file': ('filename', open(filepath,'rb'), 'text/plain')}
    )
    m = encoder.MultipartEncoderMonitor(e, create_callback(e))

    head = headers(cfg)
    head['Content-Type'] = m.content_type
    r = requests.post('{}/upload'.format(cfg['server']), data=m, verify = False,headers=head)

    response = r.json()
    return response


@yad.command()
@click.option('-s','--server', help = 'server', default = None)
@click.option('-c','--config', help = 'config file', default = DEFAULT_CONFIGFILE)
def login(server,config):
    cfg = load_config(config)
    if server:
        cfg['server'] = server
    click.secho('''
yadage service
--------------
Hi, if you already have a API key for {server}
please enter it below.

If not, please visit {server}/profile (make sure
you are logged in or click 'Login' on the upper right
hand side) and click 'Generate API Key'
'''.format(server = cfg['server']))
    value = click.prompt('Please enter your API key')
    cfg['auth_token'] = value
    json.dump(cfg,open(config,'w'))
