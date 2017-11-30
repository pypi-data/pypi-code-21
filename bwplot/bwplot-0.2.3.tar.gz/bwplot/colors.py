'''
Created on Aug 5, 2014

@author: maximmillen
'''

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ColorConverter  # import to_rgb


def cbox(i, gray=False, spectrum="alternate", reverse=False, **kwargs):
    """
    Access a modular list of colors for plotting.
    Defines colours using rgb.
    :param i: (int), index to access color
    :param gray: (bool), if true then color is return as greyscale value
    :param spectrum: (str), choice of spectrum to use
    :param reverse: (bool), reverses the color order
    :param kwargs:
    :return:
    """

    CD = {}
    CD['dark blue'] = (0.0, 0.0, 0.55)  # 0
    CD['greenish blue'] = (0.12, .8, .8)  # 10
    CD['dark green'] = (0.15, 0.35, 0.0)  # 1
    CD['yellow'] = (1.0, 1.0, 0.0)  # 6
    CD['orangish yellow'] = (1.0, 0.9, 0.1)  # 6
    CD['dark red'] = (0.73, 0.0, 0.0)  # 2
    CD['dark purple'] = (0.8, 0.0, 0.8)  # 3
    CD['light green'] = (0.49, 0.64, 0.0)  # 4
    CD['orange'] = (1.0, 0.5, 0.0)  # 5
    CD['light blue'] = (0.5, 0.85, 1.0)  # 6
    CD['pink'] = (1.0, 0.8, 0.8)  # 7
    CD['brown'] = (0.5, 0.3, 0.0)  # 8
    CD['red'] = (0.9, 0.0, 0.0)  # 9

    CD['bluey purple'] = (0.8, 0.85, 1.0)  # 12

    CD['dark grey'] = (0.25, 0.25, 0.25)  #
    CD['mid grey'] = (0.5, 0.5, 0.5)  #
    CD['light grey'] = (0.75, 0.75, 0.75)  #
    CD['black5'] = (0.05, 0.05, 0.05)  #
    CD['black'] = (0.0, 0.0, 0.0)  #
    CD['white'] = (1.0, 1.0, 1.0)  #

    if isinstance(i, int):
        i = i
    elif isinstance(i, float):
        i = int(i)
    elif isinstance(i, str):
        dat = CD[i]
        return dat
    if spectrum == "alternate":
        order = ['dark blue', 'orange', 'light blue', 'dark purple', 'dark green',
                 'bluey purple', 'dark red', 'light green', 'pink', 'brown',
                 'red', 'yellow', 'greenish blue', 'dark grey',
                 'mid grey', 'light grey']
    elif spectrum == "lighten":
        order = ['dark blue', 'dark green', 'dark red', 'brown',
                 'light green', 'orange', 'light blue', 'pink', 'dark purple',
                 'red', 'greenish blue', 'bluey purple', 'yellow',
                 'dark grey', 'mid grey', 'light grey']
    elif spectrum == 'dots':
        order = ['dark blue', 'yellow', 'light blue', 'dark purple', 'dark green', 'orange',
                 'bluey purple', 'dark red', 'light green', 'pink', 'brown',
                 'red', 'greenish blue', 'dark grey',
                 'mid grey', 'light grey']
    elif spectrum == "traffic":
        order = ['dark green', 'orange', 'red']
    else:  # warnings
        order = ['light green', 'orangish yellow', 'orange', 'red', 'black', 'dark grey']

    index = np.mod(i, len(order))
    if reverse:
        index = len(order) - index - 1
    rgb = CD[order[index]]

    gray_value = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]  # calculate the grey scale value

    if gray:
        return gray_value, gray_value, gray_value

    return rgb


