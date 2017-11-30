'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import sys
import unittest
from PyQt5.QtTest import QSignalSpy, QTest
from PyQt5.QtWidgets import QApplication
from specguiutils.scanbrowser import ScanBrowser
from spec2nexus.spec import SpecDataFile
import specguiutils
import os
#from matplotlib.cm import spec
app =  QApplication(sys.argv)

FLUORESCENCE_FILE = "Brian-Nick/Fluorescence/lineup"
SCAN_TYPES = ["all", "slitscan", "ascan", "undscan", "Escan", "qxdichro", \
              "tempdichro", "kepdichro", "qxscan"]
NUM_SCAN_TYPES = [116, 5, 60, 1, 9, 27, 5, 1, 8 ]

class TestScanBrowserTest(unittest.TestCase):

    def setUp(self):
        self.scanBrowser = ScanBrowser()
        self.dataPath = os.environ.get('DATAPATH')
        self.spyLoaded = QSignalSpy(self.scanBrowser.scanLoaded)
        self.spySelected = QSignalSpy(self.scanBrowser.scanSelected)
        print ("self.dataPath %s" % self.dataPath)
        
    def tearDown(self):
        pass


    def testLoadScans(self):
        specFile = os.path.join(self.dataPath, FLUORESCENCE_FILE)
        print ("SpecDataFile %s" % specFile)
        specData = SpecDataFile(specFile)
        self.scanBrowser.loadScans(specData.scans, newFile=True)
        self.assertEqual(len(self.spyLoaded), 1)
        self.assertEqual(len(self.spySelected), 0)
        self.assertEqual(self.scanBrowser.scanList.rowCount(),
                         len(specData.getScanNumbers()))
    
    def testFilterByScanTypes(self):
        specFile = os.path.join(self.dataPath, FLUORESCENCE_FILE)
        spyLoaded = QSignalSpy(self.scanBrowser.scanLoaded)
        specData = SpecDataFile(specFile)
        self.scanBrowser.loadScans(specData.scans)
        self.assertEqual(len(spyLoaded),1)
        self.assertEqual(len(self.spySelected), 0)
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[1])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[1])
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[2])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[2])
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[3])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[3])
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[4])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[4])
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[5])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[5])
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[6])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[6])
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[7])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[7])
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[8])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[8])
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[1:])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[0])
        self.scanBrowser.filterByScanTypes(specData.scans, [])
        self.assertEqual(self.scanBrowser.scanList.rowCount(), NUM_SCAN_TYPES[0])
        with self.assertRaises(ValueError):
            self.scanBrowser.filterByScanTypes(specData.scans, None)
        self.assertEqual(NUM_SCAN_TYPES[0], sum(NUM_SCAN_TYPES[1:]))
        self.assertEqual(len(spyLoaded),11)
        self.assertEqual(len(self.spySelected), 0)

    def testScanSelected(self):
        selectedScan = 5
        specFile = os.path.join(self.dataPath, FLUORESCENCE_FILE)
        spyLoaded = QSignalSpy(self.scanBrowser.scanLoaded)
        specData = SpecDataFile(specFile)
        self.scanBrowser.loadScans(specData.scans)
        self.assertEqual(len(spyLoaded),1)
        self.assertEqual(len(self.spySelected), 0)
        self.scanBrowser.setCurrentScan(selectedScan)
        self.assertEqual(len(spyLoaded),1)
        self.assertEqual(len(self.spySelected), 1)
        self.assertEqual(self.scanBrowser.getCurrentScan(), '6')
        self.scanBrowser.filterByScanTypes(specData.scans, SCAN_TYPES[2])
        self.assertEqual(len(spyLoaded),2)
        self.assertEqual(len(self.spySelected), 1)
        # Doesn't register a selection change since row has not changed
        self.scanBrowser.setCurrentScan(selectedScan)
        self.assertEqual(len(spyLoaded),2)
        self.assertEqual(len(self.spySelected), 1)
        self.assertEqual(self.scanBrowser.getCurrentScan(), '12')
        # Register a selection change since row changed
        self.scanBrowser.setCurrentScan(selectedScan + 1)
        self.assertEqual(len(spyLoaded),2)
        self.assertEqual(len(self.spySelected), 2)
        self.assertEqual(self.scanBrowser.getCurrentScan(), '13')
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()