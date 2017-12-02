"""
Generate shorthand functions for colorizing strings
"""


from echocolor.colorizer import Colorizer, COLORS


for fg_color in COLORS:
    colorizer = Colorizer(fg_color)
    globals()[colorizer.__name__] = colorizer
    for bg_color in COLORS:
        colorizer = Colorizer(fg_color, bg_color)
        globals()[colorizer.__name__] = colorizer
