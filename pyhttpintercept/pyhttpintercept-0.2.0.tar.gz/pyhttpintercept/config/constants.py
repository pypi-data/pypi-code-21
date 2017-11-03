# encoding: utf-8

import attr

# Set the config initialisation parameters
REDIRECT_CONFIG = u'pyhttpintercept_redirect'
HOSTING_CONFIG = u'pyhttpintercept_hosting'
INTERCEPT_CONFIG = u'pyhttpintercept_intercept'
INTERCEPT_HANDLER_CONFIG = u'pyhttpintercept_intercept_handlers'
INTERCEPT_SCENARIO_CONFIG = u'pyhttpintercept_intercept_scenarios'
PROXY_CONFIG = u'pyhttpintercept_proxy'


@attr.s(frozen=True)
class _HostingConstant(object):
    path = attr.ib(default=u'path', init=False)
    doc_root = attr.ib(default=u'doc_root', init=False)
    description = attr.ib(default=u'description', init=False)
    active = attr.ib(default=u'active', init=False)

HostingConstant = _HostingConstant()


@attr.s(frozen=True)
class _InterceptConstant(object):
    selected_scenario = attr.ib(default=u'selected_scenario', init=False)
    modifier_paths = attr.ib(default=u'modifier_paths', init=False)
    intercept_uris = attr.ib(default=u'intercept_uris', init=False)

InterceptConstant = _InterceptConstant()


@attr.s(frozen=True)
class _InterceptKeysConstant(object):
    selected_scenario = attr.ib(default=u'{c}.{k}'.format(c=INTERCEPT_CONFIG,
                                                          k=InterceptConstant.selected_scenario),
                                init=False)
    modifier_paths = attr.ib(default=u'{c}.{k}'.format(c=INTERCEPT_CONFIG,
                                                       k=InterceptConstant.modifier_paths),
                             init=False)
    intercept_uris = attr.ib(default=u'{c}.{k}'.format(c=INTERCEPT_CONFIG,
                                                       k=InterceptConstant.intercept_uris),
                             init=False)

InterceptKeysConstant = _InterceptKeysConstant()


@attr.s(frozen=True)
class _HandlerConstant(object):
    name = attr.ib(default=u'name', init=False)
    api = attr.ib(default=u'api', init=False)
    module_root = attr.ib(default=u'module_root', init=False)
    module = attr.ib(default=u'module', init=False)

    # Loaded handler keys
    module_path = attr.ib(default=u'module_path', init=False)
    instance = attr.ib(default=u'instance', init=False)

HandlerConstant = _HandlerConstant()


@attr.s(frozen=True)
class _ScenarioConstant(object):
    name = attr.ib(default=u'name', init=False)
    description = attr.ib(default=u'description', init=False)
    modifiers = attr.ib(default=u'modifiers', init=False)

    # Loaded scenario keys
    scenario = attr.ib(default=u'scenario', init=False)

ScenarioConstant = _ScenarioConstant()


@attr.s(frozen=True)
class _ModifierConstant(object):
    # Config keys
    handler = attr.ib(default=u'handler', init=False)
    modifier = attr.ib(default=u'modifier', init=False)
    active = attr.ib(default=u'active', init=False)
    filter = attr.ib(default=u'filter', init=False)
    override = attr.ib(default=u'override', init=False)
    params = attr.ib(default=u'params', init=False)

    # Loaded modifier keys
    # --> includes handler from config keys
    modifier_name = attr.ib(default=u'modifier_name', init=False)
    modifier_path = attr.ib(default=u'modifier_path', init=False)
    module_path = attr.ib(default=u'module_path', init=False)
    module = attr.ib(default=u'module', init=False)

ModifierConstant = _ModifierConstant()


@attr.s(frozen=True)
class _HandlerTypeConstant(object):
    uri = attr.ib(default=u'uri', init=False)
    canned = attr.ib(default=u'canned', init=False)
    header = attr.ib(default=u'header', init=False)
    body = attr.ib(default=u'body', init=False)
    show = attr.ib(default=u'show', init=False)

HandlerTypeConstant = _HandlerTypeConstant()


@attr.s(frozen=True)
class _ModifierPathConstant(object):
    search_path = attr.ib(default=u'search_path', init=False)
    module_root = attr.ib(default=u'module_root', init=False)

ModifierPathConstant = _ModifierPathConstant()


# TODO: Check whether these are still required!
FILTER = u'filter'
HANDLER = u'handler'
MODIFIER = u'modifier'
SCENARIO = u'scenario'
OVERRIDE = u'override'
PARAMETERS = u'parameters'
CONFIG_NAME = u'config_name'
MODIFIER_NAME = u'modifier_name'
WSC_SCENARIO_NAME = u'config_name'
WSC_SCENARIO_DESCRIPTION = u''
