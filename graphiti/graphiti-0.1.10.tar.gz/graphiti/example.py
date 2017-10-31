from client import ClientPlainText

import logging
logging.basicConfig(level=logging.DEBUG)

c = ClientPlainText("gg.antrekod.ru")

for x in range(10):
    c.send("test.plain", x)

c.flush(4)
