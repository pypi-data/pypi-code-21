# encoding: utf-8

import attr
from resources import templates, schema


# Set the config initialisation parameters
@attr.s(frozen=True)
class _ReportConfigConstant(object):
    key = attr.ib(default=u'report_config', init=False)
    template = attr.ib(default=templates.reports, init=False)
    schema = attr.ib(default=schema.reports, init=False)


# Report config property keys
@attr.s(frozen=True)
class _ReportConfigPropertiesConstant(object):
    report_root = attr.ib(default=u'report_root', init=False)
    structure = attr.ib(default=u'structure', init=False)


# Report types
@attr.s(frozen=True)
class _ReportTypesConstant(object):
    root = attr.ib(default=u'root', init=False)
    dir = attr.ib(default=u'directory', init=False)
    file = attr.ib(default=u'file', init=False)


# Create the report constant object
@attr.s(frozen=True)
class _ReportConstant(object):
    config = attr.ib(default=_ReportConfigConstant(), init=False)
    config_properties = attr.ib(default=_ReportConfigPropertiesConstant(), init=False)
    types = attr.ib(default=_ReportTypesConstant(), init=False)
    node_template = attr.ib(default={node_type: []
                                     for _, node_type in iter(_ReportTypesConstant().__dict__.items())
                                     # There should only be one root node so we do not need a ref list for it!
                                     if node_type != _ReportTypesConstant().root}, init=False)
    node_type = attr.ib(default=u'_type', init=False)


ReportConstant = _ReportConstant()
