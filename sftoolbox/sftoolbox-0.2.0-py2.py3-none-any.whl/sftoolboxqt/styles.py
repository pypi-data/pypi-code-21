"""different styles to show actions
"""
import functools

from sftoolbox.content import ActionContent, PanelContent
from sftoolboxqt import qtgui
from sftoolboxqt import engine


@engine.register_style_class
class GridStyle(qtgui.QWidget):
    """horizontal layout system
    """
    json_type = 'grid'

    def __init__(self, panel, parent=None):
        super(GridStyle, self).__init__(parent=parent)
        self.panel = panel
        self.item_count = 0
        self.max_lines = 3
        self.row = 0
        self.column = 0
        self.direction = 'vertical'

        layout = qtgui.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def add_content(self, content, show_icons=True, show_text=True):
        from sftoolboxqt.widgets import ContentWidget
        content_widget = ContentWidget(content, show_icons, show_text)

        if self.direction == 'vertical':
            self.layout().addWidget(content_widget, self.row, self.column)
        else:
            self.layout().addWidget(content_widget, self.column, self.row)
        self.item_count += 1
        self.column += 1
        if self.column >= self.max_lines:
            self.column = 0
            self.row += 1


@engine.register_style_class
class HorizontalStyle(qtgui.QWidget):
    """horizontal layout system
    """
    json_type = 'horizontal'

    def __init__(self, panel, parent=None):
        super(HorizontalStyle, self).__init__(parent=parent)
        self.panel = panel
        layout = qtgui.QHBoxLayout()
        self.setLayout(layout)

    def add_content(self, content, show_icons=True, show_text=True):
        from sftoolboxqt.widgets import ContentWidget
        content_widget = ContentWidget(content, show_icons, show_text)
        self.layout().addWidget(content_widget)


@engine.register_style_class
class VerticalStyle(qtgui.QWidget):
    """horizontal layout system
    """
    json_type = 'vertical'

    def __init__(self, panel, parent=None):
        super(VerticalStyle, self).__init__(parent=parent)
        self.panel = panel
        layout = qtgui.QVBoxLayout()
        self.setLayout(layout)

    def add_content(self, content, show_icons=True, show_text=True):
        from sftoolboxqt.widgets import ContentWidget
        content_widget = ContentWidget(content, show_icons, show_text)
        self.layout().addWidget(content_widget)


@engine.register_style_class
class DropdownStyle(qtgui.QWidget):
    """horizontal layout system
    """
    json_type = 'dropdown'

    def __init__(self, panel, parent=None):
        super(DropdownStyle, self).__init__(parent=parent)
        self.panel = panel
        self._content = []
        self._menu = qtgui.QMenu()
        self._menu.aboutToShow.connect(self._handle_about_to_show)

        self._button = qtgui.QPushButton(self.panel.human_label)
        self._button.setMenu(self._menu)
        self._button.setIcon(qtgui.QIcon(self.panel.absolute_icon_filepath))

        layout = qtgui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(self._button)

    def add_content(self, content, show_icons=True, show_text=True):
        self._content.append(content)

    def _handle_run_action(self, action):
        """handle running the action
        """
        if action.is_runnable:
            action.run()

    def _inject_content(self, menu, content_list):
        """add given content to the menu
        """
        for content in content_list:
            if isinstance(content, ActionContent):
                action = content.target_action
                q_action = qtgui.QAction(self)
                if self.panel.show_text:
                    q_action.setText(action.human_label)
                q_action.setToolTip(action.description)
                q_action.setStatusTip(action.description)
                if self.panel.show_icons:
                    if action.absolute_icon_filepath:
                        q_action.setIcon(
                            qtgui.QIcon(action.absolute_icon_filepath))
                q_action.triggered.connect(
                    functools.partial(self._handle_run_action, action))
                menu.addAction(q_action)
            elif isinstance(content, PanelContent):
                panel = content.target_panel
                sub_menu = qtgui.QMenu(panel.human_label)
                self._inject_content(sub_menu, panel.content)
                menu.addMenu(sub_menu)

    def _handle_about_to_show(self):
        """populate the menu
        """
        self._menu.clear()
        self._inject_content(self._menu, self._content)


def create_style(style_type, panel, args=None, kwargs=None):
    """create a style with the given name
    """
    if not args:
        args = []
    if not kwargs:
        kwargs = {}

    for class_ in engine.style_classes_register:
        if class_.json_type == style_type:
            return class_(panel, *args, **kwargs)

    return VerticalStyle(panel, *args, **kwargs)
