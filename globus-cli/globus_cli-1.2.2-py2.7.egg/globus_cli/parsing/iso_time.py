import click
import time


class ISOTimeType(click.ParamType):
    """
    Enforces time inputs to be in either YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    And that each value is a valid int that falls in the correct range
    """

    name = "ISO_TIME"

    def convert(self, value, param, ctx):
        try:
            time.strptime(value, "%Y-%m-%d %H:%M:%S")
            return value
        except ValueError:
            try:
                time.strptime(value, "%Y-%m-%d")
                return value
            except ValueError:
                self.fail(
                    ("Time {} is not in ISO format of 'YYYY-MM-DD' or "
                     "'YYYY-MM-DD HH:MM:SS'".format(value)))
