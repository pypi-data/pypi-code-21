import unittest


class MathsHelper_test( unittest.TestCase ):
    def test_increment_mean( self ):
        from mhelper import maths_helper
        
        my_values = [ 1, 7, 23, 2, 6, 2, 6, 8, 42, 9, 3, 1, 0.2, 0.3 ]
        
        incremental_average = 0
        incremental_count = 0
        
        for index, new_value in enumerate( my_values ):
            incremental_average, incremental_count = maths_helper.increment_mean( incremental_average, incremental_count, new_value )
            true_average = sum( my_values[ :index + 1 ] ) / (index + 1)
            self.assertAlmostEqual( incremental_average, true_average )
            self.assertEqual( incremental_count, index + 1 )


if __name__ == '__main__':
    unittest.main()
