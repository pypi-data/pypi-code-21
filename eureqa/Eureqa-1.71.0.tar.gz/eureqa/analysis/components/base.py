# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import uuid
from eureqa.utils import utils
from eureqa.utils.jsonrest import _JsonREST

# Utility function used in this file
def _iterator_not_empty(it):
    # Python idiom:
    # If you can retrieve at least one element from an iterator,
    # then that iterator is not empty.
    # For many iterators/generators, `len(it) == 0` requires
    # consuming the whole iterator in order to count its elements.
    # So, this is O(1) where that is O(n).
    try:
        it.next()
        return True
    except StopIteration:
        return False

# Python Metaclass that automatically tracks all known types of Components
# If you're in this file, you probably want to skip ahead to 'class Component()' below.
# The following code has a very specific use case.
class _ComponentRegistrar(type):
    """ For internal use only. """

    # For those not familiar with Python metaclasses and __new__:
    #
    # type.__new__() runs every time when a *class* object is created.
    # One can intercept that call by inheriting from type and overriding type.__new__().
    # And then by "registering" metaclass using __metaclass__ attribute of the actual class.
    # Just like we do in _Component class below.
    #
    # In the common case (unless you're creating classes on the fly), a class
    # is "constructed" in this sense when Python first opens and parses the
    # file containing this class.
    #
    # The "Component" class represents a common base class for a
    # collection of serializable objects.
    # The serialized representation of the class contains a 'type' string
    # that indicates what type of thing has been serialized; therefore,
    # which Python class should be used to represent it.
    # In order to de-serialize such objects, 'Component' must therefore
    # know about all of its subclasses that represent specific
    # types of objects, as well as which class represents which 'type'
    # string.
    # Rather than write and maintain a list, this code makes the Python
    # interpreter generate the list for us.

    def __new__(type_, name, bases, dict_):
        cls = type.__new__(type_, name, bases, dict_)
        assert hasattr(cls, "_component_type_str"), \
            "New Analysis Component classes must define a '_component_type' field"
        cls._register_type(cls._component_type_str)
        return cls


