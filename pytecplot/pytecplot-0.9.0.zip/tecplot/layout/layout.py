from __future__ import division, print_function, absolute_import
from six import string_types
import logging

from fnmatch import fnmatch
from os import path

from ..tecutil import _tecutil, ArgList, IndexSet, sv, lock
from ..constant import *
from ..exception import *
from .. import session
from .page import Page

log = logging.getLogger(__name__)


@lock()
def new_layout():
    """Clears the current layout and creates a blank frame.

    This will invalidate any object instances previously obtained:

    .. code-block:: python
        :emphasize-lines: 2

        >>> import tecplot
        >>> frame = tecplot.active_frame()
        >>> tecplot.new_layout()
        >>> # frame is no longer usable:
        >>> try:
        ...   frame.plot_type
        ... except Exception as e:
        ...   print(type(e),e)
        ...
        <class 'ValueError'> 255 is not a valid PlotType
    """
    _tecutil.NewLayout()


@lock()
def load_layout(filename):
    """Reads a layout file and replaces the active frame.

    Parameters:
        filename (`string <str>`): The file name of the layout to be loaded.
            (See note below conerning absolute and relative paths.)

    Raises:
        `TecplotOSError`: If file can not be found.
        `TecplotSystemError`: If the file could not be loaded.

    .. note:: **Absolute and relative paths with PyTecplot**

        Unless file paths are absolute, saving and loading files will be
        relative to the current working directory of the parent process. This
        is different when running the PyTecplot script in batch mode and when
        running in connected mode with `tecplot.session.connect()`. In batch
        mode, paths will be relative to Python's current working directory as
        obtained by :func:`os.getcwd()`. When connected to an instance of
        Tecplot 360, paths will be relative to Tecplot 360's' start-up folder
        which is typically the Tecplot 360 installation "bin" folder.

    This will replace the current layout and therefore will invalidate any
    object instances previously obtained:

    .. code-block:: python
        :emphasize-lines: 2

        >>> import tecplot
        >>> frame = tecplot.active_frame()
        >>> tecplot.load_layout('analysis.lay')
        >>> # frame is no longer usable
    """
    if not path.exists(filename):
        raise TecplotOSError('can not find layout file: {0}'.format(filename))
    with ArgList(FNAME=path.abspath(filename)) as arglist:
        if not _tecutil.OpenLayoutX(arglist):
            raise TecplotSystemError()


