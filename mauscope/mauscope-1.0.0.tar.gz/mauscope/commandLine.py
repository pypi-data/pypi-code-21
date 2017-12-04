from .core import printPorts, choosePort, commandLoop

printPorts()
serial = choosePort()
commandLoop(serial)
serial.close()
