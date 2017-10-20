# Copyright (C) 2017 Pier Carlo Chiodi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from logging.config import dictConfig
try:
    import mock
except ImportError:
    import unittest.mock as mock
import pytest
import smtplib

from pierky.buffered_smtp_handler import BufferedSMTPHandler, \
                                         BufferedSMTPHandlerSSL

@pytest.mark.parametrize(
    "kwargs", [
        {
            "args": (("host", 25), "from", ["to1"], "subject"),
            "exp": {
                "mailhost": "host",
                "mailport": 25,
                "smtp_username": None,
                "smtp_password": None,
                "secure": None,
                "fromaddr": "from",
                "subject": "subject",
                "toaddrs": ["to1"]
            }
        }, {
            "args": ("host", "from", ["to1", "to2"], "subject"),
            "exp": {
                "mailhost": "host",
                "mailport": None,
                "smtp_username": None,
                "smtp_password": None,
                "secure": None,
                "fromaddr": "from",
                "subject": "subject",
                "toaddrs": ["to1", "to2"]
            }
        }, {
            "args": ("host", "from", ["to1", "to2"], "subject", ("u", "p")),
            "exp": {
                "mailhost": "host",
                "mailport": None,
                "smtp_username": "u",
                "smtp_password": "p",
                "secure": None,
                "fromaddr": "from",
                "subject": "subject",
                "toaddrs": ["to1", "to2"]
            }
        }, {
            "args": ("host", "from", ["to1", "to2"], "subject", ("u", "p"), ()),
            "exp": {
                "mailhost": "host",
                "mailport": None,
                "smtp_username": "u",
                "smtp_password": "p",
                "secure": (),
                "fromaddr": "from",
                "subject": "subject",
                "toaddrs": ["to1", "to2"]
            }
        }, {
            "args": ("host", "from", ["to1", "to2"], "subject", ("u", "p"), ("key",)),
            "exp": {
                "mailhost": "host",
                "mailport": None,
                "smtp_username": "u",
                "smtp_password": "p",
                "secure": ("key",),
                "fromaddr": "from",
                "subject": "subject",
                "toaddrs": ["to1", "to2"]
            }
        }, {
            "args": ("host", "from", ["to1", "to2"], "subject", ("u", "p"), ("key","cert")),
            "exp": {
                "mailhost": "host",
                "mailport": None,
                "smtp_username": "u",
                "smtp_password": "p",
                "secure": ("key","cert"),
                "fromaddr": "from",
                "subject": "subject",
                "toaddrs": ["to1", "to2"]
            }
        }, {
            "args": ("host", "from", ["to1", "to2"], "subject", None, ("key","cert")),
            "exp": {
                "mailhost": "host",
                "mailport": None,
                "smtp_username": None,
                "smtp_password": None,
                "secure": ("key","cert"),
                "fromaddr": "from",
                "subject": "subject",
                "toaddrs": ["to1", "to2"]
            }
        }, {
            "args": ("host", "from", "to1", "subject"),
            "fail": "toaddrs must be a list of strings"
        }, {
            "args": ("host", "from", [1], "subject"),
            "fail": "toaddrs must be a list of strings"
        }, {
            "args": (("host", 25, 1), "from", ["to1"], "subject"),
            "fail": "mailhost must be a tuple of 2 elements"
        }, {
            "args": ((1, 25), "from", ["to1"], "subject"),
            "fail": "the first element of mailhost must be a string"
        }, {
            "args": (("host", "25"), "from", ["to1"], "subject"),
            "fail": "the second element of mailhost must be an int"
        }, {
            "args": (("host", 25), "from", ["to1"], "subject", "a"),
            "fail": "credentials must be a tuple"
        }, {
            "args": (("host", 25), "from", ["to1"], "subject", ()),
            "fail": "credentials must be a tuple of two elements"
        }, {
            "args": (("host", 25), "from", ["to1"], "subject", None, "a"),
            "fail": "secure must be an empty tuple"
        }, {
            "args": (("host", 25), "from", ["to1"], "subject", None, ("a","b","c")),
            "fail": "secure must be an empty tuple"
        }, {
            "args": (("host", 25), 1, ["to1"], "subject"),
            "fail": "fromaddr must be a string"
        }, {
            "args": (("host", 25), "from", ["to1"], 1),
            "fail": "subject must be a string"
        }
    ]
)
@pytest.mark.parametrize(
    "handler_class", [
        BufferedSMTPHandler, BufferedSMTPHandlerSSL
    ]
)
def test_init(kwargs, handler_class, monkeypatch):

    def fake_create_smtp(*args, **kwargs):
        fake_smtp = mock.Mock()
        return fake_smtp

    monkeypatch.setattr(smtplib, "SMTP", fake_create_smtp)
    monkeypatch.setattr(smtplib, "SMTP_SSL", fake_create_smtp)

    args = kwargs.get("args")
    fail = kwargs.get("fail", None)
    exp = kwargs.get("exp", {})

    if not fail:
        h = handler_class(*args, capacity=1)
        for attr in exp:
            assert exp[attr] == getattr(h, attr)
        logger = logging.getLogger("bufferedemaillogging")
        logger.setLevel(logging.INFO)
        h.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        h.setFormatter(formatter)
        logger.addHandler(h)
        logger.warning("Test")
    else:
        with pytest.raises(Exception, match=r".*" + fail + ".*"):
            handler_class(*args)
