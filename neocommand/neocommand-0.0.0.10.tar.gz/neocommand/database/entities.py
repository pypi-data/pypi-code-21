"""
Dockets are generally just pointers to database nodes or edges, though they can contain full information.
Unlike the "py2neo" objects, our dockets are internally serialisable and tailored to our database.

Purposes:
 * the user can keep hold of the small dockets on their computer, but we can use their information to rapidly lookup full information when the user demands it.
 * we can marshal our data easily, regardless of whether it came from "py2neo", "neo4j.v1" or some other source (e.g. CSV).
 * dockets can also store full information, so we also use them to hold information before we insert it into the database
    * and unlike the "py2neo" entities, dockets can be inserted via any of our import methods: directly, bulk-import, or create-new-database

Realisation:
    Depending on the driver, pointer-type dockets may point to a node by UID or IID (neo4j `ID(...)`).
    IID isn't recommended by the Neo4j documentation, but unfortunately its what their "Neo4j.v1" driver gives us.

    All dockets:
        * can possess a descriptive name and/or comment
        * are iterable, yielding key-value tuples.
        * either contain other dockets, or simple types.
    
See also:
    * `TypeHandler` -> displayed to the user.
    * `DbManager` -> retrieved from the database.
    * `Plugin.Utility` -> added to the database (by plugins).
    * `Parsers` -> added to the database (import from file) 

"""
from typing import Callable, Dict, List, Optional, Union

from intermake import EColour, IVisualisable, UiInfo
from intermake.engine.constants import mandated
from mhelper import abstract, override, virtual
from neocommand.gui_qt import resources


__author__ = "Martin Rusilowicz"

EDGE_UID_DELIMITER = ":"


