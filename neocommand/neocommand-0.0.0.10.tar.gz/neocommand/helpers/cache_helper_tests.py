import unittest
from typing import List, cast

from mhelper import ignore


class CacheHelper_tests( unittest.TestCase ):
    def test_compute_cluster_tests( self ):
        ignore(self)
        import random
        from time import sleep
        from intermake.engine.environment import MCMD
        from intermake.plugins.command_plugin import command
        from neocommand.helpers import cache_helper
        from neocommand.helpers.cache_helper import EFormat

        @command(visibility = False)
        def compute_cluster_test_1( ):
            """
            Tests caching on a compute cluster.
            
            The first process calculates the value, the other processes wait for it.
            
            NOTE: The cache must be deleted manually after-the-fact in order to reset the test.
            """
            MCMD.print("Entered compute_cluster_test_1")
            
            cache_name = [ "test_cache_1" ]

            
            cached = cache_helper.load_cache_binary_b42( cache_name, single = True )
            
            if cached is None:
                assert MCMD.thread_index == 0
                sleep( 2 )
                cache_helper.save_cache_binary_b42( cache_name, "hello" )
                MCMD.information( "Test passed (first cached value)" )
            else:
                if MCMD.thread_index == 0:
                    raise ValueError( "The cache already existed. Cannot perform the test." )
                
                assert cached == "hello"
                MCMD.information( "Test passed (second retrieved cache)" )
                
            MCMD.print("Exiting compute_cluster_test_1")
            

        @command(visibility = False)
        def compute_cluster_test_2( ) -> None:
            """
            Tests caching on a compute cluster.
            
            Each process calculates its own value, then the first process collates them.
            
            NOTE: The cache is deleted automatically, but only if the test passes.
                  If the test fails, the cache must be deleted manually in order to reset the test.
            """
            MCMD.print("Entered compute_cluster_test_2")
            
            cache_name : List[object] = [ "test_cache_2" ] + [ MCMD.thread_index ]
            
            cached = cache_helper.load_cache_binary_b42( cache_name )
            
            if cached is not None:
                raise ValueError( "The cache already existed. Cannot perform the test." )
            
            sleep( random.uniform( 1, 5 ) )
            
            cache_helper.save_cache_binary_b42( cache_name, "hello from {} of {}".format( MCMD.thread_index, MCMD.num_threads ) )
            
            if MCMD.is_secondary_thread:
                MCMD.information( "Thread exiting (complete)" )
                return
            
            for i in range( MCMD.num_threads ):
                cache_name  = [ cast(object, "test_cache_2") ] + [ i ]
                message = cache_helper.load_cache_binary_b42( cache_name, wait = True )
                assert message
                MCMD.information( "Result from {}: {}".format( i, message ) )
                cache_helper.delete_cache( cache_name, EFormat.BINARY_B42 )
                
            MCMD.print("Exiting compute_cluster_test_2")


        compute_cluster_test_1()
        compute_cluster_test_2()

