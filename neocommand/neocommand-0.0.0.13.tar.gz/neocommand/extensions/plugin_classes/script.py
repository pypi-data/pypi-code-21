"""
Contains the `ScriptPlugin` class, an extension of the `intermake` package's Plugin that represents re-usable Cypher scripts.

The `ScriptPlugin` itself is ideally constructed through the `Script` convenience function.
"""
import inspect
from typing import Dict, List, Optional
from uuid import uuid4

from intermake import ArgsKwargs, EThread, MCMD, NOT_PROVIDED, OUVisibility, Plugin, PluginArg, PluginArgValue, PluginArgValueCollection, VisibilityClass
from mhelper import array_helper, override, sealed, string_helper, AnnotationInspector, MAnnotationFactory
from neocommand.data import constants
from neocommand.database.endpoints import IEndpoint, ECHOING_ENDPOINT


__author__ = "Martin Rusilowicz"


HDbParam = MAnnotationFactory( "DBParam" )
HScriptParam = MAnnotationFactory( "HScriptParam" )


TScriptTypes = "Union[ Type[ HDbParam ], Type[ HScriptParam ] ]"
TScriptParam = "Union[ TScriptTypes, Tuple[ TScriptTypes, object ] ]"


# noinspection PyUnusedLocal
def Script( *,
            cypher: str,
            name: str = None,
            description: Optional[str] = None,
            timeout = None,
            retries = None,
            visibility = None,
            arguments: Dict[str, TScriptParam] = None ) -> "ScriptPlugin":
    """
     Creates a ScriptPlugin. All parameters apart from _script are optional.
     The parameters begin with underscores to separate them from the script parameters - kwargs.
     
     Parameters and replacements should be passed as tuples of types and defaults, or just types.

        :param visibility:         Inherited 
        :param cypher:             The script template itself (str, use "<XXX> for arguments - see kwargs)
        :param name:               Name of the script (str, None)
        :param description:        Description of what the script does (str, None)
        :param timeout:            Timeout period for query (0 for no timeout, default is 0)
        :param retries:            Number of retries after query timeout (0 for no reties, default is infinite).
        :param arguments:          Script arguments.
    """
    
    # Description
    description = inspect.cleandoc( description ) if description else ""
    
    cypher = string_helper.strip_lines( cypher )
    description += "\n\n" + cypher
    
    # Args
    args = []
    
    if arguments:
        for arg_name, arg_info in arguments.items():
            if arg_name in ("timeout", "retries"):
                raise ValueError( "Legacy script parameter. Please remove." )
            
            if arg_info is not None:
                arg_info = array_helper.as_sequence( arg_info )
                arg_annotation = AnnotationInspector( arg_info[0] )
                arg_default = arg_info[1] if len( arg_info ) > 1 else NOT_PROVIDED
                arg_description = arg_info[2] if len( arg_info ) > 2 else "Script parameter"
                
                if arg_annotation.is_mannotation_of( HDbParam ) and not arg_annotation.is_mannotation_of( HScriptParam ):
                    raise ValueError( "The type of argument «{}» on the script «{}» is a «{}», not a <HDbParam> or <HScriptParam>.".format( arg_name, name, arg_annotation ) )
                
                args.append( PluginArg( arg_name, arg_annotation, arg_default, arg_description ) )
    
    # Special arguments for scripts:
    if timeout is None:
        timeout = 0
    
    if retries is None:
        retries = 1000
    
    plugin = ScriptPlugin( cypher = cypher,
                           name = name,
                           description = description,
                           args = args,
                           visibility = visibility,
                           timeout = timeout,
                           retries = retries )
    
    return plugin


SCRIPT_VISIBILITY = VisibilityClass( name = "scripts",
                                     default = False,
                                     comment = "Cypher scriptlets" )


