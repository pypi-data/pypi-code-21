from collections import namedtuple
import copy
import rx
import dask
import sys
import os
import dxpy.slurm as slurm
from ..model import task as taskpy
from ..model import creators
from .. import interface

NB_THREADS = 5
THREAD_POOL = rx.concurrency.ThreadPoolScheduler(NB_THREADS)


class Workers:
    @classmethod
    def is_complete(cls, task, *args):
        return task.state == taskpy.State.Complete

    @classmethod
    def on_this_worker(cls, task):
        return task.worker == cls.WorkerType

    @classmethod
    def plan(cls, task):
        raise NotImplementedError

    @classmethod
    def run(cls, task, stdout=None, stderr=None):
        print('RUN CALLED with task')
        print(task)
        if stdout is None:
            stdout = sys.stdout
        if stderr is None:
            stderr = sys.stderr
        (rx.Observable.from_([task])
         .subscribe_on(THREAD_POOL)
         .map(cls.plan)
         .subscribe(on_next=lambda r: print(r, file=stdout),
                    on_error=lambda e: print(e, file=stderr)))


class NoAction(Workers):
    WorkerType = taskpy.Worker.NoAction

    @classmethod
    def plan(cls, t, *args):
        print("NO ACTION PLAN CALLED")
        t = interface.mark_start(t)
        t = interface.mark_complete(t)
        return 'NoAction of task id: {} done.'.format(t.id)


def sbatch_command(workdir, file):
    cmd = 'cd {0}'.format(workdir)
    if file is not None:
        cmd += ' && sbatch {0}'.format(file)
    return cmd


def normal_command(workdir, command):
    return 'cd {0} && {1}'.format(workdir, command)


class Slurm(Workers):
    WorkerType = taskpy.Worker.Slurm

    @classmethod
    def is_complete(cls, task, *args):
        return slurm.is_complete(task.data.get('sid'))

    @classmethod
    def plan(cls, task, *args):
        # why?
        # TODO: FIX
        # print(args)
        # raise ValueError('task {0}, args: {1}'.format(task, args))
        # def srun_command(workdir, command):
        #     return 'cd {0} && srun {1}'.format(workdir, command)

        task = interface.mark_start(task)

        # if isinstance(task, templates.TaskCommand):
        #     command = task.command(srun_command)
        if not task.type == taskpy.Type.Script:
            raise TypeError(
                'Slurm worker only support TaskScript tasks, got: {!r}.'.format(task))
        command = sbatch_command(task.workdir, task.data.get('file'))
        with os.popen(command) as fin:
            result = fin.readlines()[0]
        sid = slurm.sid_from_submit(result)
        task.data.update({'sid': sid})
        interface.update(task)
        return result


class MultiThreding(Workers):
    WorkerType = taskpy.Worker.MultiThreading

    @classmethod
    def plan(cls, task):
        # TRT = namedtuple('TaskResultTuple', ('task', 'res'))
        task = interface.mark_start(task)
        if task.type == taskpy.Type.Command:
            with os.popen(normal_command(task.workdir, task.data['command'])) as fin:
                result = fin.readlines()
        task = interface.mark_complete(task)
        return result


WORKERS = [NoAction, MultiThreding, Slurm]


def get_workers(task):
    for w in WORKERS:
        if w.on_this_worker(task):
            return w

# class Dask(Workers):
#     WorkerType = taskpy.Worker.Dask
#     NB_PROCESSES = 5

#     @classmethod
#     def run_plan(cls, task):
#         (rx.Observable.just(task.workers.num_workers)
#          .map(lambda i: dask.delayed(task.run)(i_worker=i))
#          .to_list()
#          .map(lambda l: dask.bag.from_delayed(l))
#          .map(lambda b: b.compute(num_workers=NB_PROCESSES)))
