from .block_meta import BlockConfig
from .exceptions import aslist, SemanticError
from .visualization import semantic_warning


__all__ = ['resolve_config']

def resolve_config(list_of_config, given_config, block, STRICT=True):
    '''
        Checks that the configuration passed is coherent with the definition.
        Returns a dictionary with the values to use.
    
        If STRICT is True, throws an error if we pass some configuration
        that was not properly defined in list_of_config.
    
        list_of_config: list of BlockConfig instances
    '''

    for c in list_of_config:
        assert isinstance(c, BlockConfig)

    # First we get the names of the required config variables.
    defined_variables = set([x.variable for x in list_of_config])
    required_variables = set([x.variable for x in list_of_config
                              if not x.has_default])
    passed_variables = set(given_config.keys())
    required_not_passed = required_variables.difference(passed_variables)
    passed_not_defined = passed_variables.difference(defined_variables)

    if required_not_passed:
        msg = ('Some required config (%r) was not passed.' %
                aslist(required_not_passed))
        raise SemanticError(msg, block)

    if passed_not_defined:
        msg = ('We were passed some config variable(s) (%r) which was not '
               'defined formally '
               'as a config variable.\nThe defined ones are: %s.' %
               (aslist(passed_not_defined), aslist(defined_variables)))
        if STRICT:
            raise SemanticError(msg, block)
        else:
            semantic_warning(msg, block)

    result = {}
    for x in list_of_config:
        if x.has_default:
            result[x.variable] = x.default
    for key, val in given_config.items():
        result[key] = val

    return result


