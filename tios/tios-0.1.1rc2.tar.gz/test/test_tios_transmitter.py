import unittest
from tios import transmitter, communication
import shutil
import tempfile
import mdtraj as mdt

class TestTiosTransmitterMethods(unittest.TestCase):

    def setUp(self):
        #self.protocol = 'Dummy'
        self.protocol = 'Mongo'
        self.testdir = tempfile.mkdtemp()
        #self.testdir = 'scratchdir'
        shutil.copy('test/examples/bpti.tpr', self.testdir)
        shutil.copy('test/examples/bpti.cpt', self.testdir)

    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_initialize_new_tios_transmitter_from_command(self):
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol = self.protocol)
        self.assertIsInstance(tj, transmitter.TiosTransmitter)

    def test_initialize_new_tios_transmitter_from_database(self):
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        id = tj.id

        tj2 = transmitter.from_entry(id, protocol=self.protocol, targetdir=self.testdir)
        self.assertIsInstance(tj2, transmitter.TiosTransmitter)

    def test_tios_job_from_command_datastore_integrity(self):
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        self.assertEqual(tj._te.title, 'test')
        self.assertEqual(tj._te.timepoint, 0.0)
        self.assertEqual(tj._te.md_code, 'GROMACS')
        self.assertEqual(tj._te.status, 'Ready')
        self.assertEqual(tj._te.trate, 1.0)
        self.assertEqual(tj._te.frame_rate, 0.0)
        self.assertIsInstance(tj._te.topology, mdt.Topology)
        self.assertEqual(len(tj._te.selection), 58)
        self.assertEqual(len(tj._te.xyzsel), 58)
        self.assertEqual(len(tj._te.xyzsel[0]), 3)

    def test_tios_job_from_command_datastore_integrity2(self):
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        id = tj.id

        tj2 = transmitter.from_entry(id, protocol=self.protocol, targetdir=self.testdir)

        self.assertEqual(tj2._te.title, 'test')
        self.assertEqual(tj2._te.timepoint, 0.0)
        self.assertEqual(tj2._te.md_code, 'GROMACS')
        self.assertEqual(tj2._te.status, 'Ready')
        self.assertEqual(tj2._te.trate, 1.0)
        self.assertEqual(tj2._te.frame_rate, 0.0)
        self.assertIsInstance(tj2._te.topology, mdt.Topology)
        self.assertEqual(len(tj2._te.selection), 58)
        self.assertEqual(tj2._te.xyzsel.shape, (58, 3))

    def test_tios_transmitter_start_step_and_stop(self):
    
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        tj.start()
        self.assertEqual(tj._te.status, 'Running')
        self.assertFalse(tj._imd_sim.new_checkpoint)
        tj.step()
        self.assertEqual(tj._te.timepoint, 0.002)
        tj.step()
        self.assertEqual(tj._te.timepoint, 1.002)
        tj.stop()
        self.assertEqual(tj._te.status, 'Stopped')
        
    def test_tios_transmitter_restart_step_and_stop(self):
    
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti -cpi {}/bpti.cpt -noappend'.format(self.testdir, self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        self.assertEqual(tj._te.status, 'Ready')
        self.assertEqual(tj._te.timepoint, 1.04)
        self.assertTrue('-cpi' in tj._te.filepack)
        tj.start()
        self.assertEqual(tj._te.status, 'Running')
        tj.step()
        #self.assertEqual(tj._te.timepoint, 1.202)
        tj.step()
        self.assertAlmostEqual(tj._te.timepoint, 2.002)
        tj.stop()
        self.assertEqual(tj._te.status, 'Stopped')

    def test_tios_transmitter_start_stop_and_restart(self):
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        tj.start()
        tj.step()
        tj.step()
        tj.stop()
        self.assertAlmostEqual(tj._te.timepoint, 1.002)
        id = tj.id

        tj2 = transmitter.from_entry(id, protocol=self.protocol, targetdir=self.testdir)
        #self.assertAlmostEqual(tj2._te.timepoint, 1.012)
        tj2.start()
        self.assertEqual(tj2._te.status, 'Running')
        tj2.stop()
        self.assertEqual(tj2._te.status, 'Stopped')

    def test_tios_transmitter_stop_by_message(self):
        tj = transmitter.from_command('gmx mdrun -deffnm {}/bpti'.format(self.testdir), 
                                   title='test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        tj.start()
        tj.step()
        tj.step()
        self.assertEqual(tj._te.status, 'Running')
        tj._te.message = {'header' : 'STOP'}
        tj._te.sync()
        tj.step()
        self.assertEqual(tj._te.status, 'Stopped')

