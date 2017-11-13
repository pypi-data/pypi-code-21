import ipywidgets as widgets
from traitlets import Unicode, validate, List, Tuple, Int, All
import numpy as np

class GameGrid(widgets.DOMWidget):
    _view_name = Unicode('GameGridView').tag(sync=True)
    _view_module = Unicode('gamegrid').tag(sync=True)
    _view_module_version = Unicode('0.5.0').tag(sync=True)
    _model_name = Unicode('GameGridModel').tag(sync=True)
    _model_module = Unicode('gamegrid').tag(sync=True)
    _model_module_version = Unicode('0.5.0').tag(sync=True)
    _grid = List([[]]).tag(sync=True)
    _images = List([
        "https://brifly.github.io/python-lessons-images/diamond.png",
        "https://brifly.github.io/python-lessons-images/wdiamond.png",
        "https://brifly.github.io/python-lessons-images/precious-stone.png",
        "https://brifly.github.io/python-lessons-images/jewels.png",
        "https://brifly.github.io/python-lessons-images/gem.png"   
    ]).tag(sync=True)
    _selected = List(Tuple().tag(sync=True), []).tag(sync=True)
    _is_overlay_on = Bool(false).tag(sync=True)
    _overlay_message = Unicode('').tag(sync=True)
    
    def __init__(self, **kwargs):
        super(GameGrid, self).__init__(**kwargs)
        self._click_handlers = widgets.CallbackDispatcher();
        self.on_msg(self._handle_click_msg);
    
    def on_click(self, callback, remove=False):
        self._click_handlers.register_callback(lambda s, a: callback(self, a['row'],a['col']), remove=remove)
    

    @property
    def data(self):
        return np.array(self._grid)
        
    @data.setter
    def data(self, arr):
        self._grid = arr.tolist()
        
    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, images):
        self._images = images

    @property    
    def selected(self):
        return self._selected
    
    def is_selected(self, point):
        return point in self._selected
    
    def toggle_select(self, point):        
        # Copy the list so that it forces an update
        newList = self._selected[:]
        if(point in newList):
            newList.remove(point)
        else:
            newList.append(point)
            
        self._selected = newList
    
    @property
    def is_overlay_on(self):
        return _is_overlay_on
            
    def _handle_click_msg(self, _, content, buffers):
        if content.get('event', '') == 'click':
            self._click_handlers(self, content)