"""Jupyter Notebook initialization.

Usage:

1) Add the following to the first code cell of your notebook:

   import mmf_setup; mmf_setup.nbinit()

2) Execute and save the results.

3) Trust the notebook (File->Trust Notebook).


This module provides customization for Jupyter notebooks including
styling and some pre-defined MathJaX macros.
"""
import importlib
import os.path
import shutil
import subprocess
import sys
import tempfile
import traceback

from IPython.display import HTML, Javascript, display, clear_output
import notebook

__all__ = ['nbinit']

_HERE = os.path.abspath(os.path.dirname(__file__))
_DATA = os.path.join(_HERE, '_data')
_NBTHEMES = os.path.join(_DATA, 'nbthemes')

_MESSAGE = r"""
<i>
<p>This cell contains some definitions for equations and some CSS for styling
  the notebook. If things look a bit strange, please try the following:
<ul>
  <li>Choose "Trust Notebook" from the "File" menu.</li>
  <li>Re-execute this cell.</li>
  <li>Reload the notebook.</li>
</ul>
</p>
</i>
"""

_TOGGLE_CODE = r"""<script>
code_show=true;
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
}
$( document ).ready(code_toggle);
</script>
<form action="javascript:code_toggle()"><input type="submit"
    value="Click here to toggle on/off the raw code."></form>
"""


def nbinit(theme='default', hgroot=True, toggle_code=False, debug=False, quiet=False):
    """Initialize a notebook.

    This function displays a set of CSS and javascript code to customize the
    notebook, for example, defining some MathJaX latex commands.  Saving the
    notebook with this output should allow the notebook to render correctly on
    nbviewer.org etc.

    Arguments
    ---------
    theme : str
       Choose a theme.
    hgroot : bool
       If `True`, then add the root hg directory to the path so that top-level
       packages can be imported without installation.  This is the path
       returned by `hg root`.  This path is also stored as `mmf_setup.HGROOT`.
    toggle_code : bool
       If `True`, then provide a function to toggle the visibility of input
       code.  (This should be replaced by an extension.)
    debug : bool
       If `True`, then return the list of CSS etc. code displayed to the
       notebook.
    quiet : bool
       If `True`, then do not display message about reloading and trusting notebook.
    """
    clear_output()

    res = []

    def _load(ext, theme=theme):
        """Try loading resource from theme, fallback to default"""
        for _theme in [theme, 'default']:
            _file = os.path.join(_NBTHEMES,
                                 '{theme}{ext}'.format(theme=_theme, ext=ext))
            if os.path.exists(_file):
                with open(_file) as _f:
                    return _f.read()
        return ""
        
    def _display(val, wrapper=HTML):
        res.append((val, wrapper))
        display(wrapper(val))

    # CSS
    _display(r"<style>{}</style>".format(_load(".css")))

    # Javascript
    _display(_load('.js'), wrapper=Javascript)

    # LaTeX commands
    _template = r'<script id="MathJax-Element-48" type="math/tex">{}</script>'
    _display(_template.format(_load('.tex').strip()))

    # Remaining HTML
    _display(_load('.html'))

    # Message
    if not quiet:
        _display(_MESSAGE)
        
    if toggle_code:
        _display(_TOGGLE_CODE)

    if hgroot:
        from .set_path import hgroot

    if debug:
        return res


######################################################################
# Old stuff.  This was the old way of installing things.  There are
# also some additional goodies here that should be included above
# after testing.
def run_with_bash(cmds):
    """Execute the specified commands with a shell.

    Note each command should be a list of strings as required by subprocess.

    Example
    -------
    >>> res = run_with_bash([['echo', 'hello!']])
    Running: echo hello!
    """
    for cmd in cmds:
        print("Running: {}".format(" ".join(cmd)))
        try:
            subprocess.check_call(cmd)
        except Exception:
            traceback.print_exc()


class Install(object):
    """
    Use this as a context::

        with Install() as install:
            install.install_all()
    """

    def __init__(self, ipython_dir=None, user=True):
        """Installs various notebook extensions etc.

        Arguments
        ---------
        ipython_dir : str, None
           If provided, then the install is performed here, otherwise
           the install takes place in the default ipython_dir location.
        user : bool
           If `True`, then install in the user's ipython_dir,
           otherwise install in the system location.  This simply
           passes the `--user` flag to ipython.
        """
        self.ipython_dir = ipython_dir
        self.user = user
        self.old_ipython_dir = None

    def install_nbextension(self, name):
        notebook.install_nbextension(name, user=self.user)

    def __enter__(self):
        """Set the IPYTHONDIR environment variable."""
        # Use environment because --ipython-dir does not always work
        # https://github.com/ipython/ipython/issues/8138
        if self.ipython_dir is not None:
            if 'IPYTHONDIR' in os.environ:
                self.old_ipython_dir = os.environ['IPYTHONDIR']
            os.environ['IPYTHONDIR'] = self.ipython_dir
        return self

    def __exit__(self, type, value, tb):
        if self.old_ipython_dir is not None:
            os.environ['IPYTHONDIR'] = self.old_ipython_dir

        return type is not None

    def install_all(self):
        self.install_calico_tools()
        # self.install_drag_and_drop()
        self.install_mathjax()
        self.install_rise()

    def install_calico_tools(self):
        """Install the Calico tools:

        * Section numbering
        * Table of contents generation
        * References
        * Moving cells by group
        * Spell checking.
        """
        for _f in ["calico-document-tools-1.0.zip",
                   "calico-cell-tools-1.0.zip",
                   "calico-spell-check-1.0.zip"]:
            self.install_nbextension(
                "https://bitbucket.org/ipre/calico/downloads/{}".format(_f))

    def install_mathjax(self):
        from IPython.external import mathjax
        mathjax.install_mathjax()

    def install_rise(self):
        """Install RISE for slideshows.

        https://github.com/damianavila/RISE.
        """
        tmpdir = tempfile.mkdtemp()
        cmds = [
            ['git', 'clone', 'https://github.com/damianavila/RISE.git',
             '{}/RISE'.format(tmpdir)]
        ]
        run_with_bash(cmds=cmds)

        sys.path.insert(0, '{}/RISE'.format(tmpdir))
        setup = importlib.import_module('setup')
        setup.install(use_symlink=False, profile='default', enable=True)
        del sys.path[0]
        shutil.rmtree(tmpdir)

    def install_drag_and_drop(self):
        """Install the drag and drop extension for images:
        https://github.com/ipython-contrib/\
                IPython-notebook-extensions/wiki/drag-and-drop
        """
        self.install_nbextension(
            'https://raw.githubusercontent.com/ipython-contrib/' +
            'IPython-notebook-extensions/master/usability/dragdrop/main.js')
