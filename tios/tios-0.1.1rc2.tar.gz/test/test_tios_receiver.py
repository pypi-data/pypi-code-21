import unittest
from tios import receiver, transmitter
import shutil
import tempfile
import mdtraj as mdt

class TestTiosReceiverMethods(unittest.TestCase):

    def setUp(self):
        self.protocol = 'Mongo'
        self.testdir = tempfile.mkdtemp()
        shutil.copy('test/examples/bpti.tpr', self.testdir)
        shutil.copy('test/examples/bpti.cpt', self.testdir)

    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_initialize_new_tios_receiver_from_database(self):
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        id = tj.id

        tj2 = receiver.TiosReceiver(id, protocol=self.protocol)
        self.assertIsInstance(tj2, receiver.TiosReceiver)
        self.assertEqual(tj2.status, 'Ready')
        self.assertIsInstance(tj2.trajectory, mdt.Trajectory)
        self.assertEqual(tj2.trajectory.n_atoms, 20521)

        tj3 = receiver.TiosReceiver(id, protocol=self.protocol, selection='protein')
        self.assertEqual(tj3.trajectory.n_atoms, 892)

    def test_tios_receiver_collection(self):
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        id = tj.id

        tj2 = receiver.TiosReceiver(id, protocol=self.protocol)
        self.assertEqual(tj2.status, 'Ready')
        tj.start()
        self.assertEqual(tj.status, 'Running')
        self.assertEqual(len(tj2.trajectory), 1)
        tj.step()
        self.assertEqual(tj.status, 'Running')
        tj2.step()
        self.assertEqual(tj2.status, 'Running')
        self.assertEqual(len(tj2.trajectory), 2)
        tj.step()
        tj2.step()
        self.assertEqual(len(tj2.trajectory), 3)
        tj.stop()
        self.assertEqual(tj2.status, 'Stopped')
        self.assertEqual(tj.status, 'Stopped')
      
