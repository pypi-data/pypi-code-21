import os
import re

import pystache

import fizzgun.util
from fizzgun.application.service_contexts import ReporterContext
from fizzgun.core.common import Worker


class Reporter(Worker):

    def initialize(self, report_config=None):
        self._report_dir = report_config['directory'] if report_config else './reports'
        format = report_config['format'] if report_config else 'txt'
        self._formatter = Formatter.formatter_for(format)
        self.reporter_context.file_system.create_directory(self._report_dir)

    def process(self, work):
        rep_path = os.path.join(self._report_dir, "%s.%s" % (self._extract_session_id(work),
                                                             self._formatter.extension))

        self.reporter_context.file_system.append_to_file(rep_path, self._formatter.format(work))
        return self.NO_RESULT

    @property
    def reporter_context(self) -> ReporterContext:
        return self.service_context

    @classmethod
    def _extract_session_id(cls, work):
        session_id = work.get('session_id', 'global-session')
        session_id = session_id or "global-session"

        # Avoid path traversal
        session_id = re.sub('[^a-zA-Z0-9_\-]', '', session_id) or 'global-session'
        return session_id


class Formatter(object):

    @classmethod
    def formatter_for(cls, format):
        if format == 'html':
            return HTMLFormatter()
        else:
            return TXTFormatter()

    @property
    def extension(self):
        raise NotImplementedError("property 'extension' must be implemented in %s" % self.__class__.__name__)

    def format(self, work):
        raise NotImplementedError("method 'format' must be implemented in %s" % self.__class__.__name__)


class PystacheFormatter(Formatter):

    def __init__(self):
        self._renderer = pystache.Renderer()

    @property
    def template(self):
        raise NotImplementedError("property 'template' must be implemented in %s" % self.__class__.__name__)

    def format(self, work):
        for entity in ['original', 'modified', 'response']:
            work[entity]['headers'] = list({'name': h[0], 'value': h[1]}
                                           for h in work[entity]['headers'])

        return self._renderer.render_path(fizzgun.util.tpl(self.template), {
            'bubble_name': work['bubble']['name'],
            'bubble_description': work['bubble']['description'],
            'errors': work['errors'],
            'original_request': work['original'],
            'modified_request': work['modified'],
            'server_response': work['response']
        })


class TXTFormatter(PystacheFormatter):

    @property
    def extension(self):
        return 'txt'

    @property
    def template(self):
        return 'txt_report_entry'


class HTMLFormatter(PystacheFormatter):

    @property
    def extension(self):
        return 'html'

    @property
    def template(self):
        return 'html_report_entry'
