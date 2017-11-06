###############################################################################
#
#   Copyright: (c) 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core import Date
from ..exceptions import DatafeedError

import win32com.client
import collections
import datetime

__all__ = []

security_error_attrs = ["security", "source", "code",
                        "category", "message", "subcategory"]
security_error = collections.namedtuple("SecurityError", security_error_attrs)

field_error_attrs = ["security", "field", "source",
                     "code", "category", "message", "subcategory"]
field_error = collections.namedtuple("FieldError", field_error_attrs)


# -----------------------------------------------------------------------------
def security_iter(nodearr):
    """
    Provide a security data iterator by returning a tuple of
    (Element, SecurityError) which are mutually exclusive
    """
    if nodearr.Name != "securityData":
        raise RuntimeError("nodearr.Name != 'securityData'")
    if not nodearr.IsArray:
        raise RuntimeError("nodearr.IsArray is False")

    for i in range(nodearr.NumValues):
        node = nodearr.GetValue(i)
        err = get_security_error(node)
        yield (None, err) if err else (node, None)


# -----------------------------------------------------------------------------
def message_iter(evt):
    """
    Provide a message iterator which checks for a response error prior
    to returning
    """
    msg_iter = evt.CreateMessageIterator()
    while msg_iter.Next():
        msg = msg_iter.Message
        if msg.AsElement.HasElement("responseError"):
            raise DatafeedError(msg.AsElement.GetValue("message"))
        yield msg


# -----------------------------------------------------------------------------
def get_sequence_value(node):
    """
    Convert an element with DataType Sequence to a list of dictionaries.
    Note this may be a naive implementation as it assumes that bulk data is
    always a table.
    """
    data, cols = [], []
    for i in range(node.NumValues):
        row = node.GetValue(i)
        # --- get the ordered cols and assume they are constant
        if i == 0:
            cols = [str(row.GetElement(k).Name)
                    for k in range(row.NumElements)]

        values = []
        for cidx in range(row.NumElements):
            elm = row.GetElement(cidx)
            values.append(as_value(elm))

        data.append(dict(zip(cols, values)))

    return data


# -----------------------------------------------------------------------------
def as_value(ele):
    """
    Convert the specified element as a python value.
    """
    dtype = ele.Datatype
    if dtype in (1, 2, 3, 4, 5, 6, 7, 9, 12):
        # --- BOOL, CHAR, BYTE, INT32, INT64, FLOAT32, FLOAT64,
        #     BYTEARRAY, DECIMAL
        return ele.Value
    elif dtype == 8:  # string
        return str(ele.Value)
    elif dtype == 10:  # date
        v = ele.Value
        if v is None:
            return None
        else:
            return Date(year=v.year, month=v.month, day=v.day)
    elif dtype == 11:  # time
        v = ele.Value
        if v is None:
            return None
        else:
            return datetime.time(hour=v.hour, minute=v.minute, second=v.second)
    elif dtype == 13:  # datetime
        v = ele.Value
        if v is None:
            return None
        else:
            return Date(year=v.year, month=v.month, day=v.day,
                        hour=v.hour, minute=v.minute, second=v.second)
    elif dtype == 14:  # Enumeration
        raise NotImplementedError("ENUMERATION "
                                  "data type needs implemented")
    elif dtype == 15:  # SEQUENCE
        return get_sequence_value(ele)
    elif dtype == 16:  # Choice
        raise NotImplementedError("CHOICE data type needs implemented")
    else:
        raise NotImplementedError("Unexpected data type {0:s}. "
                                  "Check documentation".format(dtype))


# -----------------------------------------------------------------------------
def get_child_value(parent, name):
    """
    Return the value of the child element with name in the parent Element
    """
    if parent.HasElement(name):
        return as_value(parent.GetElement(name))
    else:
        return None


# -----------------------------------------------------------------------------
def get_child_values(parent, names):
    """
    Return a list of values for the specified child fields. If field not in
    Element then replace with nan.
    """
    vals = []
    for name in names:
        if parent.HasElement(name):
            vals.append(as_value(parent.GetElement(name)))
        else:
            vals.append(None)
    return vals


# -----------------------------------------------------------------------------
def as_security_error(node, secid):
    """
    Convert the securityError element to a SecurityError.
    """
    if node.Name != "securityError":
        raise RuntimeError("node.Name != 'securityError'")

    src = get_child_value(node, "source")
    code = get_child_value(node, "code")
    cat = get_child_value(node, "category")
    msg = get_child_value(node, "message")
    subcat = get_child_value(node, "subcategory")
    return security_error(security=secid, source=src, code=code,
                          category=cat, message=msg, subcategory=subcat)


# -----------------------------------------------------------------------------
def as_field_error(node, secid):
    """
    Convert a fieldExceptions element to a FieldError or FieldError array.
    """
    if node.Name != "fieldExceptions":
        raise RuntimeError("node.Name != 'fieldExceptions'")

    if node.IsArray:
        return [as_field_error(node.GetValue(k),
                               secid) for k in range(node.NumValues)]
    else:
        fld = get_child_value(node, "fieldId")
        info = node.GetElement("errorInfo")
        src = get_child_value(info, "source")
        code = get_child_value(info, "code")
        cat = get_child_value(info, "category")
        msg = get_child_value(info, "message")
        subcat = get_child_value(info, "subcategory")
        return field_error(security=secid, field=fld, source=src,
                           code=code, category=cat, message=msg,
                           subcategory=subcat)


# -----------------------------------------------------------------------------
def get_security_error(node):
    """
    Return a SecurityError if the specified securityData element has one,
    else return None
    """
    if node.Name != "securityData":
        raise RuntimeError("node.Name != 'securityData'")
    if node.IsArray:
        raise RuntimeError("node.IsArray is True")

    if node.HasElement("securityError"):
        secid = get_child_value(node, "security")
        element = node.GetElement("securityError")
        return as_security_error(element, secid)
    else:
        return None


# -----------------------------------------------------------------------------
def get_field_errors(node):
    """
    Return a list of FieldErrors if the specified securityData element has
    field errors
    """
    if node.Name != "securityData":
        raise RuntimeError("node.Name != 'securityData'")
    if node.IsArray:
        raise RuntimeError("node.IsArray is True")

    nodearr = node.GetElement("fieldExceptions")
    if nodearr.NumValues > 0:
        secid = get_child_value(node, "security")
        return as_field_error(nodearr, secid)
    else:
        return None


# -----------------------------------------------------------------------------
def debug_event(evt):
    print("unhandled event: {0:s}".format(evt.EventType))
    if evt.EventType in [win32com.client.constants.RESPONSE,
                         win32com.client.constants.PARTIAL_RESPONSE]:
        print("messages:")
        for msg in message_iter(evt):
            print(msg.Print)
