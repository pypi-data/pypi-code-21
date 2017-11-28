from inukshuk import Engine, Template


class Something:
    def widget(self):
        return "WIDGET"

    def bigWidget(self):
        return {'widget': 'BIG WIDGET'}

    def paramWidget(self, param):
        return {'widget': '%s WIDGET' % param.upper()}

    def paramWidget2(self, param1, param2):
        return {'widget': '%s WIDGET' % (' '.join([param1, param2])).upper()}


def test_simple_call():
    engine = Engine()
    tpl = Template('Here is a {{widget()}}')
    tpl._engine = engine
    out = tpl.render(Something())
    assert out == 'Here is a WIDGET'


def test_nested_call():
    engine = Engine()
    tpl = Template('Here is a {{thing.widget()}}')
    tpl._engine = engine
    out = tpl.render({'thing': Something()})
    assert out == 'Here is a WIDGET'


def test_nested_call_in_the_middle():
    engine = Engine()
    tpl = Template('Here is a {{thing.bigWidget().widget}}')
    tpl._engine = engine
    out = tpl.render({'thing': Something()})
    assert out == 'Here is a BIG WIDGET'


def test_nested_param_call():
    engine = Engine()
    tpl = Template('Here is a {{thing.paramWidget("cool").widget}}')
    tpl._engine = engine
    out = tpl.render({'thing': Something()})
    assert out == 'Here is a COOL WIDGET'


def test_multi_param_call():
    engine = Engine()
    tpl = Template('Here is a {{thing.paramWidget2("pretty", "cool").widget}}')
    tpl._engine = engine
    out = tpl.render({'thing': Something()})
    assert out == 'Here is a PRETTY COOL WIDGET'
