import ICP
import os
import unittest

class TestFontFileAvailability(unittest.TestCase):

    def test_fontFileExists(self):
        print("testing for the availability of the font file 'FreeSerif.ttf'")
        available = False;
        if os.path.isfile("FreeSerif.ttf"):
            available = True;
        elif (os.path.exists("/usr/share/fonts/truetype/freefont/FreeSerif.ttf")):
            available = True;
        if not available:
            print( '''\n\n
                     The display of results requires access to the "FreeSerif.ttf" 
                     font file for the labels that are needed in the display panel.
                     The module assumes that this file can be located through 
                     the paths stored in 'sys.path', or via the paths available 
                     through your environment variables, or at the following path:

                          /usr/share/fonts/truetype/freefont/FreeSerif.ttf

                     which is typical for a Ubuntu install.\n\n''')
        self.assertEqual( available, True )

def getTestSuites(type):
    return unittest.TestSuite([
            unittest.makeSuite(TestFontFileAvailability, type)
                             ])                    
if __name__ == '__main__':
    unittest.main()

