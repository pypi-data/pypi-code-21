import unittest
from tios import gromacs_utilities
import tempfile
import os
import zlib
import mdtraj as mdt

class TestGromacsUtilitiesMethods(unittest.TestCase):

    def test_complete_inputs_nothing_needed(self):
        inputs = {'-s': 'test.tpr'}
        new_inputs = gromacs_utilities.complete_inputs(inputs)
        self.assertDictEqual(inputs, new_inputs)

    def test_complete_inputs_with_deffnm(self):
        inputs = {'-deffnm': 'test'}
        expected_inputs = { '-s'      : 'test.tpr',
                            '-o'      : 'test.trr',
                            '-x'      : 'test.xtc',
                            '-cpo'    : 'test.cpt',
                            '-e'      : 'test.edr',
                            '-g'      : 'test.log'}
        new_inputs = gromacs_utilities.complete_inputs(inputs)
        self.assertDictEqual(expected_inputs, new_inputs)

    def test_complete_inputs_for_imd(self):
        inputs = {'-deffnm': 'test'}
        expected_inputs = { '-deffnm' : 'test',
                            '-imdwait': None,
                            '-imdterm': None,
                            '-imdport': '0'}
        new_inputs = gromacs_utilities.complete_inputs_for_imd(inputs)
        self.assertDictEqual(expected_inputs, new_inputs)

    def test_apply_checkpoint(self):
        testdir = tempfile.mkdtemp()
        checkpoint = zlib.compress(b'Dummy checkpoint data')
        inputs = {'-deffnm': '{}/test'.format(testdir)}
        expected_inputs = {'-deffnm' : '{}/test'.format(testdir),
                           '-cpi' : '{}/test.cpt'.format(testdir),
                           '-noappend' : None}
        new_inputs = gromacs_utilities.apply_checkpoint(inputs, checkpoint)
        self.assertEqual(new_inputs, expected_inputs)
        self.assertTrue(os.path.exists('{}/test.cpt'.format(testdir)))
        
    def test_tpr_file_valid_for_imd(self):
        tprfile = 'test/examples/bpti.tpr'
        self.assertTrue(gromacs_utilities.tpr_file_valid_for_imd(tprfile))

    def test_tpr_file_does_not_set_imd(self):
        tprfile = 'test/examples/bpti_no_imd.tpr'
        self.assertFalse(gromacs_utilities.tpr_file_valid_for_imd(tprfile))

    def test_tpr_file_is_NPT(self):
        tprfile = 'test/examples/bpti_NPT.tpr'
        self.assertFalse(gromacs_utilities.tpr_file_valid_for_imd(tprfile))

    def test_dt_from_tpr_file(self):
        tprfile = 'test/examples/bpti.tpr'
        dt = gromacs_utilities.dt_from_tpr_file(tprfile)
        self.assertEqual(dt, 0.002)

    def test_trajectory_from_tpr_file(self):
        tprfile = 'test/examples/bpti.tpr'
        traj = gromacs_utilities.trajectory_from_tpr_file(tprfile)
        self.assertIsInstance(traj, mdt.Trajectory)
        self.assertEqual(traj.topology.n_atoms, 20521)

    def test_step_from_checkpoint_file(self):
        cptfile = 'test/examples/bpti.cpt'
        step = gromacs_utilities.step_from_checkpoint_file(cptfile)
        self.assertEqual(step, 520)
