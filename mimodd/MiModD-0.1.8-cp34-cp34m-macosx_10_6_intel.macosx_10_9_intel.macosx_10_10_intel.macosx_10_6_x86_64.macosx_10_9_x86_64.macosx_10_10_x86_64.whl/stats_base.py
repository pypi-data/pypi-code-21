from itertools import chain

def fisher_hyper (a,b,c,d):
    p=1.0
    div = chain(range(a+b+1, a+b+c+d+1), range(2, d+1))
    for x,y in ((a,c), (c,d), (b,d)):
        for f in range(x+1,x+y+1):
            # print(p)
            p = p*f
            if p > 1:
                for n in div:
                    p = p/n
                    if p < 1:
                        break
    for n in div:
        p = p/n

    # if p == 0:
    #     print(a,b,c,d)
    return p


def fisher (a,b,c,d, sided=0):
    """sided=0 means right-sided test - the only one implemented here."""

    p = fisher_hyper(a,b,c,d)
    r = p
    while b and c:
        a+=1
        d+=1
        r=r*b*c/(a*d)
        p+=r
        b-=1
        c-=1
    return p


def hexbin (data, x_bin_size, y_bin_size):
    """Bin 2D data into hexagons.

       Tessalate the data plane with hexagons the centers of which are
       x_bin_size apart along the x axis and y_bin_size along the y axis,
       i.e., the distance between neighbouring centers is
       sqrt(xbin_size**2 + ybin_size**2).

       Returns a dictionary with the keys designating 2-dimensional indices
       of the hexagons and the values being lists of x- and y-coordinate of
       the centroid of the data falling into the given hexagon, and the
       number of data points in the hexagon, i.e., [cx, cy, n].
       """
    
    hexbinner = {}
    for x, y in data:
        xbin = x // x_bin_size
        ybin = y // y_bin_size
        if (xbin + ybin) % 2:
            if (x - x_bin_size * xbin)**2 + (y - y_bin_size * (ybin+1))**2 < \
               (x - x_bin_size * (xbin+1))**2 + (y - y_bin_size * ybin)**2:
                hdata = hexbinner.setdefault((xbin, ybin+1), [0, 0, 0])
            else:
                hdata = hexbinner.setdefault((xbin+1, ybin), [0, 0, 0])
        else:
            if (x - x_bin_size * xbin)**2 + (y - y_bin_size * ybin)**2 < \
               (x - x_bin_size * (xbin+1))**2 + (y - y_bin_size * (ybin+1))**2:
                hdata = hexbinner.setdefault((xbin, ybin), [0, 0, 0])
            else:
                hdata = hexbinner.setdefault((xbin+1, ybin+1), [0, 0, 0])
        hdata[0] = hdata[0] + x
        hdata[1] = hdata[1] + y
        hdata[2] += 1
    for hdata in hexbinner.values():
        hdata[0] /= hdata[2]
        hdata[1] /= hdata[2]
    return hexbinner
    
