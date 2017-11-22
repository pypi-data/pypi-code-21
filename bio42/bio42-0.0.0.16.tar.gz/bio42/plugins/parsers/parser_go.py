from intermake import command, MCMD
from mhelper import Filename, EFileMode, string_helper
from neocommand import IEndpoint

from bio42.plugins.parsers.parser_plugin import ParserFilter, ParserPlugin
from bio42.constants import EDGE_GOCLASS_CONTAINS_GOCLASS, NODE_GOCLASS





__mcmd_folder_name__ = "parsers"

_OWL_EXT = ".owl"


@command()
class ParserGo( ParserPlugin ):
    """
    Parses the GO hierarchy, creating both nodes for each GO class, as well as edges between GO subclasses.
    
    This creates the GO nodes only and does not perform any annotation on actual sequences.
    """
    
    
    def __init__( self ):
        super().__init__( "GO", [ ParserFilter( "GO OWL", ".owl", "GO, in OWL (XML) format" ) ] )
    
    
    def iterate_file( self, 
                      endpoint: IEndpoint, 
                      file_name: Filename[EFileMode.READ, _OWL_EXT] ) -> None:
        """
        OVERRIDE
        :param endpoint: Where to send the data to. 
        :param file_name:   Where to get the data from 
        """
        from xml.etree import ElementTree
        from xml.etree.ElementTree import Element
        
        _GO_ID_PREFIX = "GO:"
        
        with MCMD.action("Parsing GO tree"):
            tree = ElementTree.parse( file_name )
        
        root = tree.getroot()
        
        CLASS_ID = '{http://www.w3.org/2002/07/owl#}Class'
        CLASS_SUBCLASS_ID = '{http://www.w3.org/2000/01/rdf-schema#}subClassOf'
        CLASS_SUBCLASS_RESOURCE_ID = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'
        CLASS_ID_ID = '{http://www.geneontology.org/formats/oboInOwl#}id'
        GO_SUBCLASS_ID_REMOVE = 'http://purl.obolibrary.org/obo/GO_'
        
        
        def remove_namespace( tag ):
            tag = str( tag )
            
            if "}" in tag:
                return tag[ tag.index( "}" ) + 1: ]
            
            return tag
        
        with MCMD.action("Parsing GO nodes") as action:
            for element in root:
                if not isinstance( element, Element ):
                    continue
                    
                action.increment()
                
                if element.tag == CLASS_ID:
                    class_subclass = [ ]
                    class_misc = { }
                    class_id = None
                    
                    for sub_element in element:
                        if not isinstance( element, Element ):
                            continue
                        
                        if sub_element.tag == CLASS_SUBCLASS_ID:
                            resource_id = sub_element.get( CLASS_SUBCLASS_RESOURCE_ID )
                            if resource_id:
                                class_subclass.append( string_helper.remove_prefix( resource_id, GO_SUBCLASS_ID_REMOVE ) )
                            continue
                        elif sub_element.tag == CLASS_ID_ID:
                            class_id = string_helper.remove_prefix( sub_element.text, _GO_ID_PREFIX )
                            continue
                        else:
                            key = remove_namespace( sub_element.tag )
                        
                        if key == "IAO_0000115":  # because it's ridiculous
                            key = "description"
                        elif key == "hasOBONamespace":  # because it's also quite silly
                            key = "namespace"
                        elif key == "label":  # because having "node.label" and "node.data.label" as two different things is confusing
                            key = "name"
                        elif key.startswith( "has" ):  # because this makes it sound like a boolean, but it isn't, it's the value
                            key = key[ len( "has" ): ]
                        
                        key = key.lower()
                        
                        if sub_element.text:
                            text = sub_element.text.strip()
                            
                            if text:
                                if key in class_misc:
                                    if not isinstance( class_misc[ key ], list ):
                                        class_misc[ key ] = [ class_misc[ key ] ]
                                    
                                    class_misc[ key ].append( text )
                                else:
                                    class_misc[ key ] = text
                    
                    if class_id:
                        endpoint.endpoint_create_node( label = NODE_GOCLASS, uid = class_id, properties = class_misc )
                        
                        for subclass in class_subclass:
                            endpoint.endpoint_create_edge( label = EDGE_GOCLASS_CONTAINS_GOCLASS, start_label = NODE_GOCLASS, start_uid = subclass, end_label = NODE_GOCLASS, end_uid = class_id, properties = { } )
                
                

