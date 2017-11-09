"""
dominter
multiple window / multiple-instance, single-instance example
"""
import os

from dominter.dom import Window, start_app


class MyWindow1(Window):
    def __init__(self):
        super(MyWindow1, self).__init__()
        # shortcuts
        document = self.document
        add_body = self.document.body.appendChild

        def br():
            br = self.document.br()
            add_body(br)

        # header ------------------------------------------------------------
        self.title = document.title('THE TITLE1')
        self.document.head.appendChild(self.title)

        # body --------------------------------------------------------------
        self.txt1 = document.text()
        add_body(self.txt1)
        self.btn1 = document.button('test1', onclick=self.on_btn1,
                                    style="background-color: green;")
        add_body(self.btn1)
        br()
        self.txt2 = document.text()
        add_body(self.txt2)
        self.btn2 = document.button('test2', onclick=self.on_btn2)
        add_body(self.btn2)
        br()
        self.clear_btn = document.button('clear', onclick=self.on_clear_btn)
        add_body(self.clear_btn)

    def on_btn1(self, ev):
        self.txt1.value = 'changed'
        self.btn1.textContent = 'this is the button'
        self.btn1.setAttribute("style", "background-color: red;")

    def on_btn2(self, ev):
        self.txt2.value = 'copy:' + self.txt1.value
        self.btn1.setAttribute("style", "background-color: grey;")

    def on_clear_btn(self, ev):
        self.txt1.value = ''
        self.txt2.value = ''
        self.btn1.removeAttribute("style")


class MyWindow2(Window):
    def __init__(self):
        super(MyWindow2, self).__init__()
        # shortcuts
        document = self.document
        add_body = self.document.body.appendChild

        def br():
            br = self.document.br()
            add_body(br)

        # header ------------------------------------------------------------
        self.title = document.title('THE TITLE2')
        self.document.head.appendChild(self.title)

        # body --------------------------------------------------------------
        self.txt1 = document.text()
        add_body(self.txt1)
        self.btn1 = document.button('test1', onclick=self.on_btn1,
                                    style="background-color: yellow;")
        add_body(self.btn1)
        br()
        self.txt2 = document.text()
        add_body(self.txt2)
        self.btn2 = document.button('test2', onclick=self.on_btn2)
        add_body(self.btn2)
        br()
        self.clear_btn = document.button('clear', onclick=self.on_clear_btn)
        add_body(self.clear_btn)

    def on_btn1(self, ev):
        self.txt1.value = 'changed'
        self.btn1.textContent = 'this is the button'
        self.btn1.setAttribute("style", "background-color: orange;")

    def on_btn2(self, ev):
        self.txt2.value = 'copy:' + self.txt1.value
        self.btn1.setAttribute("style", "background-color: wheat;")

    def on_clear_btn(self, ev):
        self.txt1.value = ''
        self.txt2.value = ''
        self.btn1.removeAttribute("style")


if __name__ == "__main__":
    start_app((MyWindow1(),    # window instance for single-instance
               MyWindow2,      # window class for multiple-instance
               ))