@abstract
class IEntity( IVisualisable ):
    """
    Base class for all entities.
    
    The entities may have a database presence, or not.
    
    See module documentation above for details.
    """
    
    
    #
    # IENTITY - MAIN
    #
    
    def __init__( self, name: Optional[ str ], comment: Optional[ object ] ):
        """
        CONSTRUCTOR
        :param name: User-provided name on the docket. Can be `None`, in which case something else like the node UID is usually displayed. 
        :param comment: User-comment on the docket. Can also be `None`. 
        """
        self.name = name
        self.comment = comment
    
    
    #
    # IENTITY - IVISUALISABLE OVERRIDES
    #
    
    
    
    
    @override
    @abstract
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE 
        """
        raise NotImplementedError( "abstract" )
    
    
    @override
    @virtual
    def __str__( self ):
        """
        OVERRIDE 
        """
        return self.name or "(untitled)"
    
    
    @override
    def __repr__( self ):
        """
        OVERRIDE 
        """
        return "{0}(name = «{1}»)".format( type( self ).__name__, self.name )


class Node( IEntity ):
    """
    References a graph node.
    
    Nodes can act as pointers that can be "looked up" providing they have a `label`+`uid` OR an `iid`.
    
    If `data` is not `None` then the full-data should be assumed to already be available, and a lookup avoided.
    Note that this makes `data = None` and `data = {}` different.
    There is a separate (internal) `__partial_data` field, that keeps a cache of partial lookups.
    
    Nodes can be added or merged into the database providing they have `data`.
    """
    
    
    def __init__( self,
                  *,
                  label: Optional[ str ] = None,
                  uid: Optional[ str ] = None,
                  iid: Optional[ int ] = None,
                  name: Optional[ str ] = None,
                  comment: Optional[ str ] = None,
                  properties: Dict[ object, object ] = None ):
        """
        :param *: 
        :param label: Label of the node. Can be `None`. 
        :param uid: UID of the node. Can be `None`.
        :param iid: IID of the node. Can be `None`. 
        :param name: Inherited.
        :param comment: Inherited. 
        :param properties: Data on the node. Use `None` if not known, or `{}` if it is known to be empty.
        """
        super().__init__( name, comment )
        
        self.label = label
        self.uid = uid
        self.iid = iid
        
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
    
    
    def visualisable_info( self ):
        return UiInfo( name = str(self),
                       comment = self.comment,
                       type_name = "Node" if self.visualisable_is_loaded() else "Node*",
                       value = self.description(),
                       colour = EColour.BLUE,
                       icon = resources.node,
                       extra = { "label"     : self.label,
                                 "uid"       : self.uid,
                                 "properties": self.properties } )
    
    
    def __getnewargs__( self ):
        return ()
    
    
    @override
    def __getstate__( self ):
        return { "name"      : self.name,
                 "comment"   : self.comment,
                 "label"     : self.label,
                 "uid"       : self.uid,
                 "iid"       : self.iid,
                 "properties": self.properties }
    
    
    @override
    def __setstate__( self, state ):
        self.name = state[ "name" ]
        self.comment = state[ "comment" ]
        self.label = state[ "label" ]
        self.uid = state[ "uid" ]
        self.iid = state[ "iid" ]
        self.properties = state[ "properties" ]
    
    
    def description( self ):
        if self.label and self.uid:
            return self.label + " " + self.uid
        elif self.iid:
            return "#{0}".format( self.iid )
        else:
            return "?"


class Edge( IEntity ):
    """
    References a database edge.
    
    An edge can be looked up providing it has a `start` and `end` node that themselves can be looked up, or that it provides an `iid`.
    Apart from that see the documentation for `Node`.
    
    """
    
    
    def __init__( self,
                  *,
                  label: str,
                  start: Node,
                  end: Node,
                  name: Optional[ str ] = None,
                  comment: Optional[ str ] = None,
                  iid: Optional[ int ] = None,
                  data: Optional[ Dict[ object, object ] ] ):
        """
        :param *: 
        :param name: Inherited 
        :param comment: Inherited 
        :param iid: Same as for `Node` 
        :param label: Same as for `Node`  
        :param start: Start node 
        :param end: End node 
        :param data: Same as for `Node` 
        """
        super().__init__( name, comment )
        self.label = label
        self.start = start
        self.iid = iid
        self.end = end
        self.properties = data
    
    
    def visualisable_info( self ):
        return UiInfo( name = str(self),
                       comment = self.comment,
                       type_name = "Edge" if self.visualisable_is_loaded() else "Edge*",
                       value = self.value_description(),
                       colour = EColour.GREEN,
                       icon = resources.edge,
                       extra = { "label"     : self.label,
                                 "start"     : self.start,
                                 "end"       : self.end,
                                 "properties": self.properties } )
    
    
    @override
    def __getstate__( self ):
        return { "name"   : self.name,
                 "comment": self.comment,
                 "label"  : self.label,
                 "start"  : self.start,
                 "iid"    : self.iid,
                 "end"    : self.end,
                 "exists" : self.exists.name, }
    
    
    @override
    def __setstate__( self, state ):
        self.name = state[ "name" ]
        self.comment = state[ "comment" ]
        self.label = state[ "label" ]
        self.start = state[ "start" ]
        self.iid = state[ "iid" ]
        self.end = state[ "end" ]
        self.properties = None
    
    
    def value_description( self ):
        if self.label is not None:
            return "{0} ➙{1}➙ {2}".format( self.start, self.label, self.end )
        elif self.iid is not None:
            return "{0} ➙#{1}➙ {2}".format( self.start, self.iid, self.end )
        else:
            return "{0} ➙?➙ {2}".format( self.start, self.iid, self.end )


def all_nodes( root: object, filter: str = None ) -> List[ Node ]:
    results = { }
    
    iterator = iterate_all( root, (lambda x: isinstance( x, Node ) and x.label == filter) if filter else None )
    
    for x in iterator:
        results[ x.uid ] = x
    
    return list( results.values() )


@mandated
def iterate_all( root: object,
                 filter: Union[ None, type, Callable[ [ object ], bool ] ] = None ):
    """
    Give a starting docket, iterates that docket and all its children (if it is a folder)
    
    :param filter: Filter on type 
    :param root: Where to start 
    :return: Iterator over all contents 
    """
    from neocommand.database.endpoints import MemoryEndpoint
    
    if isinstance( filter, type ):
        the_type = filter
        filter = lambda x: isinstance( x, the_type )
    
    if filter is None or filter( root ):
        yield root
    
    if isinstance( root, MemoryEndpoint ):
        for a in root.contents:
            yield from iterate_all( a, filter )
    elif isinstance( root, Edge ):
        yield from iterate_all( root.start, filter )
        yield from iterate_all( root.end, filter )
