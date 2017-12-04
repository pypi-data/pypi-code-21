import serial
import numpy as np
import time
from time import sleep
from .constants import *
from threading import Thread
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Serial(serial.Serial):
    def __init__(self, port):
        serial.Serial.__init__(self, port = port, baudrate = BAUDRATE,
                             stopbits = serial.STOPBITS_ONE, parity = serial.PARITY_NONE,
                                bytesize = serial.EIGHTBITS, timeout = TIMEOUT)

        self.flush()

    def send(self, hex_int):
        self.write([hex_int])
        ans = int.from_bytes(self.read(1), byteorder='big')
        if ans != SYSTEM_RETURN:
            raise Exception()

def printPorts():
    ports = list(serial.tools.list_ports.comports())
    ports = "\n".join([str(port) for port in ports])

    print("Currently avaiable ports are:\n%s"%ports)

def choosePort():
    while True:
        try:
            port = input("Please choose port: ")
            serial = Serial(port)
            return serial
        except Exception as e:
            print(e)

def commandLoop(serial):
    while True:
        try:
            command = input("Command: ")
            if command == "exit":
                break
            exec("serial.send(%s)"%command)
        except Exception as e:
            pass

class Stage():
    def __init__(self, port, plane = None):
        if type(port) is str:
            self.port = Serial(port)
        else:
            self.port = port
        self.plane = plane

        self.ax = None
        self.fig = None
        self.dot = None
        self.currentx = 0
        self.currenty = 0
        self.currentz = 0

        self.break_ = False

    def setOrigin(self):
        self.port.send(X64)
        self.port.send(Y64)
        self.port.send(Z64)

        print("Setting x (Ctrl c if set)...")
        for i in range(8*XTURNS):
            try:
                self.port.send(LEFT)
            except KeyboardInterrupt:
                break
        print("Setting y (Ctrl c if set)...")
        for i in range(8*YTURNS):
            try:
                self.port.send(BACKWARD)
            except KeyboardInterrupt:
                break
        print("Setting z (Ctrl c if set)...")
        for j in range(8*ZTURNS):
            try:
                self.port.send(DOWN)
            except KeyboardInterrupt:
                break

    def move(self, Nsteps, dir_):
        for i in range(Nsteps):
            self.port.send(dir_)

    def getNSteps(self, res):
        if (not type(res) is int) or (res > 9) or (res < 1):
            raise(Exception("Resolution is not an int number. Min value is 1, max is 9."))

        val = int(64 * (9 - res))
        if val == 0:
            return 1
        return val

    def plot(self, plane, x, y, z):
        self.fig = plt.figure()

        self.ax = self.fig.gca(projection='3d')
        self.ax.plot_surface(x, y, z, color = "g")

        xstep = x[0, 1] - x[0, 0]
        ystep = y[1, 0] - y[0, 0]

        x = x.ravel()
        y = y.ravel()
        z = z.ravel()
        bottom = np.zeros_like(z)

        if len(z) < 200:
            self.ax.bar3d(x - 0.5*xstep, y- 0.5*ystep, bottom, xstep*0.9, ystep*0.9, z, shade=True, alpha = 0.9)
        self.dot, = self.ax.plot([self.currentx], [self.currenty], [self.currentz], marker="o", color = "r")

        self.ax.set_xlabel("$x$ ($\mu$m)")
        self.ax.set_ylabel("$y$ ($\mu$m)")
        self.ax.set_zlabel("$z$ ($\mu$m)")

    def scan(self, xlength_um, ylength_um, xres = 8, yres = 8, zres = 9, plane = None):
        self.thread = Thread(target = self.scanThread, args=(xlength_um, ylength_um, xres, yres, zres, plane))
        self.thread.start()

    def plotThread(self):
        while self.dot == None:
            sleep(1)
        while self.thread.is_alive():
            try:
                ani = FuncAnimation(self.fig, self.updatePlot)
                plt.show()
            except KeyboardInterrupt:
                self.break_ = True
                break
            else:
                pass

    def updatePlot(self, i):
        self.dot.set_data([self.currentx], [self.currenty])
        self.dot.set_3d_properties([self.currentz])
        return self.dot,

    def setXStepsPerCall(self, n):
        self.port.send(eval("X%d"%n))

    def setYStepsPerCall(self, n):
        self.port.send(eval("Y%d"%n))

    def setZStepsPerCall(self, n):
        self.port.send(eval("Z%d"%n))

    def scanThread(self, x, y, xres, yres, zres, plane):
        xsteps = self.getNSteps(xres)
        ysteps = self.getNSteps(yres)
        zsteps = self.getNSteps(zres)

        self.setXStepsPerCall(xsteps)
        self.setYStepsPerCall(ysteps)
        self.setZStepsPerCall(zsteps)

        nx = int(round((x / XSTEP) / xsteps, 0))
        ny = int(round((y / YSTEP) / ysteps, 0))

        z = 0

        xdir = RIGHT

        if self.plane != None and plane == None:
            plane = self.plane

        self.plane = plane

        if self.plane != None:
            xmesh = np.arange(0, x, xsteps*XSTEP)
            ymesh = np.arange(0, y, ysteps*YSTEP)
            xmesh, ymesh = np.meshgrid(xmesh, ymesh)
            zmesh = plane.getZ(xmesh, ymesh)
            self.plot(self.plane, xmesh, ymesh, zmesh)

        for i in range(ny):
            if i%2 == 0: xdir = RIGHT
            else: xdir = LEFT
            self.currenty = i*ysteps*YSTEP
            for j in range(nx):
                jj = j
                if xdir == LEFT: jj = nx - j - 1
                if plane != None:
                    self.currentz = zmesh[i, jj]
                    z = zmesh[i, jj] - z
                    nz = int(round((abs(z) / ZSTEP) / zsteps, 0))
                    for k in range(nz):
                        if z > 0:
                            self.port.send(UP)
                        else:
                            self.port.send(DOWN)

                        if self.break_:
                            return None

                    z = self.currentz
                self.currentx = jj*xsteps*XSTEP
                self.port.send(xdir)
            self.port.send(FORWARD)
