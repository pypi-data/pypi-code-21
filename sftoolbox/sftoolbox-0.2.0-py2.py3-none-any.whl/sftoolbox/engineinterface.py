class Engine(object):
    """engine
    """

    def __init__(self):
        """construct the engine
        """
        self.action_classes_register = []
        self.content_classes_register = []

    def register_action_class(self, class_):
        """register a given action class
        """
        if class_ not in self.action_classes_register:
            self.action_classes_register.append(class_)
        return class_

    def register_content_class(self, class_):
        if class_ not in self.content_classes_register:
            self.content_classes_register.append(class_)
        return class_
