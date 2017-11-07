# encoding: utf-8

import os
import logging_helper
from dominate import tags
from fdutil.html import (write_to_html,
                         generate_html_document,
                         CSS_DIV_ID)
from ..constants import ReportConstant
from .node import ReportNode

logging = logging_helper.setup_logging()


class HTMLReport(ReportNode):

    def __init__(self,
                 *args,
                 **kwargs):

        super(HTMLReport, self).__init__(*args, **kwargs)

        self._report_objects = []

    @property
    def node_type(self):
        return ReportConstant.types.file

    @property
    def node_path(self):
        return os.path.join(self.parent.node_path,
                            self.filename)

    @property
    def filename(self):
        return self.name

    def generate(self):

        if len(self._report_objects) > 0:
            doc = generate_html_document(title=self.name)

            with doc:
                for obj in self._report_objects:
                    obj.html()

                    # Add any extra CSS from object
                    # TODO: Is this the best method?
                    # TODO: de-dupe css from multiple of the same object?
                    css = getattr(obj, u'CSS', False)
                    inline_css = getattr(obj, u'INLINE_CSS', False)

                    if css or inline_css:
                        css_div = doc.getElementById(CSS_DIV_ID)

                        if css:
                            for c in css:
                                css_div.add(tags.style(c))

                        if inline_css:
                            for c in inline_css:
                                css_div.add(tags.style(c))

            write_to_html(html_document=doc,
                          filename=self.filename,
                          html_folder=self.parent.node_path)

    def add(self,
            obj):

        # Ensure object has an html method
        getattr(obj, u'html')  # Raises AttributeError if no html attribute exists

        # Ensure html attribute is a callable method
        if not callable(obj.html):
            raise TypeError(u'Object being added to report does not have a callable html method!')

        # Add object to list of objects to be drawn in the report
        self._report_objects.append(obj)
