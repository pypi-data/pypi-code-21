import csv
import unittest

import os

from os import path

from progressivecsv.progressive_csv import ProgressiveCsvWriter


class ProgressiveCsvTest( unittest.TestCase ):
    def test_one( self ):
        temp_file_name = "ProgressiveCsvTest.~tmp"
        
        if path.isfile( temp_file_name ):
            os.remove( temp_file_name )
        
        self.assertFalse( path.isfile( temp_file_name ) )
        
        w = ProgressiveCsvWriter( temp_file_name, default = "X" )
        
        w.write_row( { "alpha": "a1" } )  # 0
        w.write_row( { "alpha": "a2" } )  # 1
        w.write_row( { "alpha": "a3" } )  # 2
        w.write_row( { "alpha": "a4", "beta": "b4" } )  # 3
        w.write_row( { "alpha": "a5", "beta": "b5" } )  # 4
        w.write_row( { "alpha": "a6", "beta": "b6" } )  # 5
        
        w.close()
        w = ProgressiveCsvWriter( temp_file_name, default = "X" )
        
        w.write_row( { "alpha": "a7", "beta": "b7", "gamma": "c7" } )  # 6
        w.write_row( { "alpha": "a8", "beta": "b8", "gamma": "c8" } )  # 7
        w.write_row( { "alpha": "a9", "beta": "b9", "gamma": "c9" } )  # 8
        w.write_row( { "alpha": "a10", "delta": "d10" } )  # 9
        w.write_row( { "alpha": "a11", "delta": "d11" } )  # 10
        w.write_row( { "alpha": "a12", "delta": "d12" } )  # 11
        w.write_row( { "alpha": "a13", "gamma": "c13" } )  # 12
        w.write_row( { "alpha": "a14", "gamma": "c14" } )  # 13
        w.write_row( { "alpha": "a15", "gamma": "c15" } )  # 14
        
        self.assertEqual( w.needs_rewrite, True )
        self.assertEqual( w.headers["alpha"].index, 0 )
        self.assertEqual( w.headers["beta"].index, 1 )
        self.assertEqual( w.headers["gamma"].index, 2 )
        self.assertEqual( w.headers["delta"].index, 3 )
        
        self.assertFalse( path.isfile( temp_file_name ) )
        
        w.close()
        
        self.assertTrue( path.isfile( temp_file_name ) )
        
        with open( temp_file_name, "r" ) as file:
            r = csv.DictReader( file )
            
            self.assertEqual( r.fieldnames, ["alpha", "beta", "gamma", "delta"] )
            
            all_ = list( r )
            
            self.assertEqual( len( all_ ), 15 )
            self.assertEqual( all_[0], { "alpha": "a1", "beta": "X", "gamma": "X", "delta": "X" } )
            self.assertEqual( all_[1], { "alpha": "a2", "beta": "X", "gamma": "X", "delta": "X" } )
            self.assertEqual( all_[2], { "alpha": "a3", "beta": "X", "gamma": "X", "delta": "X" } )
            self.assertEqual( all_[3], { "alpha": "a4", "beta": "b4", "gamma": "X", "delta": "X" } )
            self.assertEqual( all_[4], { "alpha": "a5", "beta": "b5", "gamma": "X", "delta": "X" } )
            self.assertEqual( all_[5], { "alpha": "a6", "beta": "b6", "gamma": "X", "delta": "X" } )
            self.assertEqual( all_[6], { "alpha": "a7", "beta": "b7", "gamma": "c7", "delta": "X" } )
            self.assertEqual( all_[7], { "alpha": "a8", "beta": "b8", "gamma": "c8", "delta": "X" } )
            self.assertEqual( all_[8], { "alpha": "a9", "beta": "b9", "gamma": "c9", "delta": "X" } )
            self.assertEqual( all_[9], { "alpha": "a10", "delta": "d10", "beta": "X", "gamma": "X" } )
            self.assertEqual( all_[10], { "alpha": "a11", "delta": "d11", "beta": "X", "gamma": "X" } )
            self.assertEqual( all_[11], { "alpha": "a12", "delta": "d12", "beta": "X", "gamma": "X" } )
            self.assertEqual( all_[12], { "alpha": "a13", "gamma": "c13", "beta": "X", "delta": "X" } )
            self.assertEqual( all_[13], { "alpha": "a14", "gamma": "c14", "beta": "X", "delta": "X" } )
            self.assertEqual( all_[14], { "alpha": "a15", "gamma": "c15", "beta": "X", "delta": "X" } )
        
        os.remove( temp_file_name )
        
        self.assertFalse( path.isfile( temp_file_name ) )


if __name__ == '__main__':
    unittest.main()
