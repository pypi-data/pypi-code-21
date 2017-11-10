from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from clarusui.layout import Element

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    #loader=FileSystemLoader('/templates/'),
    autoescape=select_autoescape(['html', 'xml'])
)

layout_template = env.get_template('tabs.html')

class Tabs(Element):
    def __init__(self, *childElements, **options):
        super(Tabs, self).__init__(None,**options)
        #self.childElements = childElements
        self._set_child_elements(childElements)

    def _set_child_elements(self, childElements):
        self.childElements = []
        for element in childElements:
            self.childElements.append(element)
        
    def toDiv(self):
        return layout_template.render(tabs=self)

    
        