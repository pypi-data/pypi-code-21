from abc import ABCMeta, abstractmethod

from datetime import datetime, time

__all__ = ["Integer", "String", "DateTime", "Date", "Time"]


class BaseObject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def format_input(self, data):
        pass

    @abstractmethod
    def format_output(self, data):
        pass


class Integer(BaseObject):
    def __init__(self):
        pass

    def format_input(self, data):
        try:
            return int(data) if data is not None else None
        except:
            raise TypeError("Integer required for this field")

    def format_output(self, data):
        try:
            return int(data) if data is not None else None
        except:
            return None


class String(BaseObject):
    def __init__(self):
        pass

    def format_input(self, data):
        try:
            return str(data) if data is not None else None
        except:
            raise TypeError("String required for this field")

    def format_output(self, data):
        try:
            return str(data) if data is not None else None
        except:
            return None


class DateTime(BaseObject):
    """
    Attributes:
        tz (timezone): Default timezone
        string_format (int): Default Datetime format string
    """

    def __init__(self, **kwargs):
        self.tz = kwargs.get("tz")
        self.string_format = kwargs.get("string_format")
        if self.string_format is None:
            self.string_format = "%Y-%m-%d %H:%M:%S"  # Default format when string_format not defined

    def format_input(self, data):
        try:
            if data == "now":
                return datetime.now(self.tz) if self.tz else datetime.now()
            else:
                if isinstance(data, int):
                    return datetime.fromtimestamp(data, self.tz) if self.tz \
                        else datetime.fromtimestamp(data)
                elif isinstance(data, str):
                    data = datetime.strptime(data, self.string_format)
                    if self.tz:
                        data = data.astimezone(self.tz)
                    return data
                elif isinstance(data, datetime):
                    return data
        except:
            raise TypeError(
                "datetime Object or valid datetime string required for this field")

    def format_output(self, data):
        try:
            return data.strftime(self.string_format) if data is not None else None
        except:
            return None


class Date(BaseObject):
    """
    Attributes:
        tz (timezone): Default timezone
        string_format (int): Default Date format string
    """

    def __init__(self, **kwargs):
        self.tz = kwargs.get("tz")
        self.string_format = kwargs.get("string_format")
        if self.string_format is None:
            self.string_format = "%Y-%m-%d"  # Default Format When string_format not defined

    def format_input(self, data):
        try:
            if data == "now":
                data = datetime.now(self.tz) if self.tz else datetime.now()
                return data.date()
            else:
                if isinstance(data, int):
                    data = datetime.fromtimestamp(data, self.tz) if self.tz \
                        else datetime.fromtimestamp(data)
                    return data.date()
                elif isinstance(data, str):
                    return datetime.strptime(data, self.string_format).date()
                elif isinstance(data, datetime):
                    return data.date()
        except:
            raise TypeError(
                "datetime Object or valid date string required for this field")

    def format_output(self, data):
        try:
            return data.strftime(self.string_format) if data is not None else None
        except:
            return None


class Time(BaseObject):
    """
    Attributes:
        tz (timezone): Default timezone
    """

    def __init__(self, **kwargs):
        self.tz = kwargs.get("tz", None)

    def format_input(self, data):
        try:
            if data == "now":
                data = datetime.now(self.tz) if self.tz else datetime.now()
                return data.time()
            else:
                h, m, s = data.split(":")
                return time(int(h), int(m), int(s))
        except:
            raise TypeError(
                "datetime Object or valid date string required for this field")

    def format_output(self, data):
        try:
            return str(data) if data is not None else None
        except:
            return None
