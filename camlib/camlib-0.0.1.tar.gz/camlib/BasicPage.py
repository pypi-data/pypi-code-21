from .Page import Page

class BasicPage(Page):
 def __init__(self, name):
  self.metas = {}
  self.metas['lang'] = 'en'
  self.metas['author'] = 'cam'
  self.metas['description'] = 'cam\'s home page'
  self.metas['keywords'] = 'cam cameuh'
  self.metas['title'] = 'UNNAMED PAGE'
  self._name = name
  self._html_controller = None
  self._input_controller = None
 
 def setHTMLController(self, html):
  self._html_controller = html

 def setInputController(self, input):
  self._input_controller = input
 
 def process_input(self):
  if self._input_controller and self._input_controller.process_input:
   self._input_controller.process_input()
 def render(self):
  if not self._html_controller or not self._html_controller.render:
   raise Exception('Page object has no valid HTML render.')
  self._html_controller.render()