class _Component(_JsonREST):
    """
    Component base class.
    Implements common logic shared by all components.
    Do not construct this class directly; instead,
    construct the specific component that you want.

    Notes for component implementors:  (If your new class's sub-Components aren't showing up properly, read on!)

    The backend first sees a Component when the first of the following happens:
      * The Component is constructed with an Analysis passed into the constructor as an argument
      * The Component is added to an Item that is already attached to an Analysis
      * The Component is added to an Item that is not already attached to an Analysis, and then the Item is attached to an Analysis
      * The Component is added to a Table and that Table's data is uploaded
    If more than one of these things happens in the lifecycle of a Component, or if one happens repeatedly,
    only the very first occurrence counts.
    Call this first event "Association".

    Before Association, each individual Component subclass is responsible for tracking their sub-Components (if any).
    At Association, "Component._associate()" is called; each Component that holds sub-Components must override this
    method to also call "_associate()" on all of their sub-Components.
    After Association (and *NOT* before it), each Component is responsible for immediately calling "_associate()"
    on any sub-Component that is added to it.
    """

    __metaclass__ = _ComponentRegistrar

    def clone(self):
        # Make a copy of ourselves
        body = self._to_json()

        # Disassociate the copy from the current Analysis
        if "analysis_id" in body:
            del body["analysis_id"]
        if "component_id" in body:
            del body["component_id"]

        # Instantiate a new Item with this state
        return _Component._construct_from_json(body)

    def delete(self):
        """ Remove this Component from the server. """
        # Subclasses may override this to do more elaborate clean-up.
        self._delete()

    def __init__(self, _analysis=None, _component_id=None, _component_type=None):
        """ For internal use only. """
        if _component_id is not None:
            self._component_id = _component_id

        if _component_type is not None:
            self._component_type = _component_type
        else:
            self._component_type = self._component_type_str

        if _analysis:
            self._associate(_analysis)

    _component_type_str = "GENERIC_COMPONENT"
    _registered_types = {}

    @classmethod
    def _register_type(cls, component_type):
        cls._registered_types[component_type] = cls

    def _populate_eureqa(self):
        if not hasattr(self, "_analysis"):
            # Can't populate Eureqa yet
            return

        self._eureqa = self._analysis._eureqa


    # Override "_construct_from_json()" to use the appropriate subclass if possible
    @classmethod
    def _construct_from_json(cls, body, *args, **kwargs):

        # If we're given an analysis, pass it in after
        # we're done populating the object so that we don't make
        # extraneous HTTP requests populating partial object state.
        analysis = None
        if "_analysis" in kwargs:
            analysis = kwargs["_analysis"]
            del kwargs["_analysis"]

        ret = cls._registered_types.get(body.get("component_type"), _Component)(*args, **kwargs)
        ret._from_json(body)

        if analysis is not None:
            ret._register(analysis)

        ret._populate_eureqa()
        return ret

    # Override "_get_all_from_self()" to associate all newly-constructed components
    # with our Analysis (if any)
    def _get_all_from_self(self):
        """
        Fetch a list of all objects in the same directory as this object.
        :return: list() of objects of the current type
        """
        comps = super(_Component, self)._get_all_from_self()

        if hasattr(self, "_analysis"):
            for comp in comps:
                for c in comp._walk():
                    c._register(self._analysis)

        return comps

    def _object_endpoint(self):
        return '/analysis/%s/components/%s' % (utils.quote(self._analysis._id),
                                               utils.quote(self._component_id))

    def _directory_endpoint(self):
        return '/analysis/%s/components' % utils.quote(self._analysis._id)

    def _fields(self):
        return [ "analysis_id", "component_id", "component_type", "class_names", "style_attribute" ]

    def _batch_endpoint(self, continue_on_error):
        return self._directory_endpoint() + ("?continue_on_error=true" if continue_on_error else "")

    def _batch_update(self, eureqa, components, continue_on_error):
        json_arr = [x._to_json() for x in components]
        if len(json_arr) == 0:
            return  # Nothing to do here

        new_bodies = eureqa._session.execute(self._batch_endpoint(continue_on_error), 'POST', json_arr)
        for component, body in zip(components, new_bodies):
            if body.get("status") != "error":
                component._from_json(body)

    def _pre_associate(self, analysis):
        """
        Per-Component logic that must be performed immediately before
        associate()'ing the current Component with the server.
        Subclasses may override this method, though most shouldn't need to.
        Typically includes uploading dependent objects that are not Components.
        """
        pass

    def _associate(self, analysis):
        """
        Component-walking and -association, v2.0.

        You should NEVER override '_associate()'!  This is a major change from v1.0.

        Here are the methods that you should override:

         * _walk_children(): Should return a list or (preferably) O(1)-memory generator
           of all of the current component's immediate children
         * _register(analysis): Called after all of this component's children have been
           posted to the server and have _component_ids. Many Layout components in
           particular need to update themselves after their children have been given IDs;
           this is their opportunity to do so.

        There's also a third method that's overridden rarely, but is important when it is needed:
         * _pre_associate(analysis): This method is called on a Component immediately
           before that Component is sent to the server in order to be batch-created;
           after we know what Analysis we are going to upload the Component to.  In
           particular, our File and Image components need to upload their file and image
           data to the server prior to being POST'ed as a Component, so that their Component
           JSON structure can refer to the ID of their File.
        """

        # Pre-associate ourselves so that 'self._directory_endpoint()' can work
        # (Don't call 'self._associate()'; the whole point of this method is to
        # avoid an RPC at each level of its recursion, and we haven't done that yet.)
        self._analysis = analysis

        # Upload any files/images/etc that must be uploaded before we can start associating
        for c in self._walk():
            c._pre_associate(analysis)

        # Register all components with the server
        components = [c for c in self._walk() if not getattr(c, "_component_id", False)]
        self._batch_update(analysis._eureqa, components, True)

        # Walk all components; link them to the analysis in Python
        for c in self._walk():
            c._register(analysis)

        # Every component whose child just got an ID has now been modified with that child's new ID.
        # Force a batch-update to account for this.
        # In case we have nested layouts, repeat as needed so that each layer in the chain gets an ID.
        modified_children = components

        # Iterate at most #components times.
        # We should typically only iterate once or twice.
        # We should never actually iterate #components times;
        # the most pedantic edge case should be #components - 1 loops.
        # But, if there's a bug somewhere in this loop logic,
        # avoid an infinite loop.
        for i in xrange(len(components)):
            updated_component_ids = {c._component_id for c in modified_children
                                                      if hasattr(c, "_component_id")}

            modified_parents = \
                [
                    c for c in self._walk()
                      if _iterator_not_empty(
                          child for child in c._walk_children()
                                if getattr(child, "_component_id", None) in updated_component_ids)
                ]

            if len(modified_parents) == 0:
                break

            for c in modified_parents:
                c._register(analysis)

            self._batch_update(analysis._eureqa, modified_parents, True)

            modified_children = modified_parents

        # If, after that, any of our children don't have IDs, that's probably bad data;
        # we should probably ask the server again and error out if necessary.
        components = [c for c in self._walk() if not getattr(c, "_component_id", False)]
        if len(components) != 0:
            self._batch_update(analysis._eureqa, components, False)

    def _to_json(self):
        resp = super(_Component, self)._to_json()

        if hasattr(self, "_analysis"):
            resp["analysis_id"] = self._analysis._id

        return resp

    def _from_json(self, body):
        if hasattr(self, "_analysis") and body.get("analysis_id"):
            assert body.get("analysis_id") == self._analysis._id, \
                "_from_json() can't de-serialize an Item that belongs to a different Analysis"

        super(_Component, self)._from_json(body)

    def _walk(self):
        """
        _walk() returns a generator that iterates over the full Component tree rooted
        at the current node. The order of iteration is not guaranteed other than that
        parents come before their children.

        If you're working with component serialization in the future, you shouldn't
        override this method, but you may use it a lot.
        You *should* override '_walk_children()', below.
        """
        yield self
        for c in self._walk_children():
            for descendent in c._walk():
                yield descendent

    def _walk_children(self):
        return iter([])

    def _register(self, analysis):
        self._analysis = analysis
        self._analysis_id = analysis._id
        _JsonREST.__init__(self, analysis._eureqa)
        self._populate_eureqa()

    def _associate_with_table(self, analysis):
        # The base class implementation of this method only generates UUID but
        # does not add them to the actual analysis. Because most components
        # are directly inlined into the table and some involve extra actions (e.g. uploading a file)
        # It is up to a particular component to override this method and provide more
        # specific implementation.
        if not hasattr(self, "_component_id"):
            self._component_id = str(uuid.uuid4())
        return [self._to_json()]

    @property
    def _css_class(self):
        """
        Sets the `class` attribute of the generated component. Classes are added *after* any existing
        classes.

        Ex: Applying `component._css_class = "bar"` to `<div class="foo" />` yields `<div class="foo bar" />
        """
        return self._class_names

    @_css_class.setter
    def _css_class(self, val):
        self._class_names = val
        self._update()

    @property
    def _css_style(self):
        """
        Sets the `style` attribute of the generated component. Replaces any existing style attributes.

        Ex: `component._css_style = "background: red;"` generates `<div style="background: red;" />`
        """
        return self._style_attribute

    @_css_style.setter
    def _css_style(self, val):
        self._style_attribute = val
        self._update()

