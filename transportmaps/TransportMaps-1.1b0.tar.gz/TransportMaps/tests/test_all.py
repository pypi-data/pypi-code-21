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
# Authors: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import logging
import numpy.random as npr

def run_all(log_level=logging.WARNING, ttype='all'):
    # ttype: 'all', 'serial', 'parallel'

    npr.seed(1)

    import sys
    import unittest
    import TransportMaps as TM
    from TransportMaps.tests import test_distributions
    from TransportMaps.tests import test_laplace
    from TransportMaps.tests import test_transportmaps
    from TransportMaps.tests import test_transportmap_distributions
    from TransportMaps.tests import test_transportmap_distributions_sampling
    from TransportMaps.tests import test_kl_divergence
    from TransportMaps.tests import test_kl_minimization
    from TransportMaps.tests import test_L2_misfit
    from TransportMaps.tests import test_L2_minimization
    from TransportMaps.tests import test_xml
    from TransportMaps.tests import test_scripts
    from TransportMaps.tests import test_sequential_inference

    TM.setLogLevel(log_level)

    suites_list = [ test_distributions.build_suite(ttype),
                    test_laplace.build_suite(ttype),
                    test_transportmaps.build_suite(ttype),
                    test_transportmap_distributions.build_suite(ttype),
                    test_transportmap_distributions_sampling.build_suite(ttype),
                    test_kl_divergence.build_suite(ttype),
                    test_kl_minimization.build_suite(ttype),
                    test_L2_misfit.build_suite(ttype),
                    test_L2_minimization.build_suite(ttype),
                    test_xml.build_suite(ttype),
                    test_scripts.build_suite(ttype),
                    test_sequential_inference.build_suite(ttype)]
    all_suites = unittest.TestSuite( suites_list )
    # RUN
    tr = unittest.TextTestRunner(verbosity=2).run(all_suites)
    # Raise error if some tests failed or exited with error state
    nerr = len(tr.errors)
    nfail = len(tr.failures)
    if nerr + nfail > 0:
        print("Errors: %d, Failures: %d" % (nerr, nfail))
        sys.exit(1)

if __name__ == '__main__':
    run_all(ttype='all')
