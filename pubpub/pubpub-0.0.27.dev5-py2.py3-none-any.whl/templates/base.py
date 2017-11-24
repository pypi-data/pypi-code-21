class Template():
  def __init__(self, bundle):
    self.bundle = bundle

  def preprocess(self):
    """Preprocess"""
    pass

  def process(self):
    """Needs to be implemented by subclass"""
    pass
