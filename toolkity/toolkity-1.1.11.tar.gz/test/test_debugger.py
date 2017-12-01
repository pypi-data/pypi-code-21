from toolkit import debugger
import os


def fun():
    os.environ["DEBUG"] = "False"
    debugger()
    print(11111)


fun()