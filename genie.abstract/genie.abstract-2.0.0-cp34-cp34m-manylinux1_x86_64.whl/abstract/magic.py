import inspect
import logging
import collections

from ._magic import AbstractedModule, MagicLookup

logger = logging.getLogger(__name__)

def default_builder(tokens, *, mandatory = ()):
    '''default_builder

    A token sequence builder takes in a mandatory list of 'tokens' as specified
    by the user, and any other keyword arguments necessary, and returns the 
    abstraction lookup sequence by combining the tokens into appropriate lookup
    combinations.

    This default builder is a blend between usability and complexity, allowing
    for token dependencies and mandatory tokens. 

    Arguments
    ---------
        tokens (list): list of string tokens specified by the user, propagated
                       down from Lookup() class.
        mandatory (iterable): list/tuple of tokens that are mandatory, eg,
                              they must appear in the lookup sequence.

    Returns
    -------
        list of tuples

    Example
    -------
        >>> default_builder(['os', 'series', 'type', 'yang', 'release'],
                            mandatory =['yang'])
        [('os', 'series', 'type', 'yang', 'release'), 
         ('os', 'series', 'type', 'yang'),
         ('os', 'series', 'yang'), 
         ('os', 'yang'), 
         ('yang',)]
    '''

    # check mandatory tokens are part of tokens list
    if not set(mandatory).issubset(tokens):
        raise ValueError('mandatory tokens must be part of the overall tokens '
                         'list. Extras: %s' % (set(mandatory) - set(tokens)))

    # start with the full set of tokens
    combinations = []

    # loop through token positions in reverse order
    # (token reduction mechanism)
    for position in range(len(tokens), -1, -1):

        # create a new combination
        # (keep mandatory tokens in place)
        # (must be a tuple)
        combo = tuple(token for pos, token in enumerate(tokens) 
                               if pos < position or token in mandatory)

        # avoid duplications
        # (the above logic generate duplicates)
        if combo not in combinations:
            combinations.append(combo)

    # return all combinations
    return combinations

def get_caller_stack_pkgs(stacklvl = 1):
    '''get_caller_stack_pkgs

    helper function, returns a dictionary of names/abstraction module based on 
    the caller's stack frame. 

    Example
    -------
        >>> import genie
        >>> import mylib as local_lib
        >>> get_caller_stack_pkgs()
        {'genie': <module genie...>,
         'local_lib': <module mylib...>,}
    '''

    pkgs = {}

    # get the caller FrameInfo
    # (frame, filename, lineno, function, code_context, index) 
    frame = inspect.stack()[stacklvl][0]

    # variable scope = locals + globals
    f_scope = collections.ChainMap(frame.f_locals, frame.f_globals)

    # look for imported abstract packages
    for name, obj in f_scope.items():
        try:
            pkgs[name] = getattr(obj, '__abstract_pkg')
        except AttributeError:
            pass

    return pkgs


# global setting for default builder
DEFAULT_BUILDER = default_builder


class Lookup(MagicLookup):
    '''Lookup

    When instanciated with a set of "token requirements", the lookup object 
    allows users to dynamically reference libraries (abstraction packages).
    
    The concept is akin to dynamic imports. As opposed to 

        >>> from genie.nxos import Ospf
        >>> from local_lib.nxos.titanium import Blah

    lookup allows the user to simply do:

        >>> import genie
        >>> import local_lib
        >>> l = Lookup('nxos', 'titanium')
        >>> l.Ospf()
        >>> l.Blah()

    where the actual import based on the given tokens will be sorted out for
    the user dynamically.

    Arguments
    ---------
        *tokens (list of str): list of tokens specified for this lookup object
        builder (func): function used for creating the lookup token sequence
        packages (dict): dictionary of package names and their module object.
                         if not provided, the caller's stack is looked up for
                         all available abstraction packages.
        **builder_kwargs (kwargs): any other keyword arguments for the 
                                   sequence builder.
    
    Examples
    --------
        >>> import my_abstracted_lib as lib
        >>> l = Lookup('nxos', 'titanium')
        >>> l.lib.module_a.module_b.MyClass()
    '''

    def __init__(self, 
                 *tokens, 
                 builder = None, 
                 packages = None, 
                 **builder_kwargs):

        # lookup order builder and its kwargs
        builder = builder or DEFAULT_BUILDER

        # packages available for lookup
        # (default to collecting from caller stack)
        packages = packages or get_caller_stack_pkgs(stacklvl = 2)

        # call parent
        super().__init__(*tokens,
                         builder = builder,
                         packages = packages,
                         **builder_kwargs)
    
    @classmethod
    def from_device(cls, device, packages = None, **kwargs):
        '''from_device

        creates an abstraction Lookup object by getting the token arguments from
        a pyATS device objects.

        This api expects the device object to have an "abstraction" dictionary
        under 'custom' attribute. Eg:

        Example
        -------
            devices:
                my-device:
                    custom:
                        abstraction:
                            order: [os, serie, context]
                            os: nxos
                            serie: n7k
                            context: yang

        Arguments
        ---------
            device (Device): pyATS topology device object
            builder (func): function used for creating the lookup token sequence
            packages (dict): dictionary of package names and their module object.
                             if not provided, the caller's stack is looked up
                             for all available abstraction packages.
            **builder_kwargs (kwargs): any other keyword arguments for the 
                                       sequence builder.
        '''

        try:
            abstraction_info = device.custom['abstraction']

        except (KeyError, AttributeError):
            raise ValueError('Expected device to have custom.abstraction '
                             'definition') from None

        # get the abstraction key order
        token_order = abstraction_info['order']

        # build tokens
        tokens = []
        for token in token_order:
            try:
                token_value = abstraction_info.get(token, 
                                                   getattr(device, token))

            except (KeyError, AttributeError):
                raise ValueError('Could not find value for token {token} under '
                                 'device.custom.abstraction.{token} nor device'
                                 '.{token}'.format(token = token)) from None
            else:
                tokens.append(token_value)

        # lookup packages..
        packages = packages or get_caller_stack_pkgs(stacklvl = 2)
        
        # create lookup object
        return cls(*tokens, packages = packages, **kwargs)