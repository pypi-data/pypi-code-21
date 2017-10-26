class Engine(object):
    """engine
    """

    def __init__(self):
        self.style_classes_register = []

    def register_style_class(self, class_):
        if class_ not in self.style_classes_register:
            self.style_classes_register.append(class_)
        return class_
