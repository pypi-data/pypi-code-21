"""
this example equivalent to following html
<head>
    <title>html type</title>
    <style type="text/css">
        span { color: red; }
        button { background-color: orange; }
    </style>
</head>
<body>
    <img src="static/icooon-mono-soy1.png" width="50" height="50">
    <br>
    <a href="http://www.tornadoweb.org/">tornado</a>
    <fieldset>
        <legend>this is legend</legend>
        <span>this is span</span>
    </fieldset>
    <input type="text" id="input1" value="initValue">
    <button id="btn1" class="cls1" onclick="self.on_btn1">btn1</button>
</body>
"""

import os

from dominter.dom import Window, start_app


class MyWindow(Window):
    def __init__(self):
        super(MyWindow, self).__init__()
        document = self.document
        tag = document.tag
        document.head.elements = [
            tag('title _="html type"'),
            tag('style type="text/css" _="\
              span { color: red; } \
              button { background-color: orange; }"'
                ),
        ]
        document.body.elements = [
            tag('img src="static/icooon-mono-soy1.png" width="50" height="50"'),
            tag('br'),
            tag('a href="http://www.tornadoweb.org/" _="tornado"'),
            tag('fieldset', elements=[
                tag('legend _="this is legend"'),
                tag('span _="this is span"')
                ]),
            tag('input type="text" id="input1" value="initValue"'),
            tag('button id="btn1" class="cls1" _="btn1"', onclick=self.on_btn1)
        ]
        self.input1 = document.getElementById('input1')
        self.btn1 = document.getElementById('btn1')

    def on_btn1(self, ev):
        self.input1.value = 'changed!'


if __name__ == "__main__":
    win = MyWindow()    # http://localhost:8888/index.html
    start_app(win,
              template_path=os.path.dirname(__file__),
              static_path=os.path.join(os.path.dirname(__file__), 'static'))
