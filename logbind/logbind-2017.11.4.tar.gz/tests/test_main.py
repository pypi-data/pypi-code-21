import sys
import logging
import logbind


class CapturingHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        self.capture = kwargs.pop('capture')
        super(CapturingHandler, self).__init__(*args)

    def format(self, record):
        # type: (logging.LogRecord) -> str
        """Don't even need a Formatter class at all."""
        self.capture.append(record)
        return super(CapturingHandler, self).format(record)


def test_main():
    logger = logging.getLogger('a')
    capture = []
    logger.addHandler(CapturingHandler(capture=capture, stream=sys.stdout))
    logger.info('Hello')
    assert not hasattr(capture[-1], 'id')

    l2 = logbind.bind(logger, id=12345)
    l2.info('Hello again')
    assert capture[-1].id == 12345

    l3 = logbind.bind(l2, abc=67890)
    l3.info('Hello yet again')
    assert capture[-1].id == 12345
    assert capture[-1].abc == 67890
