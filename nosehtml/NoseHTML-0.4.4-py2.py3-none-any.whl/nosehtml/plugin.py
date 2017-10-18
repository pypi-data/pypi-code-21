from __future__ import print_function

import cgi
import errno
import io
import os
import sys
import traceback

from nose.plugins.base import Plugin


def unicodify(value):
    """
    Given a string, returns a Unicode string.
    """
    if value is None:
        return None
    if sys.version_info[0] == 2 and not isinstance(value, unicode):
        value = unicode(value, 'utf-8', 'replace')
    return value


class LogFile(object):
    def __init__(self, file, counter):
        self.file = file
        self.counter = counter


class NoseHTML(Plugin):
    """
    Styled HTML output plugin for nose.
    """

    def help(self):
        return "Output HTML report of test status into reportfile (specifiable with --html-report-file)"

    def add_options(self, parser, env=os.environ):
        Plugin.add_options(self, parser, env)
        parser.add_option("--html-report-file", action="store", default="nose_report.html", dest="report_file", help="File to output HTML report to")
        parser.add_option("--html-error-file", action="store", default="/dev/null", dest="error_file", help="File to output HTML error report to")

    def configure(self, options, config):
        Plugin.configure(self, options, config)
        self.conf = config
        self.report_fname = options.report_file
        self.error_fname = options.error_file

    def begin(self):
        self.reportlog = LogFile(io.open(self.report_fname, "w", encoding='utf-8'), 0)
        self.errorlog = LogFile(io.open(self.error_fname, "w", encoding='utf-8'), 0)
        for f in (self.reportlog.file, self.errorlog.file):
            print(HTML_START, file=f)
            f.flush()

    def finalize(self, result):
        for f in (self.reportlog.file, self.errorlog.file):
            print(HTML_END, file=f)
            # When run via buildbot on NFS on Solaris, this close() will encounter
            # the NFS bug described in OpenSolaris bug ID #6708290.  So we work
            # around that bug.
            try:
                f.close()
            except IOError as e:
                if e.errno != errno.EINVAL:
                    raise

    def print_test(self, status, test, error=None):
        fs = [self.reportlog]
        if error:
            fs.append(self.errorlog)
        for f in fs:
            f.counter += 1
            print(u"<div class='test %s'>" % unicodify(status), file=f.file)
            if test.id():
                print(u"<div><span class='label'>ID:</span> %s</div>" % unicodify(test.id()), file=f.file)
            if test.shortDescription():
                print(u"<div><span class='label'>Description:</span> %s</div>" % unicodify(test.shortDescription()), file=f.file)
            if status:
                print(u"<div><span class='label'>Status:</span> %s</div>" % unicodify(status), file=f.file)
            if test.capturedOutput:
                print(u"<div><span class='label'>Output:</span> <a href=\"javascript:toggle('capture_%d')\">...</a></div>" % f.counter, file=f.file)
                print(u"<div id='capture_%d' style='display: none'><pre class='capture'>%s</pre></div>" % (f.counter, unicodify(cgi.escape(test.capturedOutput))), file=f.file)
            if hasattr(test, 'capturedLogging') and test.capturedLogging:
                print(u"<div><span class='label'>Log:</span> <a href=\"javascript:toggle('log_%d')\">...</a></div>" % f.counter, file=f.file)
                print(u"<div id='log_%d' style='display: none'><pre class='log'>%s</pre></div>" % (f.counter, unicodify(cgi.escape("\n".join(test.capturedLogging)))), file=f.file)
            if error:
                print(u"<div><span class='label'>Exception:</span> <a href=\"javascript:toggle('exception_%d')\">...</a></div>" % f.counter, file=f.file)
                print(u"<div id='exception_%d' style='display: none'><pre class='exception'>%s</pre></div>" % (f.counter, unicodify(cgi.escape(error))), file=f.file)
            print(u"</div>", file=f.file)
            f.file.flush()

    def addSkip(self, test):
        """
        Test was skipped
        """
        self.print_test('skipped', test)

    def addSuccess(self, test):
        """
        Test was successful
        """
        self.print_test('success', test)

    def addFailure(self, test, error):
        """
        Test failed
        """
        self.print_test('failure', test, '\n'.join(traceback.format_exception(*error)))

    def addError(self, test, error):
        """
        Test errored.
        """
        self.print_test('error', test, '\n'.join(traceback.format_exception(*error)))

    def addDeprecated(self, test):
        """
        Test is deprecated
        """
        self.print_test('deprecated', test)


HTML_START = u"""
<html>
<head>
<style>

body
{
  font: 12px verdana, "Bitstream Vera Sans", geneva, arial, helvetica, helve, sans-serif;
  line-height: 160%;
}

div.test
{
  margin: 5px;
  padding: 5px;
  border: solid black 1px;
  background: lightgray;
}

div.success
{
  background: #CCFFCC;
  border: solid #66AA66 1px;
}

div.error, div.failure
{
  background: #FFCCCC;
  border: solid #AA6666 1px;
}

span.label
{
  font-weight: bold;
}

pre
{
  background: white;
  padding: 5px;
  border:  solid black 1px;
  display: block;
  overflow: auto;
}
</style>

<script>
function toggle(name){
    var elem = document.getElementById(name)
    if (elem) {
        if (elem.style.display=="none"){
            elem.style.display="block"
        } else {
            elem.style.display="none"
        }
    }
}
</script>
</head>
<body>
"""

HTML_END = u"""
</body>
</html>
"""
