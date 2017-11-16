from dxpy.file_system.path import Path
from dxpy.task.representation import creators, task
from dxpy.task import interface

def quick_command(command):
    from fs.tempfs import TempFS
    with TempFS(auto_clean=False) as t:
        t = creators.task_command(command, workdir=t.getsyspath('.'))
        interface.create(t)

