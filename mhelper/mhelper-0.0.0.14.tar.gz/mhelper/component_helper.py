"""
Contains the `ComponentFinder` class.
"""
from typing import List

class ComponentFinder:
    """
    Allows one to find connected components given a graph-like data-set without having to actually construct the graph. 
    
    Usage
    -----
    ```
    component_finder = ComponentFinder()
    
    component_finder.equate(1, 2)
    component_finder.equate(2, "Eggs")
    component_finder.equate("Eggs", object)
    
    component_finder.tabulate()
    ```
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        Nothing special.
        """
        self.__table = { }
        self.__next = 0
        self.__valid = set()
    
    
    def equate( self, a, b ):
        """
        Sets the nodes `a` and `b` as being in the same component (i.e. that they share an edge).
        
        :param a: 
        :param b: 
        :return: 
        """
        # get existing components
        ac = self.__table.get( a )
        bc = self.__table.get( b )
        
        if ac is not None:
            if bc is not None:
                if ac != bc:
                    # we know now that ac and bc are actually the same!
                    self.__substitute( bc, ac )
            else:
                # b has no component, so it belongs to a
                self.__table[ b ] = ac
        else:
            if bc is not None:
                self.__table[ a ] = bc
            else:
                self.__table[ a ] = self.__next
                self.__table[ b ] = self.__next
                self.__valid.add( self.__next )
                self.__next += 1
    
    
    def tabulate( self ) -> List[ List[ object ] ]:
        """
        Obtains the result as a list of lists.
        Each list in the result represents a component and its contents the contents of that component.
        
        :return:    List[ List[ object ] ]
        """
        order = list( self.__valid )
        new_order = { }
        
        for index, value in enumerate( order ):
            new_order[ value ] = index
        
        for k, v in list( self.__table.items() ):
            vv = new_order[ v ]
            self.__table[ k ] = vv
        
        self.__valid = set( new_order.values() )
        
        self.__next = len( self.__valid )
        
        return self.__create_groups()
    
    
    def __create_groups( self ):
        results = [ ]
        for i in range( self.__next ):
            results.append( [ ] )
        for k, v in self.__table.items():
            results[ v ].append( k )
        return results
    
    
    def __substitute( self, original_number, replacement_number ):
        fix = [ ]
        
        for k, v in self.__table.items():
            if v == original_number:
                fix.append( k )
        
        for k in fix:
            self.__table[ k ] = replacement_number
        
        self.__valid.remove( original_number )
