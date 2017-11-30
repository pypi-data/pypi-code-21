

class Event:
    def __init__(self):
        self.targets = set()
        
    def __iadd__(self, other):
        self.targets.add(other)
        
    def __isub__(self, other):
        self.targets.remove(other)
        
    def __call__(self, *args, **kwargs):
        for target in self.targets:
            target(*args, **kwargs)
        
        