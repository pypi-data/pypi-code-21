
import logging
from Queue import Queue, Empty
from Tkconstants import NORMAL, DISABLED, END

from logging_helper import setup_log_format


class TextHandler(logging.Handler):

    """This class sets up a custom log Handler that allows you to log to a Tkinter Text or ScrolledText widget"""

    def __init__(self,
                 text,
                 *args,
                 **kwargs):

        logging.Handler.__init__(self, *args, **kwargs)

        self.text = text
        self.setFormatter(setup_log_format())
        self.setup_line_colours()
        self.log_queue = Queue()

    def handle(self, record):

        rv = self.filter(record)

        if rv:
            self.log_queue.put(record)

        return rv

    def emit(self, record):

        # Might be a better way to do these .replace methods!
        # Needed to do this to avoid an issue with self.text.insert when there was a single "
        msg = (self.format(record)
               .replace(u'\"', u'"')
               .replace(u'"', u'\"')
               .replace(u"\'", u"'")
               .replace(u'"', u"\'"))

        def append():

            self.text.configure(state=NORMAL)

            try:
                colour_key = msg.split(u' - ')[1][:7].strip()
                self.text.insert(END, msg + u'\n', colour_key)

            except Exception as e:
                logging.error(u'Error inserting: [{msg}]'.format(msg=msg))
                logging.error(e)

            self.text.configure(state=DISABLED)

            # Autoscroll to the bottom (shifted for the blank line)
            self.text.yview(float(self.text.index("end-1c linestart")) - 1)

        # This is necessary because we can't modify the Text from other threads
        # and we don't want this to be blocking!
        self.text.after(0, append)

    def clear(self, start=1.0, end=END):
        self.text.configure(state=NORMAL)
        self.text.delete(start, end)
        self.text.configure(state=DISABLED)

    def setup_line_colours(self):

        tag_colours = {u'DEBUG': u'blue',
                       u'INFO': u'black',
                       u'WARNING': u'orange',
                       u'ERROR': u'red',
                       u'CRITICAL': u'red'}

        for colour in tag_colours:
            self.text.tag_configure(colour, foreground=tag_colours[colour])

    def poll(self):

        try:
            record = self.log_queue.get(timeout=0.01)

            self.emit(record=record)

            self.log_queue.task_done()

        except Empty:
            pass
