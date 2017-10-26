import unittest
from fs.tempfs import TempFS
from unittest.mock import Mock
from dxpy import slurm


class TestSlurm(unittest.TestCase):
    def test_sbatch(self):
        slurm.apply_command = Mock(return_value=['Submitted batch job 327'])
        slurm.sbatch('/tmp/test', 'run.sh')
        slurm.apply_command.assert_called_with("cd /tmp/test && sbatch run.sh")

    def test_squeue(self):
        slurm_msg = ["             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)             \n",
                     "                327      main  test.sh hongxwing  R       4:41      1 NB408A-WS1    "]
        slurm.apply_command = Mock(return_value=slurm_msg)
        tasks_gathered = []
        slurm.squeue().subscribe(lambda t: tasks_gathered.append(t))
        slurm.apply_command.assert_called_with('squeue')
        self.assertEqual(tasks_gathered[0].id, 327)
        self.assertEqual(tasks_gathered[0].part, 'main')
        self.assertEqual(tasks_gathered[0].cmd, 'test.sh')
        self.assertEqual(tasks_gathered[0].usr, 'hongxwing')
        self.assertEqual(tasks_gathered[0].stat, 'R')

    def test_is_complete(self):
        slurm_msg = ["             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)             \n",
                     "                327      main  test.sh hongxwing  R       4:41      1 NB408A-WS1    ",
                     "                329     main  test.sh hongxwing  R       4:41      1 NB408A-WS1    ",
                     "                400      main  test.sh hongxwing  R       4:41      1 NB408A-WS1    "]
        slurm.apply_command = Mock(return_value=slurm_msg)
        self.assertTrue(slurm.is_complete(300))
        self.assertFalse(slurm.is_complete(327))
        self.assertFalse(slurm.is_complete(329))
        self.assertFalse(slurm.is_complete(400))

    def test_sid_for_submit(self):
        msg = 'Submitted batch job 327'
        self.assertEqual(slurm.sid_from_submit(msg), 327)
