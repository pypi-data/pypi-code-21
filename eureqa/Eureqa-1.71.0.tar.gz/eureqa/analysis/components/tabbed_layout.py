from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST
from eureqa.analysis.analysis_file import AnalysisFile

class TabbedLayout(_Component):
    """
    TabbedLayout component

    Lets users pick to see other components based on titles (works with a few items). Similar to :py:class:`~eureqa.analysis.components.dropdown_layout.DropdownLayout` but suited to smaller lists

    For example::

        t = TabbedLayout()
        t.add_component(title="choice 1", component=HtmlBlock("This is item 1"))
        t.add_component(title="choice 2", component=HtmlBlock("This is item 2"))
        analysis.create_card(t)

    """

    _component_type_str = 'TABBED_LAYOUT'

    def __init__(self, _tabs=None, _analysis=None, _component_id=None, _component_type=None, tab_type="default"):

        tab_types = ["default", "mode_switcher"]
        if not tab_type in tab_types:
            raise Exception(
                "'{value}' is not a valid tab_type. Valid tab_types are: {types}".format(
                    value=val,
                    types=', '.join(tab_types)
                ))

        self._tab_type = tab_type;

        # Tabs to add as soon as we are _register()'d
        # Note that `_queued_tabs` are _Tab objects and `_tabs` are JSON dictionaries
        self._queued_tabs = []

        if _tabs is not None:
            self._queued_tabs = _tabs

        super(TabbedLayout, self).__init__(_analysis=_analysis, _component_id=_component_id,
                                           _component_type=_component_type)

    class _Tab(object):
        def __init__(self, title, component, icon=None):
            """
            :param str title: Title of the tab
            :param ~eureqa.analysis.components.base._Component component: Tab contents, as a Component
            :param ~eureqa.analysis.analysis_file.AnalysisFile icon: Tab icon (optional) -- must be a file containing an image
            """
            self._title = title
            self._component = component
            self._icon = icon

        def _register(self, analysis):
            if self._icon is not None and not isinstance(self._icon, AnalysisFile):
                self._icon = AnalysisFile.create(analysis, self._icon)

        def __repr__(self):
            return repr([self._title, self._component, str(self._icon)[:32] if self._icon else self._icon])

        def _to_json(self):
            ret = {
                "label": self._title,
                "icon_file_id": self._icon._file_id if getattr(self, "_icon", None) is not None else None
            }
            if hasattr(self._component, "_component_id"):
                ret["component_id"] = self._component._component_id
            return ret

    def _ensure_tabs(self):
        if not hasattr(self, "_tabs"):
            self._tabs = []
        if not hasattr(self, "_tab_components"):
            self._tab_components = []
            for tab_json in self._tabs:
                tab = TabbedLayout._Tab(tab_json["label"], _Component._get(_analysis=self._analysis,
                                                            _component_id=tab_json["component_id"]))
                tab._icon = AnalysisFile(self._analysis, tab_json["icon_file_id"])
                self._tab_components.append(tab)

    def add_component(self, title, component, icon=None):
        """
        Add a new tab containing a new component

        :param str title: Title of the tab
        :param ~eureqa.analysis.components.base._Component component: Tab contents, as a Component
        :param ~eureqa.analysis.analysis_file.AnalysisFile icon: Tab icon (optional) -- must be a file containing an image
        """
        new_tab = TabbedLayout._Tab(title, component, icon)

        if hasattr(self, "_analysis") and hasattr(new_tab, "_component_id"):
            new_tab._associate(self._analysis)
            self._ensure_tabs()
            self._tabs.append(new_tab._to_json())
            self._tab_components.append(new_tab)
        else:
            self._queued_tabs.append(new_tab)

    def _walk_children(self):
        for c in getattr(self, "_tab_components", []):
            yield c._component
        for c in self._queued_tabs:
            yield c._component

    def _register(self, analysis):
        super(TabbedLayout, self)._register(analysis)
        self._ensure_tabs()
        for new_tab in self._queued_tabs:
            new_tab._register(analysis)
            self._tabs.append(new_tab._to_json())
            self._tab_components.append(new_tab)
        self._queued_tabs = []

    def _fields(self):
        return super(TabbedLayout, self)._fields() + [ 'tabs', 'tab_type' ]
