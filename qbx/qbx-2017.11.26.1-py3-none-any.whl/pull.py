"""
Usage:
    pull [options]

Options:
    --image=<img>

"""

import logging
import threading

import requests


def pull_single(host, image):
    print('pull image', host)
    try:
        x = requests.post('http://{}.qbtrade.org:5748/pull'.format(host),
                          data={'image': image},
                          timeout=(5, 600))
        print(x.text)
    except requests.exceptions.ConnectTimeout:
        print('timeout', host, 'server may not start')
    except:
        logging.exception('unexpected fail')
    print('pull image done', host)


# haproxy --port port --dest host:port
def pull(argv):
    from docopt import docopt as docoptinit

    docopt = docoptinit(__doc__, argv)
    print(docopt)
    for host in ['alihk-slave-1', 'alihk-slave-2', 'alihk-slave-3', 'alihk-slave-4']:
        threading.Thread(target=pull_single, args=(host, docopt['--image'])).start()


if __name__ == '__main__':
    pull(['--image', 'registry.cn-hangzhou.aliyuncs.com/qbtrade/backend-go'])
