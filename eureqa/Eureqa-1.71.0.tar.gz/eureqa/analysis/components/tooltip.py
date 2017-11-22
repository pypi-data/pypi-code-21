from eureqa.analysis.components.base import _Component

class Tooltip(_Component):
    """
    Tooltip Component: implements a tooltip

    For example::

        tt = Tooltip(html="This", tooltip="Text to show when hovering")
        card = analysis.create_html_card("This is a component with a tooltip: {0}".format(analysis.html_ref(tt)))


    :param str html: Text to display normally
    :param str tooltip: The tooltip text to show when the cursor hovers over the component
    """

    _component_type_str = 'TOOLTIP'

    def __init__(self, html=None, tooltip=None, _analysis=None, _component_id=None, _component_type=None):

        super(Tooltip, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

        if html is not None:
            self._text = html

        if tooltip is not None:
            self._tooltip_content = tooltip


    @property
    def html(self):
        """The text to show normally for this component.

        :rtype: str
        """
        return self._text

    @html.setter
    def html(self, val):
        self._text = val
        self._update()


    @property
    def tooltip(self):
        """The tooltip text to show when the cursor hovers over the component

        :rtype: str
        """
        return self._tooltip_content

    @tooltip.setter
    def tooltip(self, val):
        self._tooltip_content = val
        self._update()



    def _fields(self):
        return super(Tooltip, self)._fields() + [ 'text', 'tooltip_content' ]
