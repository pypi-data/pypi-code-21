import datetime
import os

from docopt import docopt as docoptinit

haproxy_doc = """
Usage:
    haproxy.py [options]

Options:
    --port=<port>
    --dest=<dest>
    --daemon
    --timeout_server=<t>         Timeout For Server [default: 86400000]
    --timeout_client=<t>         Timeout For Server [default: 86400000]

"""


# haproxy --port port --dest host:port
def haproxy(argv, toy=False):
    docopt = docoptinit(haproxy_doc, argv)
    print(docopt)
    port = int(docopt['--port'])
    opt = {'dest': docopt['--dest'],
           'timeout_server': docopt['--timeout_server'],
           'timeout_client': docopt['--timeout_client']}
    cfg = """
    global
        debug
        log 127.0.0.1 local0
        maxconn 20480

    defaults
        mode tcp
        log     global
        option tcplog
        option tcp-check
        timeout connect 5000
        timeout client  {timeout_client} # 1day 86400 * 1000 ms
        timeout server  {timeout_server}


    frontend shadow1
        bind :9998
        option tcplog
        default_backend haproxy-nodes

    backend haproxy-nodes
        server node-1 {dest} check

    """.format(**opt)
    print(cfg)
    home = os.path.expanduser('~')
    if not os.path.exists('{}/.qbx'.format(home)):
        print('make directory ~/.qbx')
        os.system('mkdir ~/.qbx')
    filename = '{}/.qbx/haproxy-{}.cfg'.format(home, str(int(datetime.datetime.now().timestamp() * 10e6)))
    fp = open(filename, 'w')
    fp.write(cfg)
    fp.close()

    if docopt['--daemon']:
        addon = '--restart always -d --name haproxy-{}'.format(port)
    else:
        addon = '-it --rm'
    cmd = 'sudo docker run {} -v {}:/usr/local/etc/haproxy/haproxy.cfg -p {}:9998 haproxy'
    cmd = cmd.format(addon, filename, port)
    if toy:
        print(cmd)
    else:
        os.system(cmd)


if __name__ == '__main__':
    haproxy(['--port', '123', '--daemon'], toy=True)