# def dep_cbox(i, **kwargs):
# '''
# Define colours by number.
#     Can be plotted either in order of grey scale or in the 'best' order for
#     having a strong grey contrast for only three or four lines
#     :param i: the index to access a colour
#     '''
#     ordered = kwargs.get('ordered', False)
#     options = kwargs.get('options', 'best')
#     grey = kwargs.get('grey', False)
#     CD = {}
#     CD['dark blue'] = (0.0, 0.0, 0.55)  # 0
#     CD['dark green'] = (0.15, 0.35, 0.0)  # 1
#     CD['dark red'] = (0.73, 0.0, 0.0)  # 2
#     CD['dark purple'] = (0.8, 0.0, 0.8)  # 3
#     CD['light green'] = (0.49, 0.64, 0.0)  # 4
#     CD['orange'] = (1.0, 0.5, 0.0)  # 5
#     CD['light blue'] = (0.5, 0.85, 1.0)  # 6
#     CD['pink'] = (1.0, 0.8, 0.8)  # 7
#     CD['brown'] = (0.5, 0.3, 0.0)  # 8
#     CD['red'] = (0.9, 0.0, 0.0)  # 9
#     CD['greenish blue'] = (0.12, .8, .8)  # 10
#     CD['bluey purple'] = (0.8, 0.85, 1.0)  # 12
#     CD['yellow'] = (1.0, 1.0, 0.0)  # 6
#     CD['dark grey'] = (0.25, 0.25, 0.25)  #
#     CD['mid grey'] = (0.5, 0.5, 0.5)  #
#     CD['light grey'] = (0.75, 0.75, 0.75)  #
#     CD['black5'] = (0.05, 0.05, 0.05)  #
#     CD['black'] = (0.0, 0.0, 0.0)  #
#     CD['white'] = (1.0, 1.0, 1.0)  #
#
#     if isinstance(i, int):
#         i = i
#     elif isinstance(i, float):
#         i = int(i)
#     elif isinstance(i, str):
#         dat = CD[i]
#         return dat
#
#     DtoL = ['dark blue', 'dark green', 'dark red', 'brown',
#             'light green', 'orange', 'light blue', 'pink', 'dark purple',
#             'red', 'greenish blue', 'bluey purple', 'yellow',
#             'dark grey', 'mid grey', 'light grey']
#     Best = ['dark blue', 'orange', 'light blue', 'dark purple', 'dark green',
#             'bluey purple', 'dark red', 'light green', 'pink', 'brown',
#             'red', 'yellow', 'greenish blue', 'dark grey',
#             'mid grey', 'light grey']
#     Dots = ['dark blue', 'yellow', 'light blue', 'dark purple', 'dark green', 'orange',
#             'bluey purple', 'dark red', 'light green', 'pink', 'brown',
#             'red', 'greenish blue', 'dark grey',
#             'mid grey', 'light grey']
#     # ll = [0, 5, 2, 4, 1, 6, 3, 7, 8, 11, 9, 12, 10, 13, 14, 15]  # change 11 w 5
#
#     ind = np.mod(i, len(Best))
#     dat = CD[Best[ind]]
#     col = Best[ind]
#     if ordered:  # if ordered is true then the colours are accessed from darkest to lightest
#         ind = np.mod(i, len(DtoL))
#         dat = CD[DtoL[ind]]
#         col = DtoL[ind]
#     if options == "dots":
#         ind = np.mod(i, len(Dots))
#         dat = CD[Dots[ind]]
#         col = Dots[ind]
#     if options == "ordered":
#         ind = np.mod(i, len(DtoL))
#         dat = CD[DtoL[ind]]
#         col = DtoL[ind]
#
#     grey_value = 0.299 * dat[0] + 0.587 * dat[1] + 0.114 * dat[2]  # calculate the grey scale value
#
#     if grey:
#         return (grey_value, grey_value, grey_value)
#
#     return dat


def assessClassicColours():
    cl = ['b', 'g', 'r', 'm', 'y', 'k', 'ivory', 'orange']
    cc = ColorConverter()
    for ss in cl:
        print(ss)
        col = cc.to_rgb(ss)
        print(col)
        grey = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
        print(grey)


def plotter():
    cs = 16
    for j in range(cs):
        a = np.arange(0, 10, 1)
        b = 0.1 * np.ones(10)
        # plt.plot(a, b + j, c=cbox('red', ordered=True), lw=30)
        # plt.plot(a, b + j, c=cbox(j, ordered=True), lw=30)
        plt.plot(a, b + j, c=cbox(j, ordered=False), lw=30)
    plt.show()


