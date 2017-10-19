"""!

@brief Unit-tests for K-Means algorithm.

@authors Andrei Novikov (pyclustering@yandex.ru)
@date 2014-2017
@copyright GNU Public License

@cond GNU_PUBLIC_LICENSE
    PyClustering is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    PyClustering is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
@endcond

"""


import unittest;

from pyclustering.cluster.tests.kmeans_templates import KmeansTestTemplates;

from pyclustering.cluster.kmeans import kmeans;

from pyclustering.samples.definitions import SIMPLE_SAMPLES;


class KmeansUnitTest(unittest.TestCase):
    def testClusterAllocationSampleSimple1(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE1, [[3.7, 5.5], [6.7, 7.5]], [5, 5]);

    def testClusterOneAllocationSampleSimple1(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE1, [[1.0, 2.5]], [10]);

    def testClusterAllocationSampleSimple2(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE2, [[3.5, 4.8], [6.9, 7], [7.5, 0.5]], [10, 5, 8]);

    def testClusterOneAllocationSampleSimple2(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE2, [[0.5, 0.2]], [23]);

    def testClusterAllocationSampleSimple3(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE3, [[0.2, 0.1], [4.0, 1.0], [2.0, 2.0], [2.3, 3.9]], [10, 10, 10, 30]);    

    def testClusterOneAllocationSampleSimple3(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE3, [[0.2, 0.1]], [60]);

    def testClusterAllocationSampleSimple4(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE4, [[1.5, 0.0], [1.5, 2.0], [1.5, 4.0], [1.5, 6.0], [1.5, 8.0]], [15, 15, 15, 15, 15]);

    def testClusterOneAllocationSampleSimple4(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE4, [[2.0, 5.0]], [75]);

    def testClusterAllocationSampleSimple5(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE5, [[0.0, 1.0], [0.0, 0.0], [1.0, 1.0], [1.0, 0.0]], [15, 15, 15, 15]);

    def testClusterOneAllocationSampleSimple5(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE5, [[0.0, 0.0]], [60]);

    def testClusterOneDimensionSampleSimple7(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE7, [[-3.0], [2.0]], [10, 10]);

    def testClusterOneDimensionSampleSimple8(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE8, [[-4.0], [3.1], [6.1], [12.0]], [15, 30, 20, 80]);

    def testWrongNumberOfCentersSimpleSample1(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE1, [[2.0, 4.5], [3.3, 6.5], [5.0, 7.8]], None);

    def testWrongNumberOfCentersSimpleSample2(self):
        KmeansTestTemplates.templateLengthProcessData(SIMPLE_SAMPLES.SAMPLE_SIMPLE2, [[1.3, 1.5], [5.2, 8.5], [5.0, 7.8], [11.0, -3.0]], None);

    def testDifferentDimensions(self):
        kmeans_instance = kmeans([ [0, 1, 5], [0, 2, 3] ], [ [0, 3] ]);
        self.assertRaises(NameError, kmeans_instance.process);


    def testClusterAllocationOneDimensionData(self):
        KmeansTestTemplates.templateClusterAllocationOneDimensionData(False);


    def testEncoderProcedureSampleSimple4(self):
        KmeansTestTemplates.templateEncoderProcedures(SIMPLE_SAMPLES.SAMPLE_SIMPLE4, [[1.5, 0.0], [1.5, 2.0], [1.5, 4.0], [1.5, 6.0], [1.5, 8.0]], 5, False);


if __name__ == "__main__":
    unittest.main();
