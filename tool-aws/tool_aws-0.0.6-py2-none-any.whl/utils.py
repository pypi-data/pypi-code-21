from pyproj import Proj, transform


def reprojectBBox(bbox, sridTo, sridFrom=2056):
    if sridTo == sridFrom:
        return bbox
    sridIn = Proj('+init=EPSG:%s' % sridFrom)
    srid_out = Proj('+init=EPSG:%s' % sridTo)
    pLeft = transform(sridIn, srid_out, bbox[0], bbox[1])
    pRight = transform(sridIn, srid_out, bbox[2], bbox[3])
    return pLeft + pRight
