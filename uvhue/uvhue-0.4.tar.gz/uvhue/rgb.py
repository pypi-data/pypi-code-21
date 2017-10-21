def gamma_correct(color):
    """
    Gamma correct a single color in your rgb tuple.
    """
    if color > 0.04045:
        return pow((color + 0.055) / 1.055, 2.4)
    else:
        return color / 12.92

def gamma_correct_rgb(rgb):
    """
    Gamma correct rgb colors.
    """
    return tuple([ gamma_correct(x) for x in rgb ])

def rgb_to_decimal(rgb):
    """
    Convert rgb format to decimal.
    """
    return tuple([ (x / 255.0) for x in rgb ])

def decimal_to_xyz(rgb):
    """
    Convert decimal format to xyz
    """
    red, green, blue = rgb[0], rgb[1], rgb[2]

    x = red * 0.649926 + green * 0.103455 + blue * 0.197109
    y = red * 0.234327 + green * 0.743075 + blue * 0.022598
    z = red * 0.0000000 + green * 0.053077 + blue * 1.035763

    return (x, y, z)

def xyz_to_xy(xyz):
    """
    Convert xyz tuple to xy
    """
    total = sum(xyz)
    return xyz[0] / total, xyz[1] / total

def rgb_to_xy(rgb):
    """
    Convert a tuple of rgb colors to xy.
    """
    decimal = rgb_to_decimal(rgb)
    decimal = gamma_correct_rgb(decimal)

    xyz = decimal_to_xyz(decimal)
    return xyz_to_xy(xyz)

def is_grey(rgb, threshold=20):
    """
    Return true if an rgb color is a shade of grey.
    """
    return abs(rgb[0] - rgb[1]) <= threshold and abs(rgb[1] - rgb[2]) <= threshold and abs(rgb[2] - rgb[0]) <= threshold
