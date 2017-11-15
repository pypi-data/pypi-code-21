import traceback as tb
import datetime
import a99

__all__ = ["_LogPart"]

class _LogPart(object):
    """
    This class is a base for XLogDialog and XLogMainWindow
    """
    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Interface

    def keep_ref(self, obj):
        """Adds obj to internal list to keep a reference to it.

        When using PyQt, it happens that the Python object gets garbage-collected even
        when a C++ Qt object still exists, causing a mess
        """
        self._refs.append(obj)
        return obj


    def add_log_error(self, x, flag_also_show=False, E=None):
        """Sets text of labelError."""
        if len(x) == 0:
            x = "(empty error)"
            tb.print_stack()
        x_ = x
        if E is not None:
            a99.get_python_logger().exception(x_)
        else:
            a99.get_python_logger().info("ERROR: {}".format(x_))

        x = '<span style="color: {0!s}">{1!s}</span>'.format(a99.COLOR_ERROR, x)
        self._add_log_no_logger(x, False)
        if flag_also_show:
            a99.show_error(x_)

    def add_log(self, x, flag_also_show=False):
        """Logs to 4 different outputs: conditionally to 3, and certainly to get_python_logger()"""

        self._add_log_no_logger(x, flag_also_show)

        a99.get_python_logger().info(x)

    def _add_log_no_logger(self, x, flag_also_show):
        if hasattr(self, "label_last_log"):
            self.label_last_log.setText(x)
        if hasattr(self, "textEdit_log"):
            te = self.textEdit_log
            te.append("{0!s} -- {1!s}".format(a99.now_str(), x))
        if flag_also_show:
            a99.show_error(x)

    def status(self, x):
        """Sets text of label_last_log"""
        if hasattr(self, "label_last_log"):
            self.label_last_log.setText(x)

    def clear_log(self):
        """Clears text of label_last_log"""
        if hasattr(self, "label_last_log"):
            self.label_last_log.setText("")