@lock()
def save_layout(filename, include_data=None, include_preview=None,
                use_relative_paths=None, post_layout_commands=None,
                pages=None):
    """Writes the current layout to a file.

    Parameters:
        filename (`string <str>`): The path to the output filename. (See note
            below conerning absolute and relative paths.)
        include_data (`boolean <bool>`, optional): Associated value indicates
            if the layout should be saved as a layout package where the data
            is included with the style information or if it should reference
            linked data. If 'include_data' is None and the filename ends
            with '.lpk', then the file will be saved as a layout package file.
            (default: None)
        include_preview (`boolean <bool>`, optional): Associated value
            indicates if the layout package should also include a preview
            image. This argument only applies if the include data option is
            True. (default: `True`)
        use_relative_paths (`boolean <bool>`, optional): Associated value
            indicates if the layout should be saved using relative paths.
            This argument only applies if the include data option is `False`.
            (default: `False`)
        post_layout_commands (`string <str>`, optional): A character string
            containing a set of Tecplot macro commands that are appended to
            the layout or layout package file. These can be almost anything
            and are generally used to store add-on specific state
            information using ``$!EXTENDEDCOMMAND`` commands. (default:
            `None`)
        pages (`list` of `Page` objects, optional): If `None`, all pages
            are written to the layout, otherwise the specified subset of pages
            are written. (default: `None`)

    Raises:
        `TecplotSystemError`

    .. note:: **Absolute and relative paths with PyTecplot**

        Unless file paths are absolute, saving and loading files will be
        relative to the current working directory of the parent process. This
        is different when running the PyTecplot script in batch mode and when
        running in connected mode with `tecplot.session.connect()`. In batch
        mode, paths will be relative to Python's current working directory as
        obtained by :func:`os.getcwd()`. When connected to an instance of
        Tecplot 360, paths will be relative to Tecplot 360's' start-up folder
        which is typically the Tecplot 360 installation "bin" folder.

    .. note::

        If you receive an exception with the error message "Journal should be
        valid in all frames", then you must save a data file using
        `save_tecplot_ascii` or `save_tecplot_plt` before saving the layout.

    Example:
        In this example, we load an example layout file and then save it as a
        packaged layout file.

        .. code-block:: python
            :emphasize-lines: 6

            >>> import os
            >>> import tecplot
            >>> examples_dir = tecplot.session.tecplot_examples_directory()
            >>> infile = os.path.join(examples_dir, 'SimpleData', 'F18.lay')
            >>> tecplot.load_layout(infile)
            >>> tecplot.save_layout('output.lpk', include_data=True)
    """

    if __debug__:
        # for frame in frames():
        #     if frame.plot_type is PlotType.Sketch:
        #         log.warning(
        #             'Saving layout will ignore data attached to Frames that ' +
        #             'have plot-type "Sketch". Set the plot-type of the frames to ' +
        #             'Cartesian 3D for example to save the associated datasets.')

        if not isinstance(filename, string_types):
            raise TecplotTypeError('filename must be a string')

        for argument in [(include_data, 'include_data'),
                         (include_preview, 'include_preview'),
                         (use_relative_paths, 'use_relative_paths')]:
            if not isinstance(argument[0], (bool, type(None))):
                raise TecplotTypeError('{} must be bool'.format(argument[1]))

        if not isinstance(post_layout_commands, (string_types, type(None))):
            raise TecplotTypeError('post_layout_commands must be a string')

        if not isinstance(pages, (list, type(None))):
            raise TecplotTypeError('pages must be a list of Page objects')

    # As a convenience for the client, if they don't provide a value
    # for include_data and the filename ends in .lpk, set include_data
    # to true so that an lpk file will be created.
    if include_data is None and filename.lower().endswith('.lpk'):
        include_data = True

    with ArgList() as arglist:
        arglist[sv.FNAME] = filename

        for arg, svarg in [(include_data, sv.INCLUDEDATA),
                           (include_preview, sv.INCLUDEPREVIEW),
                           (use_relative_paths, sv.USERELATIVEPATHS),
                           (post_layout_commands, sv.POSTLAYOUTCOMMANDS)]:
            if arg is not None:
                arglist[svarg] = arg

        if pages is not None:
            # noinspection PyProtectedMember
            arglist[sv.PAGELIST] = IndexSet(P.position for P in pages)

        if not _tecutil.SaveLayoutX(arglist):
            raise TecplotSystemError()


def active_page():
    """Returns the currently active page.

    Returns:
        `Page`: The currently active page.

    Only one `Page` can be active at any given time. As long as the page is
    not deleted (through a call to `new_layout` or `load_layout` for
    example) this can be used to bring it back to the active state:

    .. code-block:: python
        :emphasize-lines: 1

        >>> import tecplot
        >>> page1 = tecplot.active_page()
        >>> page2 = tecplot.add_page()
        >>> # page2 is now active, but we can
        >>> # bring page1 back to the front:
        >>> page1.activate()
    """
    return Page(_tecutil.PageGetUniqueID())


@lock()
def add_page():
    """Adds a `Page` to the layout.

    Returns:
        `Page`: The newly created page.

    This will implicitly activate the newly created page:

    .. code-block:: python
        :emphasize-lines: 2

        >>> import tecplot
        >>> page1 = tecplot.active_page()
        >>> page2 = tecplot.add_page()
        >>> # page2 is now active
    """
    if _tecutil.PageCreateNew():
        return Page(_tecutil.PageGetUniqueID())
    else:
        raise TecplotSystemError('could not add-create-new page')


@lock()
def delete_page(page_to_delete):
    """Removes a `Page` from the layout.

    This will render any `Page` object pointing to the deleted `Page` useless.
    The unique ID will not be used again in the active session and it is up
    to the user to clear the python object using `del`::

        >>> import tecplot as tp
        >>> page = tp.add_page()
        >>> tp.delete_page(page)
        >>> next_page = tp.active_page()
        >>> page == next_page
        False
        >>> page.active
        False
        >>> page.activate()
        >>> del page # clear the python object
    """
    page_to_delete.activate()
    _tecutil.PageDelete()


