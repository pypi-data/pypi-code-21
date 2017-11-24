#!/usr/bin/env python
import os
import sys
import time
import signal
import logging 
import logging.handlers 
import inspect 
import subprocess

SGE_ROOT = '/usr/share/gridengine'
SGE_USER = 'sgeadmin'
SGE_EXECD = '/usr/bin/sge_execd'
SGE_MASTER = '/usr/bin/sge_qmaster'
SGE_CELL_NAME = 'default'

def daemonize():
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError, e:
        print str(e)
        sys.exit(1)

    os.setsid()
    os.umask(0)
    signal.signal(signal.SIGCLD, signal.SIG_IGN)

def get_logger(file_name):
    fmt = "[%(asctime)s]\t[%(levelname)s]\t[%(thread)d]\t[%(pathname)s:%(lineno)d]\t%(message)s"
    #200M * 50
    formatter = logging.Formatter(fmt)
    handler = logging.handlers.RotatingFileHandler(file_name, maxBytes = 1024*1024*200, backupCount = 10)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def run_cmd_for_stdout(cmd):
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
    p.wait()
    if p.returncode != 0:
        msg = 'Failed to run cmd ' + cmd + ' returncode: ' + str(p.returncode) + '. ' + str(p.stdout.read())
        raise Exception(msg)
    return p.stdout.read()

def run_cmd(cmd, raise_exception = True):
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
    p.wait()
    if p.returncode != 0 and raise_exception:
        msg = 'Failed to run cmd ' + cmd + ' returncode: ' + str(p.returncode) + '. ' + str(p.stdout.read())
        raise Exception(msg)
    return p.returncode

def set_etc_hosts(ip_address, host_name, logger = None):
    hosts = '/etc/hosts'
    with open(hosts, 'r') as f:
        for line in f:
            if line.find(ip_address) >= 0 and line.find(host_name) >= 0:
                if logger:
                    msg = 'find %s %s in %s' % (ip_address, host_name, hosts)
                    logger.info(msg)
                return
    with open(hosts, 'a+') as f:
        f.write('\n%s %s\n' % (ip_address, host_name))

def set_act_qmaster(sge_root, cell_name, master_host_name):
    act_file = os.path.join(sge_root, cell_name, 'common/act_qmaster')
    with open(act_file, 'w') as f:
        f.write('%s' % master_host_name)

def get_process_pid(user, process):
    def parse_proecess_line(line):
        ret = line.startswith(user)
        ret = ret and line.find(process) != -1 and line.find('grep') == -1
        if ret:
            return int(line.split()[1])
        return 0

    cmd = 'ps aux|grep ' + process 
    stdout = run_cmd_for_stdout(cmd)
    for line in stdout.split('\n'):
        pid = parse_proecess_line(line)
        if pid:
            return pid
    return 0

def kill_process(user, process, retry_count = 0, logger = None):
    def _kill_process(pid):
        cmd = 'kill -9 %d' % pid
        run_cmd(cmd)

    for i in range(retry_count + 1):
        try:
            pid = get_process_pid(user, process)
            if pid:
                _kill_process(pid)
                if logger:
                    logger.warning('kill process: %s, user: %s, pid: %d' % (process, user, pid))
            return 
        except Exception, e:
            if logger:
                logger.exception(str(e))
            if i == retry_count:
                raise e
            time.sleep(1) #if raise some exception ???

def start_sge_master():
    cmd = '/sbin/service sgemaster start'
    msg = run_cmd_for_stdout(cmd) #XXX
    if 'error' in msg or "sge_qmaster didn't start" in msg:
        raise Exception('Failed to run: %s, msg: %s' % (cmd, msg))

def start_sge_execd():
    cmd = '/sbin/service sge_execd start'
    msg = run_cmd_for_stdout(cmd)
    if 'error' in msg:
        raise Exception('Failed to run: %s, msg: %s' % (cmd, msg))

def get_running_script_dir():
    caller_file = inspect.stack()[1][1]
    return os.path.abspath(os.path.dirname(caller_file))