class _TwoVariablePlotComponent(_Component):
    _component_type_str = "TwoVariablePlot helper mixin (not a complete type)"


    def __init__(self, _analysis=None, _component_id=None, _component_type=None):

        super(_TwoVariablePlotComponent, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

        default_x_label = getattr(self, '_x_var', 'the x var')
        default_y_label = getattr(self, '_y_var', 'the y var')

        DEFAULTS = {'BOX_PLOT':             {'default_label' : { 'x': default_x_label, 'y': default_y_label },
                                             'default_format': { 'x': 'g',   'y': '.2s' }},

                    'DOUBLE_HISTOGRAM_PLOT':{'default_label' : { 'x': [default_x_label, default_y_label], 'y': 'number of values' },
                                             'default_format': { 'x': 'g', 'y': '.3s' }},

                    'SCATTER_PLOT':         {'default_label' : { 'x': default_x_label, 'y': default_y_label },
                                             'default_format': { 'x': '.3s', 'y': '.3s' }},

                    'BINNED_MEAN_PLOT':     {'default_label' : { 'x': default_x_label, 'y': default_y_label },
                                             'default_format': { 'x': '.3s', 'y': '.2f' }}}



        default_values = DEFAULTS.get(self._component_type,
                                      {'default_label' : { 'x': default_x_label, 'y': default_y_label },
                                       'default_format': { 'x': '.3s', 'y': '.3s' }})

        if not hasattr(self,'_axisLabels'):
            self._axisLabels = default_values['default_label']
        if not hasattr(self,'_labelFormat'):
            self._labelFormat = default_values['default_format']


    class XYMap(object):
        """ A named tuple with keys 'x' and 'y'

        :param TwoVariablePlotCard tvp: The TwoVariablePlotCard object.
        :param dict dic: X and Y parameters as dictionary.
        """

        def __init__(self, parent_component, body):
            self._parent_component = parent_component
            self._body = body

        @property
        def x(self):
            """ X value """
            return self._body['x']

        @x.setter
        def x(self, val):
            self._body['x'] = val
            self._update()

        @property
        def y(self):
            """ Y value """
            return self._body['y']

        @y.setter
        def y(self, val):
            self._body['y'] = val
            self._update()

        def _update(self):
            self._parent_component._update()
