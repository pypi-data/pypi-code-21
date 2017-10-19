
__all__ = [
           'PlotAnim',
]


class PlotAnim(object):
    
    def __init__(self):
        self.handle_line = {}
        self.handle_text = {}
        self.pylab = None
        
    def set_pylab(self, pylab):
        self.pylab = pylab
        
    def assert_pylab_given(self):
        if self.pylab is None:
            msg = 'Please call set_pylab() before plotting.'
            raise ValueError(msg)
        
    def plot(self, name, x, y, *args, **kwargs):
        self.assert_pylab_given()
        if not name in self.handle_line:
            handle, = self.pylab.plot(x, y, *args, **kwargs)
            self.handle_line[name] = handle
        else:
            handle = self.handle_line[name]
            handle.set_data(x, y)

    def text(self, name, x, y, text, *args, **kwargs):
        self.assert_pylab_given()
        if not name in self.handle_text:
            handle = self.pylab.text(x, y, text, *args, **kwargs)
            self.handle_text[name] = handle
        else:
            handle = self.handle_text[name]
            handle.set_text(text)
        
    