@lock()
def next_page():
    """Activates and returns the next page.

    Returns:
        `layout.Page`: The next page in the layout.

    `Page` objects are stored in an ordered stack in the |Tecplot Engine|.
    This method rotates the stack and returns the resulting active `Page`:

    .. code-block:: python
        :emphasize-lines: 3

        >>> import tecplot
        >>> from tecplot.layout import next_page
        >>> page1 = tecplot.add_page()
        >>> page2 = tecplot.add_page()
        >>> next_page = next_page()
        >>> # page1 is now the active page
        >>> next_page == page1
        True
    """
    _tecutil.PageSetCurrentToNext()
    return active_page()


def page(pattern):
    """Returns the page by name.

    Parameters:
        pattern (`string <str>`): `Glob-style <fnmatch.fnmatch>`  pattern.

    Returns:
        `Page`: The first page identified by *pattern*.

    .. note::
        A layout can contain pages with identical names. When the parameter
        *pattern* is a string, the first match found is returned. This is
        not guaranteed to be deterministic and care should be taken to have
        only pages with unique names when this feature is used.

    Example:

        .. code-block:: python
            :emphasize-lines: 5

            >>> import tecplot
            >>> page11 = tecplot.add_page()
            >>> page11.name = 'Page 11'
            >>> page12 = tecplot.add_page()
            >>> page12.name = 'Page 12'
            >>> page12 == tecplot.page('Page 1*')
            True
    """
    try:
        return next(pages(pattern), None)
    except StopIteration:
        raise TecplotPatternMatchError(
            pattern, 'no page found with name: "{}"'.format(pattern), 'glob')


def pages(pattern=None):
    """Yields pages matching a specified pattern.

    Parameters:
        pattern (`string <str>`, optional):
            `Glob-style pattern <fnmatch.fnmatch>` used to match the names
            of the yielded `Page` objects. All pages are returned if no
            pattern is specified. (default: `None`)

    Returns:
        `Page`: Generator of pages identified by *pattern*.

    This function returns a generator which can only be iterated over once.
    It can be converted to a `list` for persistence::

        >>> import tecplot
        >>> # iterate over all pages and print their names
        >>> for page in tecplot.pages():
        >>>     print(page.name)
        >>> # store a persistent list of pages
        >>> pages = list(tecplot.pages())
    """
    for i in range(_tecutil.PageGetCount()):
        current_page = Page(_tecutil.PageGetUniqueID())
        if pattern is None or fnmatch(current_page.name, pattern):
            yield current_page
        next_page()


def active_frame():
    """Returns the active frame.

    Returns:
        `Frame`: Currently active frame.
    """
    return active_page().active_frame()


def frames(frame_pattern=None, page_pattern=None):
    """Returns a generator of frames matching the specified pattern.

    Parameters:
        frame_pattern (`string <str>`, optional):
            `Glob-style pattern <fnmatch.fnmatch>` used to match the names
            of the yielded `Frame` objects. All frames are returned if no
            pattern is specified. (default: `None`)
        page_pattern (`string <str>`, optional):
            `Glob-style pattern <fnmatch.fnmatch>` used to match the names
            of the yielded `Frame` objects. All frames are returned if no
            pattern is specified. (default: `None`)

    Returns:
        `Frame`: Generator of frames identified by name patterns.
    """
    for page in pages(page_pattern):
        for frame in page.frames(frame_pattern):
            yield frame

def aux_data():
    """Auxiliary data for the current layout.

    Returns:
        `AuxData`

    This is the auxiliary data attached to the entire layout containing all
    frames and datasets currently held by the Tecplot Engine. Such data is
    written to the layout file by default and can be retrieved later. Example
    usage::

        >>> aux = tp.layout.aux_data()
        >>> aux['info'] = '''\
        ... This layout contains a lot of things:
        ...     1. Something
        ...     2. Something else
        ...     3. Also this'''
        >>> print(aux['info'])
        This layout contains a lot of things:
            1. Something
            2. Something else
            3. Also this
    """
    return session.AuxData(None, AuxDataObjectType.Layout)
