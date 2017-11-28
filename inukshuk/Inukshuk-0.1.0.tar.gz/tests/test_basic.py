from inukshuk.template import Template


def test_basic1():
    tpl = Template('Here is a {{what}}')
    out = tpl.render({'what': 'rendered template'})
    assert out == 'Here is a rendered template'
