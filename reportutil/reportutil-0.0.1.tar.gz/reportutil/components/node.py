# encoding: utf-8

import logging_helper
from copy import deepcopy
from abc import ABCMeta, abstractmethod, abstractproperty
from configurationutil import (Configuration,
                               cfg_params)
from .._metadata import __version__, __authorshort__, __module_name__
from ..constants import ReportConstant

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__


def _register_report_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=ReportConstant.config.key,
                 config_type=cfg_params.CONST.json,
                 template=ReportConstant.config.template,
                 schema=ReportConstant.config.schema)

    return cfg


class ReportNode(object):

    __metaclass__ = ABCMeta

    def __init__(self,
                 parent=None,
                 key=None,  # None for root node
                 *args,
                 **kwargs):

        """ Report base class """

        self.parent = parent
        self._name = key

        _node_root = u'{cfg}.{key}'.format(cfg=ReportConstant.config.key,
                                           key=ReportConstant.config_properties.structure)

        self.parent_key = _node_root if self.parent is None else self.parent.node_key
        self.node_key = u'{root}.{node}'.format(root=self.parent_key,
                                                node=key) if key is not None else _node_root

        self._cfg = _register_report_config()

        # Setup structure for this node
        try:
            # Check whether node registered
            node = self._cfg[self.node_key]
            assert self.node_type == node[ReportConstant.node_type]

        except KeyError:
            # If not registered register node
            self._cfg[self.node_key] = {
                ReportConstant.node_type: self.node_type
            }

        except AssertionError:
            raise TypeError(u'Existing definition does not match node definition! '
                            u'{exist} != {new}'.format(exist=self.node_type,
                                                       new=self._cfg[self.node_key][ReportConstant.node_type]))

        # Initialise child tracking object
        self._child_nodes = deepcopy(ReportConstant.node_template)

    @abstractproperty
    def node_type(self):

        """ Return one of ReportConstant.types """

        pass

    @abstractproperty
    def node_path(self):

        """ Fully qualified path to this node """

        pass

    @abstractmethod
    def generate(self):

        """ Generates the report, creating the directory structure and files that make up this report node.

        :return: path to report node index file.
        """

        pass

    @property
    def name(self):
        return self._name

    @property
    def children(self):
        return self._child_nodes

    @property
    def child_dirs(self):
        return self.children.get(ReportConstant.types.dir, [])

    @property
    def child_files(self):
        return self.children.get(ReportConstant.types.file, [])

    def add_node(self,
                 key,
                 node_class,
                 *args,
                 **kwargs):

        if self.node_type == ReportConstant.types.file:
            raise TypeError(u'Cannot call add_node method on file nodes!')

        # We create the node no matter what as we need it instantiated to check the type.
        obj = node_class(parent=self,
                         key=key,
                         *args,
                         **kwargs)

        matches = [node for node in self._child_nodes[obj.node_type] if node.node_key == obj.node_key]

        if bool(matches):
            raise KeyError(u'Node ({node}) already registered'.format(node=obj.node_key))

        else:
            self._child_nodes[obj.node_type].append(obj)

        return obj

    def get_node(self,
                 name):

        if self.node_type == ReportConstant.types.file:
            raise TypeError(u'Cannot call get_node method on file nodes!')

        # TODO: Retrieve and return the requested report node object
        raise NotImplementedError(u'get_node method not written yet!')

    def generate_children(self):

        """ Invokes the generate methods on all children. """

        for d in self.child_dirs:
            d.generate()

        for f in self.child_files:
            f.generate()
