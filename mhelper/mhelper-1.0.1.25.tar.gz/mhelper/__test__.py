import unittest
from typing import Optional, Union

from mhelper import BatchList, array_helper, batch_lists, string_helper, AnnotationInspector




class string_helper_tests( unittest.TestCase ):
    def test_highlight_quotes( self ):
        self.assertEqual( string_helper.highlight_quotes( "hello 'world' hello's", "'", "'", "<", ">" ), "hello <world> hello's" )
    
    
    def test_fix_indents( self ):
        text_a = """alpha\n\n        beta\n            gamma\n                delta\n        epsilon\n    """
        text_b = """alpha\n\nbeta\n    gamma\n        delta\nepsilon\n"""
        self.assertEqual( string_helper.fix_indents( text_a ), text_b )


class array_helper_tests( unittest.TestCase ):
    def test__create_index_lookup( self ):
        """
        TEST: create_index_lookup
        """
        
        my_list = "a", "b", "c", "d", "e"
        
        lookup = array_helper.create_index_lookup( my_list )
        
        # Sanity check
        for i, v in enumerate( my_list ):
            self.assertEqual( i, lookup[v] )


class batch_lists_test( unittest.TestCase ):
    def test__BatchList__take( self ):
        b = BatchList( (1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 3 )
        
        self.assertEqual( b.take(), [1, 2, 3] )
        self.assertEqual( b.take(), [4, 5, 6] )
        self.assertEqual( b.take(), [7, 8, 9] )
        self.assertEqual( b.take(), [10, ] )
    
    
    def test__divide_workload( self ):
        self.assertEqual( batch_lists.divide_workload( 0, 5, 51 ), (0, 10) )
        self.assertEqual( batch_lists.divide_workload( 1, 5, 51 ), (10, 20) )
        self.assertEqual( batch_lists.divide_workload( 2, 5, 51 ), (20, 30) )
        self.assertEqual( batch_lists.divide_workload( 3, 5, 51 ), (30, 40) )
        self.assertEqual( batch_lists.divide_workload( 4, 5, 51 ), (40, 51) )
    
    
    def test__divide_workload_2( self ):
        last_b = None
        for i in range( 1000 ):
            a, b = batch_lists.divide_workload( i, 1000, 1600 )
            
            self.assertGreater( b, a )
            
            if last_b is not None:
                self.assertEqual( a, last_b )
            
            last_b = b


class reflection_helper_tests( unittest.TestCase ):
    def test__annotations( self ):
        class UPPER:
            pass
        
        
        class MIDDLE( UPPER ):
            pass
        
        
        class LOWER( MIDDLE ):
            pass
        
        
        class DIFFERENT:
            pass
        
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_indirectly_below( UPPER ) )
        self.assertTrue( AnnotationInspector( Optional[MIDDLE] ).is_indirectly_below( UPPER ) )
        self.assertTrue( AnnotationInspector( Optional[Union[DIFFERENT, MIDDLE]] ).is_indirectly_below( UPPER ) )
        self.assertFalse( AnnotationInspector( Optional[Union[DIFFERENT, MIDDLE]] ).is_indirectly_below( LOWER ) )
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_directly_below( UPPER ) )
        self.assertFalse( AnnotationInspector( Optional[MIDDLE] ).is_directly_below( UPPER ) )
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_indirectly_above( LOWER ) )
        self.assertTrue( AnnotationInspector( Optional[MIDDLE] ).is_indirectly_above( LOWER ) )
        self.assertTrue( AnnotationInspector( Optional[Union[DIFFERENT, MIDDLE]] ).is_indirectly_above( LOWER ) )
        self.assertFalse( AnnotationInspector( Optional[Union[DIFFERENT, MIDDLE]] ).is_indirectly_above( UPPER ) )
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_directly_above( LOWER ) )
        self.assertFalse( AnnotationInspector( Optional[MIDDLE] ).is_directly_above( LOWER ) )
        
        middle = MIDDLE()
        
        self.assertTrue( AnnotationInspector( MIDDLE ).is_viable_instance( middle ) )
        self.assertTrue( AnnotationInspector( Optional[UPPER] ).is_viable_instance( middle ) )
        self.assertTrue( AnnotationInspector( Union[LOWER, UPPER] ).is_viable_instance( middle ) )
        self.assertFalse( AnnotationInspector( Union[LOWER] ).is_viable_instance( middle ) )


if __name__ == '__main__':
    unittest.main()
