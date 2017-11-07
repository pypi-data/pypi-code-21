"""
Class for reflecting upon
"""
from typing import List, Callable, Union, Dict
from typing import Optional

from mhelper import string_helper


class ICode:
    """
    Interface for code object (for Intellisense only)
    """
    def __init__( self ):
        self.__class__ = None
        self.__delattr__ = None
        self.__dir__ = None
        self.__doc__ = None
        self.__eq__ = None
        self.__format__ = None
        self.__ge__ = None
        self.__getattribute__ = None
        self.__gt__ = None
        self.__hash__ = None
        self.__init__ = None
        self.__le__ = None
        self.__lt__ = None
        self.__ne__ = None
        self.__new__ = None
        self.__reduce__ = None
        self.__reduce_ex__ = None
        self.__repr__ = None
        self.__setattr__ = None
        self.__sizeof__ = None
        self.__str__ = None
        self.__subclasshook__ = None
        self.co_argcount = None
        self.co_cellvars = None
        self.co_code = None
        self.co_consts = None
        self.co_filename = None
        self.co_firstlineno = None
        self.co_flags = None
        self.co_freevars = None
        self.co_kwonlyargcount = None
        self.co_lnotab = None
        self.co_name = None
        self.co_names = None
        self.co_nlocals = None
        self.co_stacksize = None
        self.co_varnames = None
        raise NotImplementedError( "type hinting only - not intended for construction" )


class IFunctionBase:
    """
    Interface for function object (for Intellisense only)
    """
    def __init__( self ):
        self.__annotations__ = None
        self.__call__ = None
        self.__class__ = None
        self.__closure__ = None
        self.__code__ = ICode( )
        self.__defaults__ = None
        self.__delattr__ = None
        self.__dict__ = None
        self.__dir__ = None
        self.__doc__ = None
        self.__eq__ = None
        self.__format__ = None
        self.__ge__ = None
        self.__get__ = None
        self.__getattribute__ = None
        self.__globals__ = None
        self.__gt__ = None
        self.__hash__ = None
        self.__init__ = None
        self.__kwdefaults__ = None
        self.__le__ = None
        self.__lt__ = None
        self.__module__ = None
        self.__name__ = None
        self.__ne__ = None
        self.__new__ = None
        self.__qualname__ = None
        self.__reduce__ = None
        self.__reduce_ex__ = None
        self.__repr__ = None
        self.__setattr__ = None
        self.__sizeof__ = None
        self.__str__ = None
        self.__subclasshook__ = None
        raise NotImplementedError( "type hinting only - not intended for construction" )


IFunction = Union[ IFunctionBase, Callable ]


class FnArg:
    """
    Function argument details
    """
    def __init__( self, name: str, type_: Optional[ type ], desc: Optional[ str ], default: Optional[ object ] ):
        self.name = name
        self.type = type_
        self.description = desc
        self.default = default


class NoDefaultType:
    """
    Type of `NOT_PROVIDED` constant. Used to distinguish a value of `None` and one that isn't provided.
    """
    def __str__(self) -> str:
        return "(mandatory)"


NOT_PROVIDED = NoDefaultType( )
"""
NOT_PROVIDED is used to distinguish between a value of `None` and a value that that isn't even provided.

As a parameter default, it can be considered to mean "mandatory".
When passed as a parameter's value, it can be considered to mean "I'm not specifying this, use your default (or raise an Exception if there is no default)."
"""


class FnInspect:
    """
    CLass for inspecting a function.
    """
    def __init__( self, fn: IFunction):
        self.function = fn  #type: IFunction
        
        self.name = fn.__name__  # type: str
        self.args = [ ]  # type: List[FnArg]
        
        arg_names = fn.__code__.co_varnames[ :fn.__code__.co_argcount ]
        
        arg_types = { }

        self.return_type = None
        
        for k, v in fn.__annotations__.items( ):
            if k != "return":
                arg_types[ k ] = v
            else:
                self.return_type = v
        
        doc = fn.__doc__  # type:str

        arg_descriptions = extract_documentation( doc, "param", False )
        
        arg_defaults = { }
        has_args = (fn.__code__.co_flags & 0x4) == 0x4
        has_kwargs = (fn.__code__.co_flags & 0x8) == 0x8
        
        if fn.__defaults__:
            num_defaults = len( fn.__defaults__ )
            default_offset = len( arg_names ) - num_defaults
            
            if has_args:
                default_offset -= 1
            
            if has_kwargs:
                default_offset -= 1
            
            for i, v in enumerate( fn.__defaults__ ):
                name = arg_names[ default_offset + i ]
                arg_defaults[ name ] = v
        
        for arg_name in arg_names:
            arg_desc_list = arg_descriptions.get( arg_name, None )
            arg_desc = "\n".join( arg_desc_list ) if arg_desc_list else ""
            arg_desc = string_helper.fix_indents(arg_desc)
            arg_type = arg_types.get( arg_name, None )
            arg_default = arg_defaults.get( arg_name, NOT_PROVIDED )
            
            if arg_type is None and arg_default is not NOT_PROVIDED and arg_default is not None:
                arg_type = type(arg_default) 
            
            self.args.append( FnArg( arg_name, arg_type, arg_desc, arg_default ) )
        
        fn_desc = "\n".join(arg_descriptions[ "" ])
        fn_desc = string_helper.fix_indents(fn_desc)
        
        self.description = fn_desc
        
    def __str__(self):
        return str(self.function)
        

    def call( self, *args, **kwargs ):
        """
        Calls the function.
        """
        # noinspection PyCallingNonCallable
        return self.function( *args, **kwargs )

def extract_documentation( doc, param_keyword = "param", as_string = True ) -> Union[Dict[str, str], Dict[str, List[str]]]:
    """
    Extracts the documentation into a dictionary
    :param doc:             Documentation string
    :param param_keyword:   Keyword to use for parameters, e.g. "param" 
    :param as_string:       `True`: Return each entry as a `str` with "\n" for or newline
                            `False`: Return each entry as a `list` with a `str` on each line.
                            
    :return:                Dictionary of argument name vs. documentation. The primary documentation is under the param name `""`.
    """
    arg_descriptions = {}
    
    param_keyword = ":{} ".format( param_keyword )
    current_desc = []
    arg_descriptions[""] = current_desc
    current_indent = -1
    if doc is not None:
        for line in doc.split( "\n" ):
            if line.lstrip().startswith( param_keyword ):
                line = line.replace( param_keyword, " " * len( param_keyword ) )
                name = line.split( ":", 1 )[ 0 ]
                line = line.replace( name, " " * len( name ), 1 )
                line = line.replace( ":", " ", 1 )
                current_indent = string_helper.get_indent( line )
                current_name = name.strip()
                current_desc = [ string_helper.remove_indent( current_indent, line ) ]
                arg_descriptions[ current_name ] = current_desc
            elif not line.lstrip().startswith( ":" ):
                if current_indent == -1:
                    current_indent = string_helper.get_indent( line )
            
                current_desc.append( string_helper.remove_indent( current_indent, line ) )
            else:
                current_desc = [ ]
    
    if as_string:
        for k in list(arg_descriptions.keys()):
            arg_descriptions[k] = "\n".join(arg_descriptions[k]).strip()
                
    return arg_descriptions