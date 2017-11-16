import unittest
from tios import transmitter, communication
import shutil
import tempfile
import mdtraj as mdt

from contextlib import contextmanager
import os

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

class TestTiosNAMDTransmitterMethods(unittest.TestCase):

    def setUp(self):
        #self.protocol = 'Dummy'
        self.protocol = 'Mongo'
        self.testdir = tempfile.mkdtemp()
        #self.testdir = 'scratchdir'
        shutil.copy('test/examples/ubq_wb.conf', self.testdir)
        shutil.copy('test/examples/ubq_wb.psf', self.testdir)
        shutil.copy('test/examples/ubq_wb.pdb', self.testdir)
        shutil.copy('test/examples/ubq_wb_eq.coor', self.testdir)
        shutil.copy('test/examples/ubq_wb_eq.xsc', self.testdir)
        shutil.copy('test/examples/par_all27_prot_lipid.inp', self.testdir)

    def tearDown(self):
        shutil.rmtree(self.testdir)

    def test_initialize_new_tios_namd_transmitter_from_command(self):
        with cd(self.testdir):
            tj = transmitter.from_command('namd2 +p4 ubq_wb.conf', 
                                          title='NAMD test',
                                          selection='name CA', 
                                          protocol = self.protocol)
            self.assertIsInstance(tj, transmitter.TiosTransmitter)

    def test_initialize_new_tios_namd_transmitter_from_database(self):
        tj = transmitter.from_command('namd2 +p4 test/examples/ubq_wb.conf', 
                                      title='NAMD test',
                                      selection='name CA', 
                                      protocol=self.protocol)
        id = tj.id

        with cd(self.testdir):
            tj2 = transmitter.from_entry(id, protocol=self.protocol)
            self.assertIsInstance(tj2, transmitter.TiosTransmitter)

    def test_tios_namd_job_from_command_datastore_integrity(self):
        tj = transmitter.from_command('namd2 +p4 test/examples/ubq_wb.conf', 
                                      title='NAMD test',
                                      selection='name CA', 
                                      protocol=self.protocol)
        self.assertEqual(tj._te.title, 'NAMD test')
        self.assertEqual(tj._te.timepoint, 0.0)
        self.assertEqual(tj._te.md_code, 'NAMD')
        self.assertEqual(tj._te.status, 'Ready')
        self.assertEqual(tj._te.trate, 1.0)
        self.assertEqual(tj._te.frame_rate, 0.0)
        self.assertIsInstance(tj._te.topology, mdt.Topology)
        self.assertEqual(len(tj._te.selection), 76)
        self.assertEqual(tj._te.xyzsel.shape, (76, 3))

    def test_tios_namd_job_from_command_datastore_integrity2(self):
        tj = transmitter.from_command('namd2 +p4 test/examples/ubq_wb.conf', 
                                   title='NAMD test',
                                   selection='name CA', 
                                   protocol=self.protocol)
        id = tj.id

        with cd(self.testdir):
            tj2 = transmitter.from_entry(id, protocol=self.protocol)

            self.assertEqual(tj2._te.title, 'NAMD test')
            self.assertEqual(tj2._te.timepoint, 0.0)
            self.assertEqual(tj2._te.md_code, 'NAMD')
            self.assertEqual(tj2._te.status, 'Ready')
            self.assertEqual(tj2._te.trate, 1.0)
            self.assertEqual(tj2._te.frame_rate, 0.0)
            self.assertIsInstance(tj2._te.topology, mdt.Topology)
            self.assertEqual(len(tj2._te.selection), 76)
            self.assertEqual(tj2._te.xyzsel.shape, (76, 3))

    def test_tios_namd_transmitter_start_step_and_stop(self):
        with cd(self.testdir):
            tj = transmitter.from_command('namd2 +p4 ubq_wb.conf', 
                                          title='NAMD test',
                                          selection='name CA', 
                                          protocol=self.protocol)
            tj.start()
            self.assertEqual(tj._te.status, 'Running')
            self.assertFalse(tj._imd_sim.new_checkpoint)
            tj.step()
            self.assertEqual(tj._te.timepoint, 1.00)
            tj.step()
            self.assertEqual(tj._te.timepoint, 2.00)
            tj.stop()
            self.assertEqual(tj._te.status, 'Stopped')
        
    def test_tios_namd_transmitter_start_stop_and_restart(self):
        with cd(self.testdir):
            tj = transmitter.from_command('namd2 +p4 ubq_wb.conf', 
                                          title='NAMD test',
                                          selection='name CA', 
                                          protocol=self.protocol)
            tj.start()
            tj.step()
            tj.step()
            tj.stop()
            self.assertAlmostEqual(tj._te.timepoint, 2.000)
            id = tj.id

        with cd('scratchdir'):
            tj2 = transmitter.from_entry(id, protocol=self.protocol)
            tj2.start()
            self.assertEqual(tj2._te.status, 'Running')
            tj2.step()
            tj2.stop()
            self.assertEqual(tj2._te.status, 'Stopped')

    def test_tios_namd_transmitter_stop_by_message(self):
        with cd(self.testdir):
            tj = transmitter.from_command('namd2 +p4 ubq_wb.conf', 
                                          title='NAMD test',
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

