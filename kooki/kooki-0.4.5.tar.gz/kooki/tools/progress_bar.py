import sys

class ProgressBar():

    _bar_length = 20
    _running = False
    _progress = 0
    _message = ''
    _status = ''

    @classmethod
    def new(cls, message=''):

        if cls._running:
            cls._status = 'Abort...\r\n'
            cls._update(cls._progress)

        cls._message = message
        cls._status = ''
        cls._update(0)
        cls._running = True

    @classmethod
    def update(cls, progress):
        cls._update(progress)

    @classmethod
    def finish(cls):
        cls._update(1.0)
        cls._running = False

    @classmethod
    def _update(cls, progress):

        cls._progress = progress

        if isinstance(progress, int):
            progress = float(progress)

        if not isinstance(progress, float):
            progress = 0
            cls._status = 'error: progress var must be float\r\n'

        if progress < 0:
            progress = 0
            cls._status = 'Halt...\r\n'

        if progress >= 1:
            progress = 1
            cls._status = 'Done...\r\n'

        block = int(round(cls._bar_length * progress))
        text = "\r{2}: [{0}] {1:.2f}% {3}".format( "#" * block + "-" * (cls._bar_length - block), progress * 100, cls._message, cls._status)
        sys.stdout.write(text)
        sys.stdout.flush()
