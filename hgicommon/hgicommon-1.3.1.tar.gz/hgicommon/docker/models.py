class Container:
    """
    Model of a Docker container.
    """
    def __init__(self):
        super().__init__()
        self.native_object = None
        self.name = None
