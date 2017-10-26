import uuid
import sftoolbox


class Content(object):
    """content object can point further to an action
    """

    def __init__(self, project):
        """content
        """
        project.add(self)
        self.idname = str(uuid.uuid4())
        self.project = project
        self.weight = 0
        self.panel_idname = None

    @property
    def panel(self):
        """return panels that this content belongs to
        """
        for panel in self.project.panels:
            if panel.idname == self.panel_idname:
                return panel

    @panel.setter
    def panel(self, value):
        """set the panel
        """
        self.panel_idname = value.idname

    def load_json(self, data):
        """load the json in
        """
        self.panel_idname = data.get('panel')
        self.weight = data.get('weight')
        self.idname = data.get('idname')

    @classmethod
    def from_json(cls, project, data):
        raise NotImplementedError


@sftoolbox.engine.register_content_class
class ActionContent(Content):
    """content pointing to an action
    """
    json_type = 'action'

    def __init__(self, project, target_action_idname=None):
        super(ActionContent, self).__init__(project)
        self.target_action_idname = target_action_idname

    @property
    def target_action(self):
        for action in self.project.actions:
            if action.idname == self.target_action_idname:
                return action

    @target_action.setter
    def target_action(self, value):
        if value:
            self.target_action_idname = value.idname
        else:
            self.target_action_idname = None

    def load_json(self, data):
        super(ActionContent, self).load_json(data)
        self.target_action_idname = data.get('target_action')

    @classmethod
    def from_json(cls, project, data):
        content = cls(project)
        content.load_json(data)
        return content


@sftoolbox.engine.register_content_class
class PanelContent(Content):
    """content pointing a panel
    """
    json_type = 'panel'

    def __init__(self, project, target_panel_idname=None):
        super(PanelContent, self).__init__(project=project)
        self.target_panel_idname = target_panel_idname

    @property
    def target_panel(self):
        for panel in self.project.panels:
            if panel.idname == self.target_panel_idname:
                return panel

    @target_panel.setter
    def target_panel(self, value):
        if value:
            self.target_panel_idname = value.idname
        else:
            self.target_panel_idname = None

    @classmethod
    def from_json(cls, project, data):
        content = cls(project)
        content.load_json(data)
        return content

    def load_json(self, data):
        """load the json in
        """
        super(PanelContent, self).load_json(data)
        self.target_panel_idname = data.get('target_panel')


def from_json(project, data):
    """make a content from the given json data
    """
    json_type = data.get('type')

    for class_ in sftoolbox.engine.content_classes_register:
        if class_.json_type == json_type:
            return class_.from_json(project, data)
