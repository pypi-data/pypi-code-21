import unittest
from dxpy.task.model import creators, task


class TestCreators(unittest.TestCase):
    def test_create_command(self):
        t = creators.task_command(command='ls')
        self.assertEqual(t.data['command'], 'ls')
        self.assertEqual(t.type, task.Type.Command)

    def test_create_script(self):
        t = creators.task_script(file='run.sh', workdir='/tmp/test')
        self.assertEqual(t.data['file'], '/tmp/test/run.sh')
        self.assertEqual(t.type, task.Type.Script)

    def test_create_slurm(self):
        t = creators.task_slurm(file='run.sh', workdir='/tmp/test')
        self.assertEqual(t.data['file'], '/tmp/test/run.sh')
        self.assertEqual(t.type, task.Type.Script)
        self.assertEqual(t.worker, task.Worker.Slurm)
