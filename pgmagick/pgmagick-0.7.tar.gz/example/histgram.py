import time
from pgmagick import Image, Color, Geometry

# im = Image('X.jpg')


for i in range(10000):
    redColor = Color('red')
    im = Image(Geometry(30, 20), redColor)
    histogram = im.colorHistogram()

    for packet in histogram:
        color, count = packet.key(), packet.data()
        print(color.redQuantum(), color.greenQuantum(), color.blueQuantum(), color.alpha(), count)
    time.sleep(0.1)
