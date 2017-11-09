from dominter.dom import Window, start_app


document = None


def on_btn1(ev):
    txt1 = document.getElementById('txt1')
    btn1 = document.getElementById('btn1')
    txt1.value = 'changed!'
    btn1.textContent = 'this is a button'
    btn1.setAttribute("style", "background-color: red;")


def on_btn2(ev):
    txt1 = document.getElementById('txt1')
    txt2 = document.getElementById('txt2')
    btn1 = document.getElementById('btn1')
    txt2.value = 'copy:' + txt1.value
    btn1.setAttribute("style", "background-color: grey;")


def on_clear_btn(ev):
    txt1 = document.getElementById('txt1')
    txt2 = document.getElementById('txt2')
    btn1 = document.getElementById('btn1')
    btn2 = document.getElementById('btn2')
    txt1.value = ''
    txt2.value = ''
    btn1.removeAttribute("style")
    btn2.removeAttribute("style")


def on_btn3(ev):
    sel1 = document.getElementById('sel1')
    txt3 = document.getElementById('txt3')
    txt3.value = 'value:{} selectedIndex:{}'.format(sel1.value, sel1.selectedIndex)


def on_sel1(ev):
    sel1 = document.getElementById('sel1')
    txt3 = document.getElementById('txt3')
    txt3.value = str(sel1.selectedIndex)


def on_keypress(ev):
    txt3 = document.getElementById('txt3')
    txt3.value = 'keypress'


def on_keydown(ev):
    txt2 = document.getElementById('txt2')
    txt2.value = 'keydown'


def on_keyup(ev):
    txt2 = document.getElementById('txt2')
    txt2.value = 'keyup'


def makewin():
    global document

    window = Window()
    # shortcuts
    document = window.document
    add_head = window.document.head.appendChild
    add_body = window.document.body.appendChild

    def add_br():
        br = document.createElement('br')
        add_body(br)

    # header ------------------------------------------------------------

    title = document.createElement('title')
    title.textContent = 'THE TITLE'
    add_head(title)

    style = document.createElement('style')
    style.setAttribute('type', 'text/css')
    style.textContent = (
        'span { color:green; font-weight:bold; }\n' +
        '.cls1 { color:DarkSeaGreen; font-weight:bold; }\n'
    )
    add_head(style)

    # body --------------------------------------------------------------

    txt1 = document.createElement('input')
    txt1.id = 'txt1'
    txt1.type = 'text'
    add_body(txt1)
    add_br()

    btn1 = document.createElement('button')
    btn1.id = 'btn1'
    btn1.type = 'button'
    btn1.textContent = 'test1'
    btn1.setAttribute("style", "background-color: yellow;")
    btn1.setAttribute("class", "cls1")
    btn1.onclick = on_btn1
    btn1.addEventListener('keypress', on_keypress)
    btn1.addEventListener('keydown', on_keydown)
    btn1.addEventListener('keyup', on_keyup)
    add_body(btn1)
    add_br()

    spn1 = document.createElement('span')
    spn1.id = 'spn1'
    spn1.textContent = 'green background by individual style'
    add_body(spn1)
    add_br()

    txt2 = document.createElement('input')
    txt2.id = 'txt2'
    txt2.type = 'text'
    add_body(txt2)
    add_br()

    btn2 = document.createElement('button')
    btn2.id = 'btn2'
    btn2.type = 'button'
    btn2.textContent = 'test2'
    btn2.onclick = on_btn2
    btn2.setAttribute('class', 'cls1 btn btn-lg')
    add_body(btn2)
    add_br()

    clear_btn = document.createElement('button')
    clear_btn.id = 'clear_btn'
    clear_btn.textContent = 'clear'
    clear_btn.setAttribute('class', "btn btn-sm")
    clear_btn.onclick = on_clear_btn
    add_body(clear_btn)
    add_br()

    chk_tst1 = document.createElement('input')
    chk_tst1.id = 'chk_tst1'
    chk_tst1.type = 'checkbox'
    add_body(chk_tst1)
    add_br()

    sel1 = document.createElement('select')
    sel1.id = 'sel1'
    sel1.selectedIndex = 0
    sel1.value='red'
    sel1.onchange = on_sel1
    opt11 = document.createElement('option')
    opt11.value = 'red'
    opt11.textContent='option red'
    opt12 = document.createElement('option')
    opt12.value = 'green'
    opt12.textContent='option green'
    opt13 = document.createElement('option')
    opt13.value = 'blue'
    opt13.textContent='option blue'
    list([sel1.appendChild(elm) for elm in (opt11, opt12, opt13)])
    add_body(sel1)
    add_br()

    txt3 = document.createElement('input')
    txt3.id = 'txt3'
    txt3.type = 'text'
    txt3.setAttribute('style', 'width:300px;')
    add_body(txt3)
    add_br()

    btn3 = document.createElement('button')
    btn3.id = 'btn3'
    btn3.textContent = 'test3'
    btn3.setAttribute('class', "cls1")
    btn3.onclick = on_btn3
    add_body(btn3)
    add_br()

    return window


def main():
    win = makewin()
    start_app(win)


if __name__ == "__main__":
    main()
