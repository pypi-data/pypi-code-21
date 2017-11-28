"""
    Sphinx Extension lilypond
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Allow Lilypond music notes to be included in Sphinx-generated documents
    inline and outline.

    :copyright: Copyright © 2017 by Fabrice Salvaire.
    :copyright: Copyright © 2009 by Wei-Wei Guo.
    :license: BSD, see LICENSE for details.

    The extension is modified from mathbase.py and pngmath.py by Sphinx team.

    Note: The extension has only very basic support for LaTeX builder.
"""

####################################################################################################

from hashlib import sha1 as sha
from subprocess import Popen, PIPE
import logging
import os
import shutil
import tempfile

from docutils import nodes, utils
from docutils.parsers.rst import directives

from sphinx.errors import SphinxError
from sphinx.util import ensuredir
from sphinx.util.compat import Directive

####################################################################################################

_logger = logging.getLogger(__name__)

####################################################################################################

DOCUMENT_BEGIN = r'''
\paper{
  indent=0\mm
  line-width=120\mm
  oddFooterMarkup=##f
  oddHeaderMarkup=##f
  bookTitleMarkup=##f
  scoreTitleMarkup=##f
}
'''

INLINE_BEGIN = r'''
\markup \abs-fontsize #{} {{
'''

# INLINE_BEGIN = r'''
# \markup \abs-fontsize #{} { \musicglyph
# '''

INLINE_END = r'''
}
'''

DIRECTIVE_BEGIN = r'''
\new Score \with {{
  fontSize = #{}
  \override StaffSymbol #'staff-space = #(magstep {})
}}{{ <<
'''

DIRECTIVE_END = r'''
>> }
'''

####################################################################################################

class LilyExtError(SphinxError):
    category = 'Lilypond extension error'

####################################################################################################

class lily(nodes.Inline, nodes.TextElement):
    pass

####################################################################################################

class displaylily(nodes.Part, nodes.Element):
    pass

####################################################################################################

def lily_role(role, rawtext, text, lineno, inliner, options={}, content=[]):

    music = utils.unescape(text, restore_backslashes=True)
    return [lily(music=music)], []

####################################################################################################

