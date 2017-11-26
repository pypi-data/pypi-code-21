import os
import requests
from requests_toolbelt.multipart import encoder
from clint.textui.progress import Bar as ProgressBar
import json
import tempfile
import shutil
import click

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

# Thanks SO
# https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
def download_file(url,stream, request_opts):
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True, **request_opts)
    for chunk in r.iter_content(chunk_size=1024):
        if chunk: # filter out keep-alive new chunks
            stream.write(chunk)

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

class Client(object):
    def __init__(self,config = None ):
        self.configfile = config or DEFAULT_CONFIGFILE
        self.config = load_config(self.configfile)

    def submit(self,workflow,toplevel,parameters,input,outputs,local):
        wflowname = 'submit'
        if not outputs:
            raise RuntimeError('need some outputs')
        outputs = ','.join(outputs)

        inputURL = ''
        inputAuth = False
        if input and not input.startswith('http'):
            if os.path.exists(input):
                if os.path.isdir(input):
                    tmpfilename = tempfile.mktemp()
                    shutil.make_archive(tmpfilename, 'zip', input)
                    r = upload_file(tmpfilename+'.zip', self.config)
                    os.remove(tmpfilename+'.zip')
                else:
                    r = upload_file(input, self.config)
                inputURL = '{}/workflow_input/{}'.format(self.config['server'], r['file_id'])
                inputAuth = True
            else:
                raise RuntimeError('not sure how to handle input')
        submit_url = '{}/workflow_submit'.format(self.config['server'])

        submission_data = {
          "outputs": outputs,
          "inputURL": inputURL,
          "inputAuth": inputAuth,
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
            headers = headers(self.config),
            verify=False
        )
        if not r.ok:
            raise RuntimeError('submission failed %s', r.content)

        response = r.json()
        return response

    def status(self,workflow_id):
        status_url = '{}/jobstatus/{}'.format(self.config['server'],workflow_id)
        r = requests.get(status_url, verify = False, headers = headers(self.config))
        if not r.ok:
            raise RuntimeError('submission failed %s', r.content)
        return r.json()

    def get(self,workflow_id,resultfile, output, stdout):
        result_url = '{}/results/{}/{}'.format(self.config['server'],workflow_id,resultfile)

        import sys
        if stdout:
            output_stream = sys.stdout
        else:
            output_stream = open(output or result_url.split('/')[-1], 'wb')

        download_file(result_url, output_stream, request_opts = dict(
            verify = False,
            headers = headers(self.config)
        ))
        output_stream.close()

    def job_logs(self,jobid,json_lines,topic):
        for i in requests.get("{}/subjob_logs/{}?topic={}".format(self.config['server'],jobid,topic),
                              headers = headers(self.config), verify=False, stream=True
                              ).iter_lines():
            if not json_lines:
                yield json.loads(i)['msg']
            else:
                yield i

    def wflow_logs(self,wflowid,json_lines,topic):
        if topic == 'state': key = 'state'

        r = requests.get("{}/wflow_logs/{}?topic={}".format(self.config['server'],wflowid,topic), headers = headers(self.config), verify=False, stream=True)

        if topic == 'state':
            for i in r.iter_lines():
                pass
            state = json.loads(i)['state']
            for node in state['dag']['nodes']:
                click.secho('node: {} state: {}'.format(node['name'], node['state']))

        if topic == 'log':
            for i in r.iter_lines():
                if not json_lines:
                    click.secho(json.loads(i)['msg'])
                else:
                    click.secho(i)

    def login(self,server,auth_token):
        if server:
            self.config['server'] = server
        self.config['auth_token'] = auth_token
        json.dump(self.config,open(self.configfile,'w'))

    def upload(self,filepath):
        response = upload_file(filepath,self.config)
        return response
