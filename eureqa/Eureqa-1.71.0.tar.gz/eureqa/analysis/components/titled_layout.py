from eureqa.analysis.components.base import _Component

class TitledLayout(_Component):
    """A layout with space for a title and description and content within an Analysis

    For example::

        h=HtmlBlock(html="<h1>Hybrid Performance</h1>")
        layout=TitledLayout(title="the title", description="You can add content specific description here", content=h)
        analysis.create_card(layout)

    :param str title: The title of the layout
    :param str description: The description of the layout (can contain HTML)
    :param _Component content: The component to use in the main content of the layout

    """

    _component_type_str = 'TITLED_LAYOUT'

    def __init__(self, title=None, description=None, content=None, _analysis=None, _component_id=None, _component_type=None):
        super(TitledLayout, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

        if title is not None:
            self._title = title

        if description is not None:
            self._description = description

        if content is not None:
            self.create_card(content)


    @property
    def title(self):
        """The title of this card.

        :return: title of this card
        :rtype: str"""
        return self._title

    @title.setter
    def title(self, val):
        self._title = val
        self._update()


    @property
    def description(self):
        """ The description of this card.

        :return: description of this card
        :rtype: str"""
        return self._description

    @description.setter
    def description(self, val):
        self._description = val
        self._update()


    @property
    def content(self):
        """The Component that this TitledLayout is adding a title to.
        This field can't be assigned to; use 'create_card()' to
        assign a Component to this TitledLayout.

        :rtype: ~eureqa.analysis.components._Component"""
        if not hasattr(self, "_content_component"):
            self._content_component = _Component._get(_analysis=self._analysis, _component_id=self._content_component_id)
        return self._content_component

    def create_card(self, component):
        """
        Assign a Component to this TitledLayout

        :param _Component component: Component to use as the content of this layout
        """
        if hasattr(self, "_analysis"):
            component._associate(self._analysis)

        # Set all local fields that we're able to set at this time
        self._content_component = component
        if hasattr(self, "_content_component_id"):
            del self._content_component_id
        if hasattr(component, "_component_id"):
            self._content_component_id = component._component_id

        # Save any updates to ourself
        self._update()

    def delete(self):
        if hasattr(self, "_content_component"):
            self._content_component.delete()
        super(TitledLayout, self).delete()

    def clone(self):
        clone = super(TitledLayout, self).clone()
        clone.create_card(self.content.clone())
        return clone

    def _walk_children(self):
        if hasattr(self, "_content_component"):
            yield self._content_component

    def _register(self, analysis):
        super(TitledLayout, self)._register(analysis)
        if hasattr(self, "_content_component"):
            self.create_card(self._content_component)

    def _associate_with_table(self, analysis):
        child_json = []
        if hasattr(self, "_content_component") and not hasattr(self._content_component, "_component_id"):
            children = self._content_component._associate_with_table(analysis)
            self.create_card(self._content_component)
            child_json += children
        return super(TitledLayout, self)._associate_with_table(analysis) + child_json

    def _fields(self):
        return super(TitledLayout, self)._fields() + [ 'title', 'description', 'content_component_id' ]