def checkGreys():
    cs = 16
    for j in range(cs):
        a = np.arange(0, 5, 1)
        b = 0.1 * np.ones(5)
        # plt.plot(a, b + j, c=cbox('red', ordered=True), lw=30)
        # plt.plot(a, b + j, c=cbox(j, ordered=True), lw=30)
        col = cbox(j, ordered=False)
        grey = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
        plt.plot(a, b + j, c=col, lw=30)
        d = np.arange(4, 9, 1)
        print('grey value: ', grey)
        plt.plot(d, b + j, c=(grey, grey, grey), lw=30)
    plt.show()


if __name__ == '__main__':
    #     plotter()
    checkGreys()
    pass


def spectra(i, **kwargs):
    '''
    Define colours by number.
    Can be plotted either in order of grey scale or in the 'best' order for
    having a strong grey contrast for only three or four lines
    :param i: the index to access a colour
    '''
    ordered = kwargs.get('ordered', False)
    options = kwargs.get('options', 'best')
    grey = kwargs.get('grey', False)
    CD = {}
    CD['dark blue'] = (1.0, 0.0, 0.55)  # 0
    CD['dark green'] = (0.15, 0.35, 0.0)  # 1
    CD['dark red'] = (0.73, 0.0, 0.0)  # 2
    CD['dark purple'] = (0.8, 0.0, 0.8)  # 3
    CD['light green'] = (0.49, 0.64, 0.0)  # 4
    CD['orange'] = (1.0, 0.5, 0.0)  # 5
    CD['light blue'] = (0.5, 0.85, 1.0)  # 6
    CD['pink'] = (1.0, 0.8, 0.8)  # 7
    CD['brown'] = (0.5, 0.3, 0.0)  # 8
    CD['red'] = (0.9, 0.0, 0.0)  # 9
    CD['greenish blue'] = (0.12, .8, .8)  # 10
    CD['bluey purple'] = (0.8, 0.85, 1.0)  # 12
    CD['yellow'] = (1.0, 1.0, 0.0)  # 6
    CD['dark grey'] = (0.25, 0.25, 0.25)  #
    CD['mid grey'] = (0.5, 0.5, 0.5)  #
    CD['light grey'] = (0.75, 0.75, 0.75)  #
    CD['black5'] = (0.05, 0.05, 0.05)  #
    CD['black'] = (0.0, 0.0, 0.0)  #
    CD['white'] = (1.0, 1.0, 1.0)  #

    if isinstance(i, int):
        i = i
    elif isinstance(i, float):
        i = int(i)
    elif isinstance(i, str):
        dat = CD[i]
        return dat

    DtoL = ['dark blue', 'dark green', 'dark red', 'brown',
            'light green', 'orange', 'light blue', 'pink', 'dark purple',
            'red', 'greenish blue', 'bluey purple', 'yellow',
            'dark grey', 'mid grey', 'light grey']
    Best = ['dark blue', 'orange', 'light blue', 'dark purple', 'dark green',
            'bluey purple', 'dark red', 'light green', 'pink', 'brown',
            'red', 'yellow', 'greenish blue', 'dark grey',
            'mid grey', 'light grey']
    Dots = ['dark blue', 'yellow', 'light blue', 'dark purple', 'dark green', 'orange',
            'bluey purple', 'dark red', 'light green', 'pink', 'brown',
            'red', 'greenish blue', 'dark grey',
            'mid grey', 'light grey']
    # ll = [0, 5, 2, 4, 1, 6, 3, 7, 8, 11, 9, 12, 10, 13, 14, 15]  # change 11 w 5

    ind = np.mod(i, len(Best))
    dat = CD[Best[ind]]
    col = Best[ind]
    if ordered:  # if ordered is true then the colours are accessed from darkest to lightest
        ind = np.mod(i, len(DtoL))
        dat = CD[DtoL[ind]]
        col = DtoL[ind]
    if options == "dots":
        ind = np.mod(i, len(Dots))
        dat = CD[Dots[ind]]
        col = Dots[ind]
    if options == "ordered":
        ind = np.mod(i, len(DtoL))
        dat = CD[DtoL[ind]]
        col = DtoL[ind]

    grey_value = 0.299 * dat[0] + 0.587 * dat[1] + 0.114 * dat[2]  # calculate the grey scale value

    if grey:
        return (grey_value, grey_value, grey_value)

    return dat