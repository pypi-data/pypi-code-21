#!/usr/bin/env python
#coding: utf-8

#import pdb
import argparse
import yaml
import logging
import logging.config
import os
import time
import signal

from .core.master import StsMaster
from .core.slaver import StsSlaver
from .utils.daemonize import daemonize
from .banner import banner

print(os.path.dirname(os.path.realpath(__file__))+'/conf/logging.conf')
logging.config.fileConfig(os.path.dirname(os.path.realpath(__file__))+'/conf/logging.conf')

def signal_process():

    def signal_handler(signum, frame):
        print('********signal %d' % signum)
        #logger.debug("recv signal %d" % signum)

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(1)


def main():
    logger = logging.getLogger('sts_master')
    print(banner)
    signal_process()
    #time.sleep(5)
    prefix = os.path.dirname(os.path.realpath(__file__))
    default_conf = prefix +'/conf/sts.yaml'
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', dest='mode', help='mode of dts', choices=['master', 'slaver'], required=True)
    parser.add_argument('--daemon', dest='is_daemon', help='whether run as a daemon or not?', default=False, action='store_true')
    parser.add_argument('--sip', dest='serverip', help='connect to server... ip')
    parser.add_argument('--sport', dest='serverport', help='connect to server... port')
    parser.add_argument('--conf', dest='conf', help='configure file of dts', type=argparse.FileType('r'), default=open(default_conf))
    args = parser.parse_args()
    print("start STP server as %s..." % args.mode) 

    config = yaml.load(args.conf)
    stat_refresh_interval = config['stat_refresh_interval']
    sip = args.serverip 
    sport = args.serverport
    auth = config['auth'].encode('utf-8')
    mcgrp = config['multicast_group']
    mcport = config['multicast_port']
    mttl = config['multicast_ttl']
    ip = config[args.mode]['listen_ip']
    port = config[args.mode]['listen_port']
    task_lip = config['master']['task_listen_ip']
    task_lport = config['master']['task_listen_port']
    api_ip = config['master']['api_ip']
    api_port = config['master']['api_port']

    os.makedirs(os.path.dirname(config['stdout'])) if not os.path.exists(os.path.dirname(config['stdout'])) else None
    os.makedirs(os.path.dirname(config['pidfile'])) if not os.path.exists(os.path.dirname(config['pidfile'])) else None
    os.mknod(config['stdout']) if not os.path.exists(config['stdout']) else None
    os.mknod(config['stderr']) if not os.path.exists(config['stderr']) else None
    if args.is_daemon:
        daemonize('/dev/null', config['stdout'], config['stderr'])   
    #daemonize('/dev/null', '/dev/null', '/dev/null')   
    #daemonize('/dev/null', './stdout.log', './stderr.log')   
    #os.mknod(config['pidfile']) if not os.path.exists(config['pidfile']) else None
    with open(config['pidfile'], 'w+') as pidfile:
        logger.debug(os.getpid())
        pidfile.write(str(os.getpid()))

    #pdb.set_trace()
    runner = StsMaster(stat_refresh_interval, task_lip, task_lport, auth, ip, port, mcgrp, mcport, mttl, api_ip, api_port) if args.mode == 'master' else StsSlaver(ip, port, sip, sport, auth, mcgrp, mcport, mttl)

    runner.start()

if __name__ == '__main__':
    main()

