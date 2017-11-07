# encoding: utf-8

import os
import logging_helper
from fdutil.path_tools import ensure_path_exists
from ..constants import ReportConstant
from .node import ReportNode

logging = logging_helper.setup_logging()


class ReportDir(ReportNode):

    def __init__(self,
                 *args,
                 **kwargs):

        """ The ReportDir object represents a single directory in the report structure.
            The represented directory can contain more ReportDirs or Report Files (i.e HTMLReport objects).
            A report directory should also contain an index file as this will be used as the primary access
            point to the report directory.

        """

        super(ReportDir, self).__init__(*args, **kwargs)

    @property
    def node_type(self):
        return ReportConstant.types.dir

    @property
    def node_path(self):
        return os.path.join(self.parent.node_path,
                            self.name)

    def generate(self):

        # Generate this directory
        ensure_path_exists(self.node_path)

        # TODO: Generate index

        # Generate Children
        self.generate_children()
