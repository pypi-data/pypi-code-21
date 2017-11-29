#!/usr/bin/python2
# encoding=utf-8
import json


class AttrDict(dict):

    """
    Use dict key as attr

    **examples**

    .. code-block:: python
        :linenos:

        data = Attrdict()

        # after two lines are equal statement
        data.key1 = 1
        data["key1"] = 1


        # defaut value also is Attrdict after line is allowed
        data.key2.key.key.key = 5

        # if plus or minus a number the default value is 0
        data.key3 += 5
        assest(data.key2 == 5)

    enjoys!!!
    """

    def __init__(self, dic={}, json_string=None, *args, **kwargs):
        for arg in args:
            for var in arg:
                self[var[0]] = var[1]
        for key in kwargs:
            self[key] = kwargs[key]
        for key in dic:
            self[key] = dic[key]
        if json_string:
            dic = json.loads(json_string)
        for key in dic:
            self[key] = dic[key]

    def __getattr__(self, key):
        if key not in self:
            self[key] = AttrDict()
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    def __delitem__(self, key):
        if key not in self:
            return
        dict.__delitem__(self, key)

    def __getitem__(self, key):
        if key not in self:
            self[key] = AttrDict()
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if type(value) == dict:
            value = AttrDict(**value)
        if type(value) == list:
            values = []
            for item in value:
                if type(item) == dict:
                    values.append(AttrDict(**item))
                else:
                    values.append(item)
            value = values

        dict.__setitem__(self, key, value)

    def dict(self):
        """
        return dict object of current instance

        Returns:
            * dict: convert from current instance
        """
        res = {}
        for var in self:
            value = self[var]
            if isinstance(value, AttrDict):
                value = value.dict()
            if isinstance(value, list):
                values = []
                for item in value:
                    if isinstance(item, AttrDict):
                        values.append(item.dict())
                    else:
                        values.append(item)
                value = values
            res[var] = value
        return res

    def __getstate__(self):
        return self.dict()

    def __setstate__(self, state):
        pass

    def __add__(self, other):
        if not self:
            return other
        raise ValueError("Dict not empty.")

    def __sub__(self, other):
        if not self:
            return -other
        raise ValueError("Dict not empty.")

    def __str__(self):
        return super(AttrDict, self).__str__()

    def __unicode__(self):
        return super(AttrDict, self).__str__()

    def __copy__(self):
        import copy
        return type(self)(copy.copy(self.dict()))

    def __deepcopy__(self, memo):
        from copy import deepcopy
        return type(self)(deepcopy(self.dict()))

    def __reduce__(self):
        return super(AttrDict, self).__reduce__()

# function


def get_pickle(filename):
    """
    Load file as pickle object

    Args:
        * filename (string): local system filename

    Returns:
        * object: if file is pickled data else None
    """
    import os
    import pickle
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
            return data
    except Exception:
        return None


def put_pickle(data, filename):
    """
    Save object as pickle to filename

    Args:
        * data (object): any can pickled object
        * filename (string): local system filename
    """
    import os
    import pickle
    filename = os.path.abspath(filename)
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def get_json(filename):
    """
    Load file as pickle object

    Args:
        * filename (string): local system filename

    Returns:
        * object: if file is json data else None
    """
    import os
    import json
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, "rb") as f:
            data = json.loads(f.read())
            return data
    except Exception:
        return None


def put_json(data, filename, indent=None):
    """
    Save object as json string to filename

    Args:
        * data (object): any can jsoned object
        * filename (string): local system filename
        * indent (None, optional): json indent width default None
    """
    import os
    import json
    filename = os.path.abspath(filename)
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=indent))


def md5(data=None, filename=None):
    '''
    get data or file md5 checksum

    Args:
        * data (string, optional): string
        * filename (string, optional): local system filename

    Returns:
        * string: md5 checksum
    '''
    import hashlib
    m = hashlib.md5()
    if data:
        m.update(data)
    if filename:
        with open(filename, "rb") as f:
            while True:
                block = f.read(16 * 1024)
                if not block:
                    break
                m.update(block)
    return m.hexdigest()


def sha1(data=None, filename=None):
    '''
    get data or file sha1 checksum

    Args:
        * data (string, optional): string
        * filename (string, optional): local system filename

    Returns:
        * string: sha1 checksum
    '''
    import hashlib
    m = hashlib.sha1()
    if data:
        m.update(data)
    if filename:
        with open(filename, "rb") as f:
            while True:
                block = f.read(16 * 1024)
                if not block:
                    break
                m.update(block)
    return m.hexdigest()


def is_number(number):
    '''
    Test parameter is number True or False

    Args:
        * number (TYPE): any object

    Returns:
        * bool: True if number is float value or False
    '''
    try:
        float(number)
        return True
    except Exception:
        return False


def number(num):
    '''
    convert parameter to float or None

    Args:
        * num (TYPE): any object

    Returns:
        * float: num float value or None
    '''
    try:
        return float(num)
    except Exception:
        return None


def length(string):
    '''
    Get true size of string or char, char might be 1 or 2, string accumulate all of char

    **example**

    .. code-block:: python
        :linenos:

        dandan.value.length("test string") == 11
        dandan.value.length("测试字符串") == 10
        dandan.value.length("测试字符串 test string") == 22

    Args:
        string (string or char): requested

    Returns:
        int: size of string or char
    '''
    if len(string) == 0:
        return 0
    if len(string) > 1:
        accumulate = 0
        for char in string:
            accumulate += length(char)
        return accumulate

    import unicodedata
    if unicodedata.east_asian_width(string) in {'F', 'W', 'A'}:
        return 2
    else:
        return 1