class ScriptPlugin( Plugin ):
    """
    Wraps text with replaceable parameters up with some error checking

    These "parameters" are just text and should represent constants as far as the database is concerned.
    They should not be confused with, or used as a substitute for, database query parameters.
    """
    
    
    def __init__( self,
                  cypher: str,
                  name: str,
                  description: str,
                  args: List[PluginArg],
                  visibility: OUVisibility,
                  timeout: int,
                  retries: int ):
        """
        CONSTRUCTOR
        See Script() for argument descriptions.
        """
        assert cypher is not None, "A script plugin «{0}» needs some code.".format( name )
        
        arg_list = { }
        
        if name is None:
            name = "untitled.script.{}".format( uuid4() )
            
            if description is None:
                description = "Internal script not intended for user access."
        
        super().__init__( names = name,
                          description = description,
                          type_name = constants.PLUGIN_TYPE_SCRIPT,
                          threading = EThread.SINGLE,
                          visibility = visibility )
        
        # Arguments
        for x in args:
            super()._add_argument( x )
            arg_list[x.name] = x
        
        # Suck in arguments from arguments that are themselves Scripts
        to_add = []
        
        for arg in self.args:
            dv = arg.default
            
            if isinstance( dv, ScriptPlugin ):
                for v in dv.args:  # type: PluginArg
                    if not v.name in arg_list:
                        to_add.append( v )
        
        for v in to_add:
            self._add_argument( v )
            arg_list[v.name] = v
        
        from neocommand.database.endpoints import DbEndpoint
        self.__arg_database = super()._add_arg( "database", Optional[DbEndpoint], None, "Database to use. If this is `None` a reasonable default will be assumed." )
        self.__arg_output = super()._add_arg( "output", IEndpoint, ECHOING_ENDPOINT, "Where to send received data." )
        self.__arg_timeout = super()._add_arg( "timeout", int, timeout, "Parameter available to all scripts. Query timeout in seconds, use zero for no timeout." )
        self.__arg_retries = super()._add_arg( "retries", int, retries, "Parameter available to all scripts. Number of retries after timeouts before the query is considered a failure" )
        self.__arg_quiet = super()._add_arg( "quiet", bool, False, "Don't display results in terminal." )
        
        self._script = cypher
        
        if "limit" in arg_list:
            self.__arg_limit = arg_list["limit"]
        
        # MODE_BATCH scripts are really just MODE_ITERATIVE scripts
        # but we must auto-create some additional details
        
        # Extra args
        self.arg_dump = super()._add_arg( "_dump", bool, False, "Dump the script's code to standard output instead of running it." )
    
    
    def new_default_args( self,
                          **kwargs ) -> List[PluginArg]:
        new_args = []
        
        for arg in self.args:
            if arg.name in kwargs:
                default = kwargs[arg.name]
            else:
                default = arg.default
            
            new_args.append( PluginArg( arg.name, arg.annotation.value, default, arg.description ) )
        
        return new_args
    
    
    @override
    @sealed
    def virtual_run( self ) -> Optional[object]:
        """
        IMPLEMENTATION
        The meaty bit
        """
        
        #
        # GET ARGUMENTS
        #
        arg_dump = self.arg_dump.get_value()
        arg_database = self.__arg_database.get_value()
        arg_timeout = self.__arg_timeout.get_value()
        arg_retries = self.__arg_retries.get_value()
        arg_output = self.__arg_output.get_value()
        arg_quiet = self.__arg_quiet.get_value()
        
        if arg_database is None:
            from neocommand.data.core import CORE
            arg_database = CORE.endpoint_manager.get_database_endpoint()
        
        #
        # GET CODE
        #
        cypher = self.create( MCMD.args )
        
        cypher_params = { }
        
        for a in MCMD.args:
            if a.annotation.is_mannotation_of( HDbParam ):
                cypher_params[a.name] = a
        
        #
        # SPECIAL CASE FOR CYPHER DUMP
        #
        if arg_dump:
            MCMD.print( cypher )
            
            for k, v in cypher_params.items():
                MCMD.print( "{} = {}".format( k, v ) )
            
            return None
        
        #
        # RUN THE SCRIPT!
        #
        with arg_database.get_database() as db:
            result = db.run_cypher( title = self.name,
                                    cypher = cypher,
                                    parameters = cypher_params,
                                    time_out = arg_timeout,
                                    retry_count = arg_retries,
                                    output = arg_output )
            
            if not arg_quiet:
                MCMD.information( result )
            
            return result
    
    
    def plain_text( self ):
        return self._script
    
    
    def check_holds_true( self, condition, message = "" ) -> None:
        if not condition:
            raise ValueError( "There is an error in the script \"" + self.name + "\". " + message + "." )
    
    
    @property
    def estimator( self ) -> "Optional[Script]":
        """

        :return:
        """
        return self._estimator
    
    
    def create( self, 
                args: Optional[PluginArgValueCollection] = None,
                ignore_missing: bool = False ) -> str:
        """
        Generates the text from this script object, parameters may be specified at this time
        Any parameters left unfilled will cause an error!
        """
        if args is None:
            args = PluginArgValueCollection( self, ArgsKwargs(  ) )  # Just use the defaults
        
        return self._create_from( self._script, args, ignore_missing )
    
    
    @staticmethod
    def _create_from( statement : str,
                      args: PluginArgValueCollection, 
                      ignore_missing: bool ) -> str:
        """
        Logic behind create().
        """
        
        for arg in args:  # type: PluginArgValue
            key = "<" + arg.name.upper() + ">"
            
            # Assert parameter exists
            if not arg.is_set:
                if ignore_missing:
                    value = "{????}"
                else:
                    raise ValueError( "The parameter «{0}» of type «{1}» has not been provided.".format( arg.name, arg.annotation ) )
            else:
                value = arg.value
            
            # Scripts can reference other scripts
            if isinstance( value, ScriptPlugin ):
                new_dict = { }
                
                for arg2 in args:
                    if arg2.name in [x.name for x in value.args]:
                        new_dict[arg2.name] = arg2.value
                
                value = value.create( args, ignore_missing )  # parameters get passed along
            
            statement = statement.replace( key, str( value ) )
        
        return statement
