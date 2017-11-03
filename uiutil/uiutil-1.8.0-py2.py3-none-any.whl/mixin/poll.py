import logging_helper
logging = logging_helper.setup_logging()


class PollMixIn(object):

    def __init__(self,
                 *args,
                 **kwargs):

        super(PollMixIn, self).__init__()

        self._poll_after_id = None

        self._poll()

    def poll(self):
        """
        Override this to poll for changes
        polls every 100 msec unless self.polling_interval is set
        """
        pass

    def _poll(self):
        try:
            self.polling_interval

        except Exception:
            self.polling_interval = 100

        self.poll()
        try:
            self._poll_after_id = self.after(self.polling_interval, self._poll)
        except Exception as e:
            logging.exception(e)  # Log and swallow

    def cancel_poll(self):
        self.after_cancel(self._poll_after_id)
