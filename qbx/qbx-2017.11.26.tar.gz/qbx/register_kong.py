import socket

import requests
from docopt import docopt as docoptinit

register_kong_doc = """
Usage:
    register_kong [options]
    
Options:
    --name=<name>
    --uris=<uris>
    --hosts=<hosts>
    --port=<port>
    --ip=<ip>
    --region=<region>
"""


def register_kong(argv):
    docopt = docoptinit(register_kong_doc, argv)
    print(docopt)
    name = docopt['--name']
    uris = docopt['--uris']
    port = docopt['--port']
    hosts = docopt['--hosts']
    region = docopt['--region']
    if region == 'alihz':
        url = 'http://alihz-master.qbtrade.org:8001/apis'
    else:
        url = 'http://kong-admin.qbtrade.org/apis'
    if not docopt['--ip']:
        ip = socket.gethostbyname(socket.gethostname())
    else:
        ip = docopt['--ip']
    r = requests.delete('{url}/{name}'.format(url=url, name=name))
    print('delete', r.text)
    data = {'name': name,
            'upstream_url': 'http://{}:{}'.format(ip, port),
            }

    if hosts:
        data['hosts'] = hosts
    if uris:
        data['uris'] = uris
        data['strip_uri'] = 'true'

    print(data)
    r = requests.post(url, data=data)
    print('add', r.text)
    print('register ip', ip)


if __name__ == '__main__':
    # register_kong(['--name', 'pytest', '--ip', '1.2.3.4', '--uris', '/pytest', '--port', '8080'])
    register_kong(['--name', 'pytest', '--ip', '1.2.3.4', '--hosts', 'pytest.qbtrade.org', '--port', '8080'])
