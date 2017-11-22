from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class DropdownLayout(_Component):
    """
    DropdownLayout component
    Lets users pick to see other components based on titles (works with "many" items). Similar to a :class:`~eureqa.analysis.components.tabbed_layout.TabbedLayout` but more suited to larger lists of items.

    For example::

        d = DropdownLayout(label="Choose an item", padding="1.0em")
        d.add_component(title="choice 1", content=HtmlBlock("This is item 1"))
        d.add_component(title="choice 2", content=HtmlBlock("This is item 2"))
        analysis.create_card(d)

    :param str label: The overall label
    :param str padding: padding, specified in ems. Example "0.5em"
    """

    _component_type_str = 'DROPDOWN_LAYOUT'

    def __init__(self, label=None, padding=None, _analysis=None, _component_id=None, _component_type=None):
        if label is not None:
            self._label = label

        if padding is not None:
            self._padding = padding

        # A place to put Components that don't have IDs yet,
        # until we're '_registered()'d with an Analysis so can go get IDs for them.
        self._queued_components = []

        super(DropdownLayout, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)


    @property
    def label(self):
        """Text label for the Dropdown box

        :rtype: str
        """
        return self._label

    @label.setter
    def label(self, val):
        self._label = val
        self._update()


    @property
    def padding(self):
        """Padding (spacing) for this DropdownLayout, expressed in ems. Example "0.5em"

        :rtype: int
        """
        return self._padding

    @padding.setter
    def padding(self, val):
        self._padding = val
        self._update()


    class _TitledComponent(object):
        """Internal class: Representation of one element in the dropdown

        :param str title: Title of the Component in the dropdown list
        :param eureqa.analysis.components._Component component: The Component
        """
        def __init__(self, title, component):
            self.title = title
            self.component = component

        def _to_json(self):
            return { "value": self.title,
                     "component_id": getattr(self.component, "_component_id", None) }

    @property
    def components(self):
        """Internal: Set of components represented in the dropdown

        :return: list() of :class:`~eureqa.analysis.components.base._Component`
        """
        if not hasattr(self, "_components_cache"):
            self._components_cache = [_Component._get(_analysis=self._analysis,
                                        _component_id=x["component_id"]) for x in self._components]

        return list(self._components_cache)

    def _ensure_components_list(self):
        if not hasattr(self, "_components"):
            self._components = []
            self._components_cache = []

    def add_component(self, title, component=None, content=None):
        """
        Add a Component to the DropdownLayout

        :param str title: Title of the Component in the dropdown list
        :param _Component component: The Component to add to the dropdown list
        :param _Component content: Deprecated, Do not use
        """
        if hasattr(self, "_analysis"):
            component._associate(self._analysis)

        #content remains for backwards compatibility
        #make sure only one is set and use that
        if (component is None) == (content is None):
            raise Exception("Incorrect arguments to add_component. Either component or content must be set, but not both.")

        if content is not None:
            component = content

        # If we don't have an Analysis yet, queue this Component to be saved later
        if not hasattr(self, "_analysis"):
            self._queued_components.append(DropdownLayout._TitledComponent(title, component))
            return

        self._ensure_components_list()
        self._components.append(DropdownLayout._TitledComponent(title, component)._to_json())
        self._components_cache.append(component)

    def _walk_children(self):
        if hasattr(self, "_components"):
            for c in self.components:
                yield c
        for c in self._queued_components:
            yield c.component

    def _register(self, analysis):
        if len(self._queued_components) != 0:
            self._ensure_components_list()
        for c in self._queued_components:
            self._components.append(c._to_json())
            self._components_cache.append(c.component)

        self._queued_components = []

        super(DropdownLayout, self)._register(analysis)

    def _associate_with_table(self, analysis):
        for c in self._queued_components:
            self._ensure_components_list()
            self._components += c.component._associate_with_table(analysis)

        self._queued_components = []

        return super(DropdownLayout, self)._associate_with_table(analysis) + self._components

    def _fields(self):
        return super(DropdownLayout, self)._fields() + [ 'label', 'padding', 'components' ]
