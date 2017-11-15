""" Task APIs
"""

from ..model.task import Task
from ..interface import read, read_all


class SlurmCreator:
    @classmethod
    def create(cls, workdir, filename):
        from ..interface import create
        from ..model.creators import task_slurm
        return create(task_slurm(workdir, filename))

    @classmethod
    def create_group(cls, workdirs, filenames, depens):
        from ..interface import create, create_graph
        from ..model.creators import task_graph
        tasks = [create(w, f, no_create=True)
                 for w, f in zip(workdirs, filenames)]
        g = create_graph(tasks, depens)
        return create_graph(g)


def submit(tid):
    from ..interface import mark_submit
    mark_submit(read(tid))


def delete(tid):
    from ..interface import delete
    delete(tid)
