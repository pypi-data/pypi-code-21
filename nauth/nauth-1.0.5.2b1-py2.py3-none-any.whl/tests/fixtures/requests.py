import pytest


class FakeRequest(object):
    def __init__(self, url="", data="", auth="", params="", headers="",
                 json="", verify=True):
            self.url = url
            self.data = data
            self.auth = auth
            self.params = params
            self.headers = headers
            self.json = json
            self.verify = verify


@pytest.fixture
def post(monkeypatch, value):
    fp = FakeRequest()

    def post(url, data="", auth="", params="", json="",
             headers="", verify=True):
        fp.url = url
        fp.data = data
        fp.auth = auth
        fp.params = params
        fp.json = json
        fp.headers = headers
        fp.verify = verify
        return value

    monkeypatch.setattr('requests.post', post)
    return fp


@pytest.fixture
def get(monkeypatch, value):
    fg = FakeRequest()

    def get(url, data="", params="", headers="", verify=True):
        fg.url = url
        fg.data = data
        fg.params = params
        fg.headers = headers
        fg.verify = verify
        return value

    monkeypatch.setattr('requests.get', get)
    return fg


@pytest.fixture
def delete(monkeypatch, value):
    fd = FakeRequest()

    def delete(url, data="", params="", headers="", verify=True):
        fd.url = url
        fd.data = data
        fd.params = params
        fd.headers = headers
        fd.verify = verify
        return value

    monkeypatch.setattr('requests.delete', delete)
    return fd
