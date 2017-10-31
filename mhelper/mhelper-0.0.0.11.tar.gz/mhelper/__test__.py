import unittest

from mhelper import BatchList, array_helper, batch_lists, string_helper


class string_helper_tests( unittest.TestCase ):
    def test_highlight_quotes( self ):
        self.assertEqual( string_helper.highlight_quotes( "hello 'world' hello's", "'", "'", "<", ">" ), "hello <world> hello's" )


class array_helper_tests( unittest.TestCase ):
    def test__create_index_lookup( self ):
        """
        TEST: create_index_lookup
        """
        
        my_list = "a", "b", "c", "d", "e"
        
        lookup = array_helper.create_index_lookup( my_list )
        
        # Sanity check
        for i, v in enumerate( my_list ):
            self.assertEqual( i, lookup[ v ] )


class batch_lists_test( unittest.TestCase ):
    def test__BatchList__take( self ):
        b = BatchList( (1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 3 )
        
        self.assertEqual( b.take(), [ 1, 2, 3 ] )
        self.assertEqual( b.take(), [ 4, 5, 6 ] )
        self.assertEqual( b.take(), [ 7, 8, 9 ] )
        self.assertEqual( b.take(), [ 10, ] )
    
    
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


# class io_helper_tests( unittest.TestCase ):
#     def test_save_bytes_manually( self ):
#         print( "INITIALISE" )
#         my_bytes = bytearray( 3250000000 )
#         
#         n = 0
#         
#         print( "CREATE" )
#         for j in range( 0, 32 ), range( 0, len( my_bytes ), 100000 ), range( len( my_bytes ) - 32, len( my_bytes ) ):
#             for i in j:
#                 my_bytes[ i ] = n
#                 n += 1
#                 
#                 if n > 255:
#                     n = 0
#         
#         my_bytes = bytes( my_bytes )
#         
#         print( "SAVE" )
#         io_helper._save_bytes_manually( "temp-del-me.tmp", my_bytes )
#         
#         saved_size = float( file_helper.file_size( "temp-del-me.tmp" ) )
#         
#         self.assertEquals( saved_size, len( my_bytes ) )
#         
#         print( "RELOAD" )
#         
#         new_bytes = bytearray()
#         
#         with open( "temp-del-me.tmp", "rb" ) as in_file:
#             while True:
#                 read = in_file.read( 1000000 )
#                 
#                 if not read:
#                     break
#                 
#                 new_bytes.extend( read )
#             
#             print( "EXISTING: {}".format( len( my_bytes ) ) )
#             print( "RELOADED: {}".format( len( new_bytes ) ) )
#             print( "EXISTING: {}".format( my_bytes[ -8: ] ) )
#             print( "RELOADED: {}".format( new_bytes[ -8: ] ) )
#             
#             self.assertEquals( len( my_bytes ), len( new_bytes ) )
#             self.assertEquals( my_bytes[ -8: ], new_bytes[ -8: ] )
#         
#         file_helper.delete_file( "temp-del-me.tmp" )


if __name__ == '__main__':
    unittest.main()
