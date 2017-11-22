from typing import cast, Iterator

from neocommand.database.endpoints import IOrigin, IMasterOrigin
from neocommand.database.entities import Node, Edge, IEntity


def transfer_with_lookup( input: IOrigin, lookup: IMasterOrigin, cache: bool = True ) -> Iterator[ IEntity ]:
    if cache:
        edge_cache = { }
        node_cache = { }
    
    for entity in input.origin_get_all():
        if isinstance( entity, Edge ):
            #
            # EDGES
            #
            edge = cast( Edge, entity )
            
            if edge.start is not None and edge.end is not None:
                if edge.start.label is not None and edge.start.uid is not None and edge.end.label is not None and edge.end.uid is not None:
                    #
                    # EDGE: End UIDs
                    #
                    if cache:
                        cache_id = "e" + edge.label + "\t" + edge.start.label + "\t" + edge.end.label + "\t" + edge.start.uid + "\t" + edge.end.uid
                        result = edge_cache.get( cache_id )
                        
                        if result is not None:
                            yield result
                            continue
                    
                    result = lookup.origin_get_edge_by_node_uids( label = edge.label,
                                                                  start_label = edge.start.label,
                                                                  end_label = edge.end.label,
                                                                  start_uid = edge.start.uid,
                                                                  end_uid = edge.end.uid )
                    
                    if result is not None:
                        if cache:
                            edge_cache[ cache_id ] = result
                        
                        yield result
                        continue
                
                elif edge.start.iid is not None and edge.end.iid is not None:
                    #
                    # EDGE: End IIDs
                    #
                    if cache:
                        cache_id = "e" + str( edge.start.iid ) + "\t" + str( edge.end.iid )
                        result = edge_cache.get( cache_id )
                        
                        if result is not None:
                            yield result
                            continue
                    
                    result = lookup.origin_get_edge_by_node_iids( start_iid = edge.start.iid, end_iid = edge.end.iid )
                    
                    if result is not None:
                        if cache:
                            edge_cache[ cache_id ] = result
                        
                        yield result
                        continue
            
            if edge.iid is not None:
                #
                # EDGE: IID
                #
                if cache:
                    result = edge_cache.get( edge.iid )
                    
                    if result is not None:
                        yield result
                        continue
                
                result = lookup.origin_get_edge_by_iid( edge.iid )
                
                if result is not None:
                    if cache:
                        edge_cache[ edge.iid ] = result
                    
                    yield result
                    continue
            
            raise ValueError( "Cannot make the edge concrete because I can't find it or it doesn't exist in the database." )
        elif isinstance( entity, Node ):
            #
            # NODES
            #
            node = cast( Node, entity )
            
            if node.label is not None and node.uid is not None:
                #
                # NODE: UID
                #
                if cache:
                    cache_id = "n" + node.label + "\t" + node.uid
                    result = node_cache.get( cache_id )
                    
                    if result is not None:
                        yield result
                        continue
                
                result = lookup.origin_get_node_by_uid( node.label, node.uid )
                
                if result is not None:
                    if cache:
                        node_cache[ cache_id ] = result
                    
                    yield result
                    continue
            
            if node.iid is not None:
                #
                # NODE: IID
                #
                if cache:
                    result = node_cache.get( node.iid )
                    
                    if result is not None:
                        yield result
                        continue
                
                result = lookup.origin_get_node_by_uid( node.label, node.uid )
                
                if result is not None:
                    if cache:
                        node_cache[ node.iid ] = result
                    
                    yield result
                    continue
            
            raise ValueError( "Cannot make the node concrete because I can't find it or it doesn't exist in the database." )
