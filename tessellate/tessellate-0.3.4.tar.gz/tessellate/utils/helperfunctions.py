import logging

logger = logging.getLogger(__name__)
from . import __version__


def write_to_json(data, output, the_indent=4,input_format="builtin"):
    import json
    j2 = json.dumps(data, indent=the_indent)
    f2 = open(output, 'w')
    f2.write("tessellate "+ __version__+" json " +input_format+ "\n")
    print(j2, file=f2)
    f2.close()


def write_to_bson(data, output):
    import bson
    logger.warning("bson cannot encode a list of dictionaries -https://github.com/py-bson/bson/issues/33")
    datadict = {str(idx): dict(key) for idx, key in enumerate(data)}
    logger.critical(datadict)
    # j2=bson.dumps({"A":[1,2,3,4,5,"6", u"7", {"C":u"DS"}]})
    j2 = bson.dumps(datadict)
    f2 = open(output, 'w')
    print(j2, file=f2)
    f2.close()

import colorsys


def generate_colors(n):
    '''Generate n colors and returns a list in hex format
    from http://mc706.com/tip_trick_snippets/1/python-color-wheel/'''
    HSV_tuples = [(x * 1.0 / n + .5, 0.6, 0.5) for x in
                  range(n)]  # Uses HSV colors to find equidistant colors on color wheel
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)  # use colorsys to convert all hsv values to rgb
    RGB_set = []
    for r, g, b in RGB_tuples:
        color = (int(r * 255), int(g * 255), int(b * 255))
        RGB_set.append(color)
    hex_set = []
    for tup in RGB_set:
        hexa = "#%02x%02x%02x" % tup  # convert all values in list to hex for use in html
        hex_set.append(hexa)
    return_set = []
    i = 0
    while len(hex_set) > 0:  # reorder list so each subsequent color is farthest distance from adjacent colors
        if i % 2 == 0:
            return_set.append(hex_set.pop(0))
        else:
            return_set.append(hex_set.pop())
    return return_set


def getorder(ringsize, conformer):
    TTorder5 = {"1E": 8, "1T5": 9, "E5": 10, "4T5": 11, "4E": 12, "4T3": 13, "E3": 14, "2T3": 15, "2E": 16, "2T1": 17,
                "E1": 18, "5T1": 19, "5E": 0, "5T4": 1, "E4": 2, "3T4": 3, "3E": 4, "3T2": 5, "E2": 6,
                "1T2": 7}
    TTorder6 = {"E6": 34, "6E": 4, "E5": 14, "5E": 32, "E4": 30, "4E": 12, "E3": 10, "3E": 28, "E2": 38, "2E": 8,
                "E1": 6, "1E": 36, "2S6": 21, "6S2": 15, "1S5": 25, "5S1": 19, "3S1": 17, "1S3": 23, "1H6": 35,
                "6H1": 5, "6H5": 3, "5H6": 33, "5H4": 31, "4H5": 13, "4H3": 11, "3H4": 29, "3H2": 27,
                "2H3": 9, "2H1": 7, "1H2": 37, "B36": 22, "36B": 16, "B25": 26, "25B": 20, "B14": 18,
                "14B": 24, "4C1": 2, "1C4": 0, "P": 1}
    TTorder7 = {"C  ": 0, "TC ": 1, "B  ": 2, "TB ": 3, "TS3": 4, "P": 5}
    TTorder8 = {"C  ": 0, "CWN": 1, "TCC": 2, "TBC": 3, "B  ": 4, "BB ": 5, "BC ": 6, "TS1": 7, "TS2": 8, "TS3": 9,
                "TS4": 10, "P": 11}
    TTorder5['P'] = 20
    TTorder5['UAP'] = 21
    TTorder5['UAS'] = 22
    TTorder_all = {}
    TTorder_all[5] = TTorder5
    TTorder_all[6] = TTorder6
    TTorder_all[7] = TTorder7
    TTorder_all[8] = TTorder8
    return TTorder_all[ringsize][conformer]


def getcolor(ringsize, conformer):
    TTcolor5 = {"1E": 8, "1T5": 9, "E5": 10, "4T5": 11, "4E": 12, "4T3": 13, "E3": 14, "2T3": 15, "2E": 16, "2T1": 17,
                "E1": 18, "5T1": 19, "5E": 0, "5T4": 1, "E4": 2, "3T4": 3, "3E": 4, "3T2": 5, "E2": 6,
                "1T2": 7}
    TTcolor6 = {"E6": 34, "6E": 4, "E5": 14, "5E": 32, "E4": 30, "4E": 12, "E3": 10, "3E": 28, "E2": 38, "2E": 8,
                "E1": 6, "1E": 36, "2S6": 21, "6S2": 15, "1S5": 25, "5S1": 19, "3S1": 17, "1S3": 23, "1H6": 35,
                "6H1": 5, "6H5": 3, "5H6": 33, "5H4": 31, "4H5": 13, "4H3": 11, "3H4": 29, "3H2": 27,
                "2H3": 9, "2H1": 7, "1H2": 37, "B36": 22, "36B": 16, "B25": 26, "25B": 20, "B14": 18,
                "14B": 24, "4C1": 2, "1C4": 0, "P": 1}
    TTcolor7 = {"C  ": 0, "TC ": 1, "B  ": 2, "TB ": 3, "TS3": 4, "P": 5}
    TTcolor8 = {"C  ": 0, "CWN": 1, "TCC": 2, "TBC": 3, "B  ": 4, "BB ": 5, "BC ": 6, "TS1": 7, "TS2": 8, "TS3": 9,
                "TS4": 10, "P": 11}
    TTcolor5['P'] = 20
    TTcolor5['UAP'] = 21
    TTcolor5['UAS'] = 22
    TTcolor_all = {}
    colors = generate_colors(len(TTcolor5))
    for key in TTcolor5:
        TTcolor5[key] = colors[TTcolor5[key]]
    TTcolor_all[5] = TTcolor5
    colors = generate_colors(len(TTcolor6))
    for key in TTcolor6:
        TTcolor6[key] = colors[TTcolor6[key]]
    TTcolor_all[6] = TTcolor6
    colors = generate_colors(len(TTcolor7))
    for key in TTcolor7:
        TTcolor7[key] = colors[TTcolor7[key]]
    TTcolor_all[7] = TTcolor7
    colors = generate_colors(len(TTcolor8))
    for key in TTcolor8:
        TTcolor8[key] = colors[TTcolor8[key]]
    TTcolor_all[8] = TTcolor8

    return TTcolor_all[ringsize][conformer]


def init_all_pucker_dictionary():
    """ Create an object for placing all pucker data"""
    import tessellate.utils.pucker as puc

    all_pucker_json = {5: {}, 6: {}, 7: {}, 8: {}, "five": {}, "six": {}, "seven": {}, "eight": {}}

    fivep = puc.Pucker("5")
    fivep._init5()
    sixp = puc.Pucker("6")
    sixp._init6()
    sevenp = puc.Pucker("7")
    sevenp._init7()
    eightp = puc.Pucker("8")
    eightp._init8()
    for key in fivep._TTnum:
        all_pucker_json[5][key] = 0

    for key in sixp._TTnum:
        all_pucker_json[6][key] = 0

    for key in sevenp._TTnum:
        all_pucker_json[7][sevenp._map[sevenp._TTnum[key]]] = 0

    for key in eightp._TTnum:
        all_pucker_json[8][eightp._map[eightp._TTnum[key]]] = 0

    return all_pucker_json
