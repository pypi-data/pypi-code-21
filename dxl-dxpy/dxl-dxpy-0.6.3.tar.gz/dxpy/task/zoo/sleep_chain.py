from dxpy.file_system.path import Path
from dxpy.task.representation import creators


class SleepChainCreator:
    def __init__(self, workdir=None, duration=5):
        self.workdir = Path(workdir)
        self.duration = duration

    def create(self):
        cmd = 'sleep {0} && hostname'.format(self.duration)
        t1 = creators.task_command(
            cmd, workdir=self.workdir, desc='sleep chain #0')
        t2 = creators.task_command(
            cmd, workdir=self.workdir, desc='sleep chain #1')
        t3 = creators.task_command(
            cmd, workdir=self.workdir, desc='sleep chain #2')
        g = creators.task_graph([t1, t2, t3], [None, 0, 1])
        return g


class SbatchCreator:
    def __init__(self, workdir=None, ):
        pass
