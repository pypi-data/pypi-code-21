from GenClass import GenClass
import yaml

class AsciiApp(GenClass):
    
    def __init__(self, appyaml: str = ''):
        appdict = {}
        try:
            with open(appyaml) as f:
                appdict = yaml.safe_load(f)

        except Exception:
            pass

        super().__init__(appdict)

    def add_controller(self, ctlr: object) -> None:
        
        # check the app controller
        if self['controller'] == ctlr.__name__:
            self.controller = ctlr()
            return

        # check the frame controllers
        if self['frames'] is None: return
        for frame in self.frames.keys():

            frame = self.frames[frame]
            if frame['controller'] == ctlr.__name__:
                self.frames[frame].controller = ctlr()
                return

            # check the page controllers
            if frame['pages'] is None: continue
            for page in frame.pages.keys():

                page = frame.pages[page]
                if page['controller'] == ctlr.__name__:
                    page.controller = ctlr()
                    return

