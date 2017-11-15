"""ReST extensions"""

from pkg_resources import Requirement, resource_filename, resource_exists
import tempfile
import urllib2

from docutils.parsers.rst.directives import misc, register_directive


class PkgResourcesInclude(misc.Include):
    """Implement the `pkg-resources-include` directive, similar to the `include`
    directive but taking a pypi project name as first argument and a data file
    within the package as second argument.

    Actual file location will be computed using pkg_resources facilities.

    Example:

        .. pkg-resources-include:: cubicweb-seda doc/profils.rst

    """

    required_arguments = 2

    def run(self):
        project, fpath = self.arguments

        if not resource_exists(Requirement.parse(project), fpath):
            raise Exception('Resource %s not found in %s' % (fpath, project))

        filename = resource_filename(Requirement.parse(project), fpath)
        self.arguments = [filename]
        return super(PkgResourcesInclude, self).run()


register_directive('pkg-resources-include', PkgResourcesInclude)


class IncludeURL(misc.Include):
    """Implement the `include-url` directive, similar to the `include`
    directive but taking an URL as argument.

    Example:

        .. include-url:: https://framagit.org/saemproject/saem-client/raw/master/README.rst
    """

    def run(self):
        url, = self.arguments

        input_stream = urllib2.urlopen(url)
        with tempfile.NamedTemporaryFile() as output_stream:
            output_stream.write(input_stream.read())
            output_stream.flush()
            self.arguments = [output_stream.name]
            return super(IncludeURL, self).run()


register_directive('include-url', IncludeURL)