class LilyDirective(Directive):

    """ This class defines a ``lily`` directive.

    .. code-block:: ReST

        .. lily::
            :nowrap:

            \relative c'' {
                c4 a d c
            }

    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        'nowrap': directives.flag,
    }

    ##############################################

    def run(self):

        node = displaylily()
        node['lily_source'] = '\n'.join(self.content)
        node['docname'] = self.state.document.settings.env.docname
        node['nowrap'] = 'nowrap' in self.options

        return [node]

####################################################################################################

def render_lily(self, lily_source):

    """Render the Lilypond music expression *lily* using lilypond.

    """

    if hasattr(self.builder, '_lilypond_warned'):
        return None, None

    # self.builder.warn('Render lilipond')
    # _logger.info('Render lilypond\n' + lily_source)
    print('Render lilypond\n' + lily_source)

    basename = "{}.png".format(sha(lily_source.encode('utf-8')).hexdigest())
    relative_filename = os.path.join(self.builder.imgpath, 'lily', basename)
    absolut_filename = os.path.join(self.builder.outdir, '_images', 'lily', basename)

    if os.path.isfile(absolut_filename):
        return relative_filename

    lily_source = DOCUMENT_BEGIN + self.builder.config.pnglily_preamble + lily_source

    # use only one tempdir per build -- the use of a directory is cleaner
    # than using temporary files, since we can clean up everything at once
    # just removing the whole directory (see cleanup_lily_tempdir)
    if not hasattr(self.builder, '_lilypond_tempdir'):
        tempdir = self.builder._lilypond_tempdir = tempfile.mkdtemp()
    else:
        tempdir = self.builder._lilypond_tempdir

    lilypond_input_file = os.path.join(tempdir, 'music.ly')
    with open(lilypond_input_file, 'w') as fh:
        fh.write(lily_source)

    ensuredir(os.path.dirname(absolut_filename))

    # use some standard lilypond arguments
    lilypond_args = [self.builder.config.pnglily_lilypond]
    # Cropped SVG
    # http://lilypond.1069038.n5.nabble.com/Cropped-SVG-Output-td182397.html
    # https://github.com/Abjad/abjad/issues/606 Option to ask lilypond to render to SVG and use ipython.display.SVG to show it #606
    # inkscape -S lylipond-test.svg
    #   svg78,170.07411,25.448056,223.11942,34.394129 # X Y W H
    lilypond_args += [
        '-o', tempdir,
        # '--format=png',
        '-dbackend=eps',
        # -dbackend=svg --svg-woff
        # cf. http://lilypond.org/doc/v2.19/Documentation/usage/command_002dline-usage#advanced-command-line-options-for-lilypond
        '-dno-gs-load-fonts',
        '-dinclude-eps-fonts',
        '--png',
        '-dresolution=200',
    ]
    # add custom ones from config value
    lilypond_args.extend(self.builder.config.pnglily_lilypond_args)

    # last, the input file name
    lilypond_args.append(lilypond_input_file)

    try:
        process = Popen(lilypond_args, stdout=PIPE, stderr=PIPE)
    except OSError as exception:
        if exception.errno != 2:   # No such file or directory
            raise
        template = 'lilypond command {} cannot be run (needed for music display), check the pnglily_lilypond setting'
        self.builder.warn(template.format(self.builder.config.pnglily_lilypond))
        self.builder._lilypond_warned = True
        return None, None
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        template = 'lilypond exited with error:\n[stderr]\n{}\n[stdout]\n{}'
        raise LilyExtError(template.format(stderr.decode('utf-8'), stdout.decode('utf-8')))

    shutil.copyfile(os.path.join(tempdir, 'music.png'), absolut_filename)

    # Popen(['mogrify', '-trim', absolut_filename], stdout=PIPE, stderr=PIPE)

    return relative_filename

####################################################################################################

def cleanup_lily_tempdir(app, exception):

    if exception:
        return
    if not hasattr(app.builder, '_lilypond_tempdir'):
        return

    try:
        shutil.rmtree(app.builder._lilypond_tempdir)
    except Exception:
        pass

####################################################################################################

def latex_visit_lily(self, node):
    self.body.append('{' + node['lily_source'] + '}')
    raise nodes.SkipNode

####################################################################################################

def latex_visit_displaylily(self, node):
    self.body.append(node['lily_source'])
    raise nodes.SkipNode

####################################################################################################

def html_visit_lily(self, node):

    lily_source = INLINE_BEGIN.format(self.builder.config.pnglily_fontsize[0])
    lily_source += node['lily_source'] + INLINE_END
    # lily_source += '#"' + node['lily_source'] + '"' + INLINE_END

    try:
        filename = render_lily(self, lily_source)
    except LilyExtError as exception:
        sytem_message = nodes.system_message(
            str(exception), type='WARNING', level=2,
            backrefs=[], source=node['lily_source'])
        sytem_message.walkabout(self)
        self.builder.warn('display lilypond {}: {}'.format(node['lily_source'], exception))
        raise nodes.SkipNode

    lily_source = self.encode(node['lily_source']).strip()
    if filename is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="lily">{}</span>'.format(lily_source))
    else:
        template = '<img class="lily" src="{}" alt="{}" align="absbottom"/>'
        self.body.append(template.format(filename, lily_source))

    raise nodes.SkipNode

####################################################################################################

def html_visit_displaylily(self, node):

    if node['nowrap']:
        lily_source = node['lily_source']
    else:
        lily_source = DIRECTIVE_BEGIN.format(
            self.builder.config.pnglily_fontsize[1],
            self.builder.config.pnglily_fontsize[1]
        )
        lily_source += node['lily_source'] + DIRECTIVE_END

    try:
        filename = render_lily(self, lily_source)
    except LilyExtError as exception:
        sytem_message = nodes.system_message(
            str(exception), type='WARNING', level=2,
            backrefs=[], source=node['lily_source'])
        sytem_message.walkabout(self)
        self.builder.warn('inline lilypond {}: {}'.format(node['lily_source'], exception))
        raise nodes.SkipNode

    self.body.append(self.starttag(node, 'div', CLASS='lily'))
    self.body.append('<p>')
    lily_source = self.encode(node['lily_source']).strip()
    if filename is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="lily">{}</span>'.format(lily_source))
    else:
        self.body.append('<img src="{}" alt="{}" />\n</div>'.format(filename, lily_source))
    self.body.append('</p>')

    raise nodes.SkipNode

####################################################################################################

def setup(app):

    app.add_node(lily,
                 latex=(latex_visit_lily, None),
                 html=(html_visit_lily, None))
    app.add_node(displaylily,
                 latex=(latex_visit_displaylily, None),
                 html=(html_visit_displaylily, None))

    app.add_role('lily', lily_role)

    app.add_directive('lily', LilyDirective)

    app.add_config_value('pnglily_preamble', '', False)
    app.add_config_value('pnglily_fontsize', ['10', '-3'], False)
    app.add_config_value('pnglily_lilypond', 'lilypond', False)
    app.add_config_value('pnglily_lilypond_args', [], False)

    app.connect('build-finished', cleanup_lily_tempdir)
