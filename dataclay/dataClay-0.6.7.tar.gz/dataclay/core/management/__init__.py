"""Submodule for all the YAML-based management structures.

For specific information about the structures, see original Java implementation
--it is used as the authoritative implementation, available in util.management.

Note that the YAML dictionary-based fields are listed in the _fields attribute
and this is what is used on the load & dump YAML procedures.

For more information of the internal magic, see "baseclass.py" file.

BLACK MAGIC WARNING! The NAME of the module (like "contractmgr") and the NAME
of the class (like "Contract") are used in order to obtain the YAML tag, which
will (hopefully) match the Java generated name, which comes from the Java
package name (like "!!util.management.contractmgr.Contract"). This is syntactic
sugar, but should be taken into account for cross-language correctness.
"""

from collections import namedtuple
from yaml import Loader

from .classmgr import (AccessedImplementation, AccessedProperty, Implementation,
                       MetaClass, Operation, Property, Type, UserType)
from .classmgr.java import JavaImplementation
from .classmgr.python import PythonImplementation, PythonClassInfo
from .accountmgr import Account
from .contractmgr import Contract
from .datacontractmgr import DataContract
from .datasetmgr import DataSet
from .namespacemgr import Namespace
from .interfacemgr import Interface
from .stubs import ImplementationStubInfo, PropertyStubInfo, StubInfo
from .metadataservice import StorageLocation, MetaDataInfo, ExecutionEnvironment
from .sessionmgr import *

# Initialize (internal) representer/constructor for UUID
import _uuid
# and also all the ignores (literal maps)
from ignores import IGNORE_CLASSES, IGNORE_PREFIXES
from dataclay.core.constants import lang_codes

__all__ = [
    "AccessedImplementation", "AccessedProperty", "Implementation", "MetaClass",
    "Operation", "Property", "Type", "UserType", "JavaImplementation",
    "PythonImplementation", "PythonClassInfo", "Account", "Contract",
    "DataContract", "DataSet", "Namespace", "Interface", "ImplementationStubInfo",
    "PropertyStubInfo", "StubInfo", "StorageLocation", "SessionInfo", "SessionContract",
    "SessionOperation", "SessionInterface", "SessionImplementation", "SessionDataContract",
    "SessionProperty", "MetaDataInfo", "ExecutionEnvironment"
]


def trivial_constructor(loader, node):
    """Constructor used to "ignore" certain types.

    The behaviour is always to build a mapping. This is a harmless behaviour
    (at least, is expected to be). dataClay uses this for all want-to-ignore
    types, without losing semantics. If problems arise from this, this method
    could avoid them by returning None.

    For aesthetic reasons, a namedtuple instance is returned (which will be
    built tailored to the input, which may or may not be an expected behaviour)
    and its name will be used from the tag.
    """
    name = node.tag.rsplit(".", 1)[-1]
    contents = loader.construct_mapping(node)
    return namedtuple(name, contents.keys())(**contents)


def tuple_constructor(loader, node):
    """Java's Tuple is a simple two-element python tuple."""
    d = loader.construct_mapping(node)
    return d["first"], d["second"]


def lang_constructor(loader, node):
    """Language (Java enum) is parsed as a String."""
    s = loader.construct_scalar(node)
    return getattr(lang_codes, s)


def feature_constructor(loader, node):
    """Feature (Java enum) is parsed as a String."""
    s = loader.construct_scalar(node)
    # Ugly hack, but we do not need the value at all
    return hash(s)


def lonely_equal_constructor(loader, node):
    """Solve/monkey-patch a very old bug.
    https://bitbucket.org/xi/pyyaml/issues/49/plain-equal-sign-as-node-content-results
    """
    s = loader.construct_scalar(node)
    return s


Loader.add_constructor(u"tag:yaml.org,2002:value", lonely_equal_constructor)

# The tuple is a bit special itself
Loader.add_constructor(u"tag:yaml.org,2002:util.structs.Tuple", tuple_constructor)

# The SupportedLanguages is very special
Loader.add_constructor(u"tag:yaml.org,2002:util.language.SupportedLanguages$Langs", lang_constructor)

# Not needed for Python, but nice to avoid errors
Loader.add_constructor(u"tag:yaml.org,2002:util.management.classmgr.features.Feature$FeatureType",
                       feature_constructor)

for prefix in IGNORE_PREFIXES:
    yaml_tag_prefix = u"tag:yaml.org,2002:%s" % prefix
    Loader.add_multi_constructor(
        yaml_tag_prefix,
        # The following is used to disregard the tag
        lambda loader, _, node: trivial_constructor(loader, node))

for class_tag in IGNORE_CLASSES:
    yaml_class_tag = u"tag:yaml.org,2002:%s" % class_tag
    Loader.add_constructor(yaml_class_tag, trivial_constructor)
