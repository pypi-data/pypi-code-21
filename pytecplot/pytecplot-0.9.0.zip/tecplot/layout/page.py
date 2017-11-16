import logging

from contextlib import contextmanager
from fnmatch import fnmatch

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from .. import macro, session
from ..tecutil import Index, lock, lock_attributes, sv
from .frame import Frame


log = logging.getLogger(__name__)


@lock_attributes
class Page(object):
    """`Page` object within a layout, holding onto one or more `Frames <Frame>`.

    Parameters:
        uid (`integer <int>`, optional): This must be a *valid* unique ID
            number pointing internally to a `Page` object or `None`. A new
            `Page` is created if set to `None`. (default: `None`)

    Warning:
        Though it is possible to create a `Page` object using the
        constructor, it is usually sufficient to obtain a page through
        `tecplot.add_page`,  `tecplot.active_page`, `tecplot.page` or
        `tecplot.pages`.

    A `Page` can be thought of like a canvas onto which one or more
    `Frames <Frame>` can be laid out. The engine guarantees there will
    always be at least one `Page` in the layout which can be accessed
    via `tecplot.active_page`::

        >>> import tecplot
        >>> page = tecplot.active_page()
        >>> page
        Page(uid=1)
        >>> for frame in page.frames():
        ...   print(frame)
        Frame 001
    """
    def __init__(self, uid):
        self.uid = uid
        self.framelist = None
        """The unique ID number of this Page, internal to the |Tecplot Engine|."""
        self._sv = [sv.PAGE]

    def __str__(self):
        """Brief string representation.

        Returns:
            `string <str>`: Brief representation of this `Page`.

        Example::
            >>> import tecplot
            >>> page = tecplot.active_page()
            >>> print(page)
            Page: "Page 001"
        """
        return 'Page: "{name}"'.format(name=self.name)

    def __repr__(self):
        """Executable string representation.

        Returns:
            `string <str>`: Internal representation of this `Page`.

        The string returned can be executed to generate an identical
        copy of this `Page` object::

            >>> import tecplot
            >>> page = tecplot.active_page()
            >>> page_copy=None
            >>> print(repr(page))
            Page(uid=1)
            >>> exec('page_copy = '+repr(page))
            >>> page_copy
            Page(uid=11, page=Page(uid=1))

            >>> # page_copy is not technically a copy.
            >>> # it is the same object as the original page:
            >>> page == page_copy
            True
        """
        return 'Page(uid={uid})'.format(uid=self.uid)

    def __eq__(self, other):
        """Checks for `Page` equality in the |Tecplot Engine|.

        Returns:
            `bool`: `True` if the unique ID numbers are the same for both `Pages <Page>`.

        Example::

            >>> import tecplot
            >>> page1 = tecplot.active_page()
            >>> page2 = tecplot.add_page()
            >>> page1 == page2
            False
            >>> tecplot.active_page() == page2
            True
        """
        return self.uid == other.uid

    @lock()
    def __contains__(self, frame):
        with self.activated():
            result = False
            if _tecutil.FrameGetCount():
                _tecutil.FrameLightweightLoopStart()
                while True:
                    if frame.uid == _tecutil.FrameGetUniqueID():
                        result = True
                        break
                    if not _tecutil.FrameLightweightLoopNext():
                        break
                _tecutil.FrameLightweightLoopEnd()
            return result

    def __getitem__(self, pattern):
        return self.frame(pattern)

    def __iter__(self):
        self.framelist = list(self.frames())
        return self

    def __next__(self):
        try:
            return self.framelist.pop(0)
        except (KeyError, IndexError):
            raise StopIteration

    def next(self):  # if sys.version_info < (3,)
        return self.__next__()

    @property
    def aux_data(self):
        """Auxiliary data for this page.

        Returns: `AuxData`

        This is the auxiliary data attached to the page. Such data is written
        to the layout file by default and can be retrieved later. Example
        usage::

            >>> aux = tp.active_page().aux_data
            >>> aux['Result'] = '3.14159'
            >>> print(aux['Result'])
            3.14159
        """
        return session.AuxData(self, AuxDataObjectType.Page)

    @property
    def position(self):
        """Returns the position of the Page

        :type: `Index`

        The page positions are 0 based positions relative to the current page,
        where the current page has a position value of 0, the next page 1,
        the page after that 2, and so on.
        """
        return Index(_tecutil.PageGetPosByUniqueID(self.uid) - 1)

    @property
    def name(self):
        """Returns or sets the name.

        :type: `string <str>`

        This is the name used when searching for `Page` objects in
        `tecplot.pages` and `tecplot.page`. It does not have to be unique.

        Example::

            >>> import tecplot
            >>> page = tecplot.active_page()
            >>> page.name = 'My Data'
            >>> print('this page:', page.name)
            this page: My Data
        """
        with self.activated():
            return _tecutil.PageGetName()[1]

    @name.setter
    @lock()
    def name(self, name):
        with self.activated():
            if not _tecutil.PageSetName(name):
                raise TecplotSystemError()

    @property
    def paper(self):
        """The `Paper` defined in this `Page`.

        :type: `Paper`

        Every `Page` has the concept of a workspace which includes
        all `Frames <Frame>` as well as a sub-area of the workspace
        called the `Paper`. The limits of the `Paper` with respect to
        the placement of `Frames <Frame>` is used when exporting
        certain image formats.
        """
        return Paper(self)

    @property
    def active(self):
        """Checks if this `Page` is active.

        Returns:
            `bool`: `True` if active.
        """
        return self.uid == _tecutil.PageGetUniqueID()

    @lock()
    def activate(self):
        """Activates the `Page`.

        Raises:
            `TecplotRuntimeError`: Page does not exist.
            `TecplotSystemError`: Could not activate the page.
        """
        if not self.active:
            if not self.exists:
                raise TecplotRuntimeError('page does not exists')
            elif not _tecutil.PageSetCurrentByUniqueID(self.uid):
                raise TecplotSystemError('could not activate page')

    @contextmanager
    def activated(self):
        current_page = Page(_tecutil.PageGetUniqueID())
        if self == current_page:
            yield
        else:
            self.activate()
            try:
                yield
            finally:
                current_page.activate()

    def active_frame(self):
        """Returns the active `Frame`.

        Returns:
            `Frame`: The active `Frame`.

        This implicitly activates this `Page` and returns the active
        `Frame` attached to it.
        """
        self.activate()
        if _tecutil.FrameGetCount():
            return Frame(_tecutil.FrameGetActiveID(), self)

    @lock()
    def add_frame(self):
        """Creates a new `Frame` in this `Page`.

        Returns:
            `Frame`: The newly created and activated `Frame`.

        Raises:
            `TecplotRuntimeError`: Could not find active frame.
            `TecplotSystemError`: Could not create a new frame.

        This implicitly activates the `Page` and creates and activates
        a new `Frame`.
        """
        self.activate()
        if not _tecutil.FrameCreateNew(False, 0, 0, 0, 0):
            raise TecplotSystemError('could not create new frame')
        else:
            uid = _tecutil.FrameGetActiveID()
            if uid > 0:
                return Frame(uid, self)
            else:
                raise TecplotRuntimeError('could not get id of newly created active frame')

    @lock()
    def delete_frame(self, frame):
        """Removes the frame from this `Page`.

        Raises:
            `TecplotRuntimeError`: If `Frame` is not in this `Page`.
            `TecplotSystemError`: Could not delete the frame.
        """
        if frame not in self:
            raise TecplotRuntimeError('frame is not in this page')
        else:
            with frame.activated():
                if not _tecutil.FrameDeleteActive():
                    raise TecplotSystemError()

    @lock()
    def frame(self, pattern):
        """Returns the `Frame` by name.

        Parameters:
            pattern (`string <str>`): `glob-style <fnmatch.fnmatch>` pattern.

        Returns:
            `Frame`: The first `Frame` identified by *pattern*.

        .. note::
            A `Page` can contain `Frames <Frame>` with identical names. When
            the parameter *pattern* is a string, the first match found is
            returned. This is not guaranteed to be deterministic and care
            should be taken to have only `Frames <Frame>` with unique names
            when this feature is used.

        Example:

            .. code-block:: python
                :emphasize-lines: 4

                >>> import tecplot
                >>> page = tecplot.active_page()
                >>> frameA = page.add_frame('A')
                >>> frameB = page.add_frame('B')
                >>> frameA == page.frame('A')
                True
        """
        with self.activated():
            frame = None
            if _tecutil.FrameGetCount():
                _tecutil.FrameLightweightLoopStart()
                while True:
                    if fnmatch(_tecutil.FrameGetName()[1], pattern):
                        frame = Frame(_tecutil.FrameGetUniqueID(), self)
                        break
                    if not _tecutil.FrameLightweightLoopNext():
                        break
                _tecutil.FrameLightweightLoopEnd()
            if frame is None:
                raise TecplotPatternMatchError(
                    pattern,
                    'no frame found with name: "{}"'.format(pattern),
                    'glob')
            return frame

    @lock()
    def frames(self, pattern=None):
        """Returns a `list` of `Frames <Frame>` matching the specified pattern.

        Parameters:
            pattern (`string <str>`, optional): `Glob-style pattern
                <fnmatch.fnmatch>` used to match the names of the yielded
                `Frame` objects. All frames are returned if no pattern is
                specified. (default: `None`)

        Returns:
            `list`: `Frames <Frame>` identified by *pattern*.

        Example::

            >>> import tecplot
            >>> page = tecplot.active_page()

            >>> # iterate over all frames and print their names
            >>> for frame in page.frames():
            >>>     print(frame.name)
            Frame 001
            Frame 002
            >>> # store a persistent list of frames
            >>> frames = page.frames()
            >>> print([f.name for f in frames])
            ['Frame 001', 'Frame 002']
        """
        with self.activated():
            framelist = []
            if _tecutil.FrameGetCount():
                _tecutil.FrameLightweightLoopStart()
                try:
                    while True:
                        success, name = _tecutil.FrameGetName()
                        if success:
                            if pattern is None or fnmatch(name, pattern):
                                framelist.append(Frame(_tecutil.FrameGetUniqueID(), self))
                        if not _tecutil.FrameLightweightLoopNext():
                            break
                finally:
                    _tecutil.FrameLightweightLoopEnd()
            if not framelist and pattern is not None:
                raise TecplotPatternMatchError(
                    pattern,
                    'no frames found with name: "{}"'.format(pattern),
                    'glob')
            return framelist

    @property
    @lock()
    def exists(self):
        """Checks if the `Page` exists in the current layout.

        This will return `False` after the `Page` has been deleted::
            >>> import tecplot as tp
            >>> page = tp.add_page()
            >>> page.exists
            True
            >>> tp.delete_page(page)
            >>> page.exists
            False
        """
        current_page = _tecutil.PageGetUniqueID()
        try:
            for _ in range(_tecutil.PageGetCount()):
                _tecutil.PageSetCurrentToNext()
                if self.uid == _tecutil.PageGetUniqueID():
                    return True
            return False
        finally:
            if current_page != _tecutil.PageGetUniqueID():
                _tecutil.PageSetCurrentByUniqueID(current_page)

    @lock()
    def tile_frames(self, mode=TileMode.Grid):
        """Tile frames based on a certain mode.

        Parameters:
            mode (`TileMode`, optional): Direction and layout mode for tiling
                frames. Possible values: `TileMode.Grid` (default),
                `TileMode.Columns`, `TileMode.Rows`, `TileMode.Wrap`.

        Example usage::

            >>> from tecplot.constant import TileMode
            >>> page.tile_frame(TileMode.Wrap)
        """
        with self.activated():
            macro.execute_extended_command('Multi Frame Manager', mode.value)


@lock_attributes
class Paper(object):
    """The `Paper` boundary defined on a workspace.

    This is the area used for certain image output formats. It
    is defined for a specific `Page`. `Frames <Frame>` can be
    laid out in reference to this sub-area of the workspace.
    """
    def __init__(self, page):
        self.page = page
        self._sv = page._sv + [sv.PAPER]

    @property
    def dimensions(self):
        """Width and height.

        the dimensions, *(width, height)* in inches, of the
        currently defined paper in the Tecplot workspace.
        """
        with self.page.activated():
            return _tecutil.PaperGetDimensions()
