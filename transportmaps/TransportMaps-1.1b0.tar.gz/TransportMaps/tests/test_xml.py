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

class XML_Map_unittest(unittest.TestCase):
    def setUp(self):
        self.reg = {'type': 'L2',
                    'alpha': 1e-2}
        self.tol = 1e-3
        self.qtype = 0
        self.qparams = 100
        self.tm = self.load_map()
    
    def load_map(self):
        import TransportMaps.XML as TMXML
        tm = TMXML.load_xml( self.map_fname )
        return tm

    def test_xml_solve(self):
        import numpy as np
        import numpy.random as npr
        import TransportMaps.Distributions as DIST
        tm = self.tm
        tar_mu = npr.randn(tm.dim)
        tar_sig = npr.randn(tm.dim**2).reshape((tm.dim, tm.dim))
        tar_sig2 = np.dot(tar_sig, tar_sig.T)
        target = DIST.GaussianDistribution(tar_mu, sigma=tar_sig2)
        base = DIST.StandardNormalDistribution(tm.dim)
        # Create push forward
        push = DIST.PushForwardTransportMapDistribution(tm, base)
        # Solve
        log = push.minimize_kl_divergence(
            target, qtype=self.qtype, qparams=self.qparams)
        
def build_suite(ttype='all'):
    import os
    suites_list = []
    if ttype in ['all','serial']:
        test_map_xml_dir = os.path.dirname(os.path.realpath(__file__)) + \
                           '/xml/maps/'
        xml_map_list = os.listdir(test_map_xml_dir)
        for xml_map_fname in xml_map_list:
            if xml_map_fname.endswith('.xml'):
                map_name = xml_map_fname.split('.xml')[0]
                test_class = type('XML_Map_' + map_name,
                                  (XML_Map_unittest,),
                                  {'map_fname': test_map_xml_dir + xml_map_fname})
                # Append new suite
                suite = unittest.TestLoader().loadTestsFromTestCase( test_class )
                suites_list.append( suite )
    all_suites = unittest.TestSuite(suites_list)
    return all_suites

def run_tests(ttype='all'):
    all_suites = build_suite(ttype)
    # RUN
    unittest.TextTestRunner(verbosity=2).run(all_suites)

if __name__ == '__main__':
    run_tests()
