import rx
from rx import Observable
from collections import namedtuple
import re
import os

SINFO = namedtuple('SINFO', ('id', 'part', 'cmd', 'usr',
                             'stat', 'time', 'nodes', 'node_name'))


class TaskInfo:
    def __init__(self, tid, part, cmd, usr, stat, time, nodes, node_name, *args):
        self.id = int(tid)
        self.part = part
        self.cmd = cmd
        self.usr = usr
        self.stat = stat
        self.time = time
        self.nodes = nodes
        self.node_name = node_name

    @classmethod
    def from_squeue(cls, l):
        s = re.sub('\s+', ' ', l).strip()
        items = s.split()
        if not items[0].isdigit():
            return None
        else:
            return cls(*items)


def _apply_command(command):
    with os.popen(command) as fin:
        return fin.readlines()


def sbatch(workdir, script_file, *args):
    cmd = 'cd {dir} && sbatch {args} {file}'.format(dir=workdir,
                                                    args=' '.join(args),
                                                    file=script_file)
    result = _apply_command(cmd)
    return sid_from_submit(result[0])


def sid_from_submit(s):
    return int(re.sub('\s+', ' ', s).strip().split(' ')[3])


def squeue():
    return (Observable.from_(_apply_command('squeue'))
            .map(lambda l: TaskInfo.from_squeue(l))
            .filter(lambda l: l is not None))


def is_complete(sid):
    if sid is None:
        return False
    result = []    
    squeue().filter(lambda tinfo: tinfo.id == sid).count().subscribe(result.append)
    import sys
    print(result, file=sys.stderr)
    return result[0] == 0
    # return (squeue()
    #         .subscribe_on(rx.concurrency.ThreadPoolScheduler())
    #         .filter(lambda tinfo: tinfo.id == sid)
    #         .count()
    #         .to_blocking().first()) == 0
