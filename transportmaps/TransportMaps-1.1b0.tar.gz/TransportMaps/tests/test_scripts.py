#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2017 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Author: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import unittest

try:
    import mpi_map
    MPI_SUPPORT = True
except:
    MPI_SUPPORT = False

class Scripts_unittest(unittest.TestCase):
    def setUp(self):
        import dill
        import numpy as np
        import numpy.random as npr
        import TransportMaps.Distributions as DIST
        # Parameters
        self.dim = 5
        self.dist_fname = 'Distribution.dill'
        self.fname_list = [self.dist_fname]
        # Build and store target distribution
        tar_mu = npr.randn(self.dim)
        tar_sig = npr.randn(self.dim**2).reshape((self.dim, self.dim))
        tar_sig2 = np.dot(tar_sig, tar_sig.T)
        target = DIST.GaussianDistribution(tar_mu, sigma=tar_sig2)
        with open(self.dist_fname, 'wb') as out_stream:
            dill.dump(target, out_stream)

    def tearDown(self):
        import os
        for fname in self.fname_list:
            if os.path.exists(fname):
                os.remove(fname)

    def postprocess(self):
        from distutils.spawn import find_executable
        from subprocess import call
        # Parameters
        self.post_fname = 'Postprocess.dill'
        self.fname_list.append( self.post_fname )
        self.fname_list.append( self.post_fname + '.bak' )
        self.fname_list.append( self.post_fname + '.hdf5' )
        # Find path to script (to avoid long paths with sh..)
        script_path = find_executable("tmap-postprocess")
        # Run post-process script with different options
        # Target aligned conditionals
        outsig = call(["python", script_path, "--input=" + self.tm_fname,
                       "--aligned-conditionals=exact-target",
                       "--no-plotting",
                       "--output=" + self.post_fname])
        self.assertFalse( outsig )
        # Random aligned conditionals
        outsig = call(["python", script_path, "--input=" + self.tm_fname,
                       "--random-conditionals=approx-base", "--no-plotting",
                       "--rndc-n-points-x-ax=20", "--rndc-n-plots-x-ax=3",
                       "--output=" + self.post_fname])
        self.assertFalse( outsig )
        # Pullback aligned conditionals
        outsig = call(["python", script_path, "--input=" + self.tm_fname,
                       "--aligned-conditionals=approx-base", "--no-plotting",
                       "--alc-n-points-x-ax=20",
                       "--output=" + self.post_fname])
        self.assertFalse( outsig )
        # Variance diagnostic (MC)
        outsig = call(["python", script_path, "--input=" + self.tm_fname,
                       "--var-diag=exact-base",
                       "--var-diag-qtype=0", "--var-diag-qnum=100",
                       "--output=" + self.post_fname])
        self.assertFalse( outsig )
        # Variance diagnostic (MC increased)
        outsig = call(["python", script_path, "--input=" + self.tm_fname,
                       "--var-diag=exact-base",
                       "--var-diag-qtype=0", "--var-diag-qnum=1000",
                       "--output=" + self.post_fname])
        self.assertFalse( outsig )
        # Variance diagnostic (Quadrature)
        outsig = call(["python", script_path, "--input=" + self.tm_fname,
                       "--var-diag=exact-base",
                       "--var-diag-qtype=3",
                       "--var-diag-qnum=%s" % ','.join(['3']*self.dim),
                       "--output=" + self.post_fname])
        self.assertFalse( outsig )

    def test_laplace(self):
        from distutils.spawn import find_executable
        from subprocess import call
        # Parameters
        tol = 1e-3
        ders = 2
        self.tm_fname = 'Laplace.dill'
        self.fname_list.append( self.tm_fname )
        # Find path to script (to avoid long paths with sh..)
        script_path = find_executable("tmap-laplace")
        # Run laplace script
        outsig = call(["python", script_path, "--dist=" + self.dist_fname,
                       "--output=" + self.tm_fname])
        self.assertFalse( outsig )
        # Test post-process
        self.postprocess()

    def test_direct(self):
        from distutils.spawn import find_executable
        from subprocess import call
        # Parameters
        tol = 1e-3
        ders = 2
        self.tm_fname = 'Direct.dill'
        self.fname_list.append( self.tm_fname )
        # Find path to script (to avoid long paths with sh..)
        script_path = find_executable("tmap-tm")
        # Run direct script
        outsig = call(["python", script_path, "--dist=" + self.dist_fname,
                       "--output=" + self.tm_fname,
                       "--mtype=intexp", "--span=total", "--btype=poly", "--order=1",
                       "--qtype=0", "--qnum=1000"])
        self.assertFalse( outsig )
        # Test post-process
        self.postprocess()

    def test_direct_xml(self):
        from distutils.spawn import find_executable
        import os.path
        from subprocess import call
        # Parameters
        tol = 1e-3
        ders = 2
        self.tm_fname = 'Direct.dill'
        self.fname_list.append( self.tm_fname )
        # Find path to script (to avoid long paths with sh..)
        script_path = find_executable("tmap-tm")
        # Run direct script
        test_map_xml_dir = os.path.dirname(os.path.realpath(__file__)) + \
                           '/xml/maps/'
        xml_map_fname = 'TotalOrdIntExpLinearMap_5d.xml'
        outsig = call(["python", script_path, "--dist=" + self.dist_fname,
                       "--output=" + self.tm_fname,
                       "--map-descr=" + test_map_xml_dir + xml_map_fname,
                       "--qtype=0", "--qnum=1000"])
        self.assertFalse( outsig )
        # Test post-process
        self.postprocess()

def build_suite(ttype='all'):
    suites_list = []
    if ttype in ['all','serial']:
        scripts_suite = unittest.TestLoader().loadTestsFromTestCase( Scripts_unittest )
        suites_list.append( scripts_suite )
    all_suites = unittest.TestSuite(suites_list)
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()
