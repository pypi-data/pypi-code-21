from collections import namedtuple
from functools import wraps

from ..exception import *
from ..constant import *
from ..tecutil import _tecutil, lock, lock_attributes, flatten_args, Index


def annotation_preamble(fn):
    """Things we want to do before calling the TecUtil annotation
       getter/setter methods."""
    @wraps(fn)
    def _fn(self, *a, **kw):
        with self.frame.activated():
            return fn(self, *a, **kw)
    return _fn


@lock_attributes
class Annotation(object):
    """An Annotation is a `Text` object which is attached to a `Frame`"""

    class _Iterator(object):
        def __init__(self, annotation_object_type, frame):
            self._annotation_object_type = annotation_object_type
            self._input_frame = frame

            assert annotation_object_type.__name__ in ('Text', 'Geom')

            tecutil_get_base = getattr(
                _tecutil, '{}GetBase'.format(annotation_object_type.__name__),
                None)
            self._tecutil_get_next = getattr(
                _tecutil, '{}GetNext'.format(annotation_object_type.__name__),
                None)

            # If there are no annotation objects attached to the frame,
            # tecutil_get_base() will return None and we will drop out
            # of the iteration loop the first time next() is called.
            self._current_annotation_id = tecutil_get_base()

        def next(self):
            # Currently Text_ID, Geom_ID types are ctypes.voidp's in pytecplot,
            # with TECUTIL_BAD_ID == None, so we check for None to indicate that
            # we are done iterating.
            # The fact that the ID's are voidp doesn't matter
            # because we're just passing the ID valid back to TecUtil without
            # trying to interpret it.
            if not self._current_annotation_id:
                # e.g., we're done iterating.
                raise StopIteration()
            else:
                # Get the next annotation in the list
                annotation_id = self._current_annotation_id
                self._current_annotation_id = self._tecutil_get_next(
                    self._current_annotation_id)

                # Return an annotation object (Text or Geom)
                # constructed from the id. Even the returned object will be
                # different from the original object in Python,
                # they will compare as equal since they have the same ID.
                #
                # Furthermore, changing the properties of one Text object
                # will change the properties of all objects with the same ID,
                # since all properties are stored in the engine and not
                # cached locally.
                return self._annotation_object_type(annotation_id,
                                                    self._input_frame)

        def __next__(self):  # python 3
            return self.next()  # python 2

        def __iter__(self):
            return self

    _TecUtilPropertyAPI = namedtuple('API', 'getter setter')

    def __init__(self, uid, frame, annotation_object_type):
        if uid == TECUTIL_BAD_ID:
            raise TecplotSystemError('Error creating annotation object')

        self.uid = uid
        self.frame = frame

        assert annotation_object_type.__name__ in ('Text', 'Geom')

        # Declare the *_api properties here to help Intellisense find these
        # symbols (which are dynamically initialized later below).

        # Prepend the names with underscores so we don't pollute the
        # intellisense namespace.
        self._is_valid_api = getattr(
            _tecutil, '{}IsValid'.format(annotation_object_type.__name__))

        self._anchor_position_api = None
        self._scope_api = None
        self._zone_or_map_api = None
        self._attached_api = None
        self._color_api = None
        self._clipping_api = None

        #
        # For TecUtil get/set methods common to Text and Geom annotations,
        # the TecUtil API to get/set those properties is symmetric, with
        # the only difference being 'Text' or 'Geom' in the function name.
        #
        # We can use this to dynamically create a table of TecUtil methods
        # which call either the Text or Geom version of the TecUtil function
        # depending on what type of annotation we are.
        #

        for name in [('anchor_position', 'AnchorPos'),
                     ('scope', 'Scope'),
                     ('zone_or_map', 'ZoneOrMap'),
                     ('color', 'Color'),
                     ('clipping', 'Clipping')
                     ]:
            tecutil_getter = getattr(
                _tecutil, '{}Get{}'.format(
                    annotation_object_type.__name__, name[1]), None)
            tecutil_setter = getattr(
                _tecutil, '{}Set{}'.format(
                    annotation_object_type.__name__, name[1]), None)

            setattr(self, '_' + name[0] + '_api', (
                Annotation._TecUtilPropertyAPI(
                    getter=tecutil_getter, setter=tecutil_setter)))

        # The TecUtilXXXAttached getter and setter do not follow the pattern
        # of TecUtil[Text|Geom]Get/Set*, so create them by hand below
        attached_getter = getattr(
            _tecutil, "{}IsAttached".format(annotation_object_type.__name__))
        attached_setter = getattr(
            _tecutil, "{}SetAttached".format(annotation_object_type.__name__))

        self._attached_api = Annotation._TecUtilPropertyAPI(
            getter=attached_getter, setter=attached_setter
        )

    _AnchorPosition = namedtuple('AnchorPosition', 'x y z')
    _AnchorPosition.__new__.__defaults__ = (0.0, 0.0, 0.0)

    @property
    @annotation_preamble
    def anchor_position(self):
        """Anchor coordinate position (e.g., origin) of the `Annotation`.

        :type: 2-`tuple` of `floats <float>`

        This will be  :math:`(x,y)` or :math:`(\theta,r)` depending on the plot
        type (Cartesian or polar). This example shows how to set the anchor
        position of a `Text` object::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_3d_text("abc")
            >>> text.anchor_position = (1.0, 2.0)
            >>> text.anchor_position.x
            1.0
            >>> text.anchor_position.y
            2.0
        """
        x, y, z = self._anchor_position_api.getter(self.uid)
        return Annotation._AnchorPosition(x, y, z)

    @anchor_position.setter
    @annotation_preamble
    def anchor_position(self, values):
        x, y, z = self._AnchorPosition(*flatten_args(*values))
        # Can't use @lock decorator here because the unit tests need to be able
        # to query the property() object for each property, and the @lock
        # decorator combined with the @property decorator confuses getattr().
        with lock():
            self._anchor_position_api.setter(
                self.uid, float(x), float(y), float(z))

    @property
    def scope(self):
        """The `Scope` (local or global) of the `Annotation`.

        :type: `Scope`

        `Annotations <Annotation>` with local scope are displayed only in the
        `frame <Frame>` in which they are created. If the `annotation
        <Annotation>` is defined as having `global <Scope.Global>` scope, it
        will appear in all "like" `frames <Frame>`. That is, those frames using
        the same data set as the one in which the `annotation <Annotation>` was
        created. (default: `Scope.Local`)

        Example showing how to set the scope of a `Text` object::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.scope = Scope.Global
            >>> text.scope
            Scope.Global
        """
        return Scope(self._scope_api.getter(self.uid))

    @scope.setter
    @lock()
    def scope(self, scope):
            self._scope_api.setter(self.uid, Scope(scope).value)

    @property
    @annotation_preamble
    def zone_or_map(self):
        """Zero-based index to the zone or map of this `Annotation`.

        :type: `Index`

        Example showing how to set the zone or map `Index` of a `Text` object::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text("abc")
            >>> text.zone_or_map = 1
            >>> text.zone_or_map
            1
        """
        return Index(self._zone_or_map_api.getter(self.uid))

    @zone_or_map.setter
    @annotation_preamble
    def zone_or_map(self, zone_or_map):
        with lock():
            self._attached_api.setter(self.uid, True)
            self._zone_or_map_api.setter(self.uid, Index(zone_or_map))

    @property
    @annotation_preamble
    def attached(self):
        """Attach the `Annotation` to a specific `Zone <data_access>` or map.

        :type: `boolean <bool>` (default: False)

        Example showing how to set the attached property of of a `Text`
        object::

            >>> import tecplot as tp
            >>> text = tp.active_frame().add_text("abc")
            >>> text.zone_or_map = 1
            >>> text.attached = True
            >>> text.zone_or_map
            1
            >>> text.attached
            True
        """
        return self._attached_api.getter(self.uid)

    @attached.setter
    @annotation_preamble
    def attached(self, is_attached):
        with lock():
            self._attached_api.setter(self.uid, is_attached)

    @property
    def color(self):
        """`Color` of the `Annotation`.

        :type: `Color` (default: `Color.Black`)

        Example showing how to set the `Color` of of a `Text` object::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text("abc")
            >>> text.color = Color.Blue
            >>> text.Color
            Color.Blue
        """
        return Color(self._color_api.getter(self.uid))

    @color.setter
    @lock()
    def color(self, color):
        with self.frame.activated():
            self._color_api.setter(self.uid, Color(color).value)

    @property
    @annotation_preamble
    def clipping(self):
        """Clipping properties of the `Annotation`

        :type: `Clipping` (default: `Clipping.ClipToViewport`)

        Clipping refers to displaying only that portion of an object that falls
        within a specified clipping region of the plot. If you have specified
        your text position in the Frame coordinate system, the `Annotation`
        will be clipped to the frame.

        If you have specified the Grid coordinate system, you can choose to
        clip your `Annotation` to the frame or the viewport. The size of the
        viewport depends on the plot type as follows:

            * 3D Cartesian - The viewport is the same as the frame, so viewport
                clipping is the same as frame clipping.
            * 2D Cartesian/XY Line - The viewport is defined by the extents of
                the X and Y axes.
            * Polar Line/Sketch - By default, the viewport is the same as the
                frame.

        Example showing how to set the clipping of a `Text`::

            >>> import tecplot as tp
            >>> from tecplot.constant import *
            >>> text = tp.active_frame().add_text('abc')
            >>> text.clipping = Clipping.ClipToFrame
            >>> text.clipping
            Clipping.ClipToFrame
        """
        return Clipping(self._clipping_api.getter(self.uid))

    @clipping.setter
    @annotation_preamble
    def clipping(self, clipping):
        with lock():
            self._clipping_api.setter(self.uid, clipping.value)
