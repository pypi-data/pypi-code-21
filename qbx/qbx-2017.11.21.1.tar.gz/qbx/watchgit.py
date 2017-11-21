import asyncio
from aiohttp import web
from aiohttp.web import run_app
from docopt import docopt as docoptinit
import os
import tempfile
import json
import logging

watch_git_doc = """
Usage:
    watch_git.py [options] <repo> <path>
    
Options:
    --debug

"""


def init_repo(directory, repo):
    os.makedirs(directory, exist_ok=True)
    os.system('cd {} && git clone {} watch'.format(directory, repo))


def watch_git(argv):
    docopt = docoptinit(watch_git_doc, argv)
    directory = tempfile.mkdtemp()
    print('watch', directory, docopt)
    init_repo(directory, docopt['<repo>'])
    path = '{}/watch/{}'.format(directory, docopt['<path>'])
    with open('{}/watch/{}'.format(directory, docopt['<path>'])) as f:
        buf = f.read()
    while True:
        import time
        time.sleep(10)
        os.system('cd {}/watch && git pull'.format(directory))
        with open(path) as f:
            new = f.read()
        if new != buf:
            logging.warning('changed')
            break


watch_git_http_doc = """
Usage:
    watch_git_http [options] <repo> <path>

Options:
    --port=<port>  Port [default: 3000]
    --debug        Debug or not

"""


def watch_git_http(argv):
    docopt = docoptinit(watch_git_http_doc, argv)
    logging.info('watch http git')
    logging.info(docopt)
    directory = tempfile.mkdtemp()
    print('watch', directory, docopt)
    os.system('cd {} && git clone {} watch'.format(directory, docopt['<repo>']))
    path = '{}/watch/{}'.format(directory, docopt['<path>'])
    with open('{}/watch/{}'.format(directory, docopt['<path>'])) as f:
        buf = f.read()

    def jsonify(dic, status=200):
        text = json.dumps(dic, sort_keys=True)
        return web.Response(body=text.encode('utf-8'), content_type='application/json', status=status)

    @asyncio.coroutine
    def check_repo(request):
        logging.info('checking')
        os.system('cd {}/watch && git pull'.format(directory))
        with open(path) as f:
            new = f.read()
        if new != buf:
            logging.warning('changed')
            return jsonify({'message': 'repo changed'}, 500)
        logging.info('not changed')
        return jsonify({'message': 'repo not change'})

    app = web.Application()
    app.router.add_route('GET', '/watchgit', check_repo)
    run_app(app, port=int(docopt['--port']))
