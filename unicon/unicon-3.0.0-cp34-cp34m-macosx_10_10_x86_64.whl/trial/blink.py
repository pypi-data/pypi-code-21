"""
    Testing Blinker
"""
from blinker import signal

test = signal('test')
print(test)

def handler_1(sender, *args, **kwargs):
    print('handler_1')
    print('fname is %s' % sender)

def handler_2(sender, *args, **kwargs):
    print('handler_2')
    print('lname is %s' % sender)
    print('args is %s' % str(args))
    print('kwargs is %s' % str(kwargs))

class BigProgram():
    def __init__(self):
        self.name = 'big program'

    def go(self):
        test = signal('test')
        test.connect(handler_1, sender=self)
        test.connect(handler_2)
        test.send(self)

bg = BigProgram()
bg.go()