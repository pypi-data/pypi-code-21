# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2017 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        mapserver.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     06/10/2017
# -------------------------------------------------------------------------------
from stime import *
from number import *
from filesystem import *
import gdal, gdalconst
import osr, ogr
import numpy as np

# TYPE [chart|circle|line|point|polygon|raster|query]
GEOMETRY_TYPE = {
    ogr.wkb25DBit: "wkb25DBit",
    ogr.wkb25Bit: "wkb25Bit",
    ogr.wkbUnknown: "LINE",  # unknown
    ogr.wkbPoint: "POINT",
    ogr.wkbLineString: "LINE",
    ogr.wkbPolygon: "POLYGON",
    ogr.wkbMultiPoint: "POINT",
    ogr.wkbMultiLineString: "LINE",
    ogr.wkbMultiPolygon: "POLYGON",
    ogr.wkbGeometryCollection: "POLYGON",
    ogr.wkbNone: "NONE",
    ogr.wkbLinearRing: "POLYGON",
    ogr.wkbPoint25D: "POINT",
    ogr.wkbLineString25D: "LINE",
    ogr.wkbPolygon25D: "POLYGON",
    ogr.wkbMultiPoint25D: "POINT",
    ogr.wkbMultiLineString25D: "LINE",
    ogr.wkbMultiPolygon25D: "POLYGON",
    ogr.wkbGeometryCollection25D: "POLYGON"
}


def renderer_v2(geomtype="POINT"):
    geomtype = upper(geomtype)
    if geomtype == "POINT":
        return {
            "forceraster": 0,
            "symbollevels": 0,
            "type": "singleSymbol",
            "enableorderby": 0,
            "symbols": {
                "symbol": {
                    "alpha": 1,
                    "clip_to_extent": 1,
                    "type": "marker",
                    "name": 0,
                    "layer": {
                        "pass": 0,
                        "class": "SimpleMarker",
                        "locked": 0,
                        "prop": [
                            {"k": "angle", "v": 0},
                            {"k": "color", "v": [randint(255), randint(255), randint(255), 255]},
                            {"k": "horizontal_anchor_point", "v": 1},
                            {"k": "joinstyle", "v": "bevel"},
                            {"k": "name", "v": "circle"},
                            {"k": "offset", "v": [0, 0]},
                            {"k": "offset_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "offset_unit", "v": "MM"},
                            {"k": "outline_color", "v": [0, 0, 0, 255]},
                            {"k": "outline_style", "v": "solid"},
                            {"k": "outline_width", "v": 0.26},
                            {"k": "outline_width_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "outline_width_unit", "v": "MM"},
                            {"k": "scale_method", "v": "diameter"},
                            {"k": "size", "v": 2},
                            {"k": "size_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "size_unit", "v": "MM"},
                            {"k": "vertical_anchor_point", "v": 1}
                        ]
                    }  # end layer
                }  # end symbol
            },
            "rotation": "",
            "sizescale": {
                "scalemethod": "diameter"
            }
        }  # end renderer-v2
    elif geomtype == "LINE":
        return {
            "forceraster": 0,
            "symbollevels": 0,
            "type": "singleSymbol",
            "enableorderby": 0,
            "symbols": {
                "symbol": {
                    "alpha": 1,
                    "clip_to_extent": 1,
                    "type": "line",
                    "name": 0,
                    "layer": {
                        "pass": 0,
                        "class": "SimpleLine",
                        "locked": 0,
                        "prop": [
                            {"k": "capstyle", "v": "square"},
                            {"k": "customdash", "v": "5;2"},
                            {"k": "customdash_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "customdash_unit", "v": "MM"},
                            {"k": "draw_inside_polygon", "v": 0},
                            {"k": "joinstyle", "v": "bevel"},
                            {"k": "line_color", "v": [randint(255), randint(255), randint(255), 255]},
                            {"k": "line_style", "v": "solid"},
                            {"k": "line_width", "v": 0.26},
                            {"k": "line_width_unit", "v": "MM"},
                            {"k": "offset", "v": 0},
                            {"k": "offset_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "offset_unit", "v": "MM"},
                            {"k": "use_custom_dash", "v": 0},
                            {"k": "width_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]}
                        ]
                    }  # end layer
                }  # end symbol
            },
            "rotation": "",
            "sizescale": {
                "scalemethod": "diameter"
            }
        }  # end renderer-v2
    elif geomtype == "POLYGON":
        return {
            "forceraster": 0,
            "symbollevels": 0,
            "type": "singleSymbol",
            "enableorderby": 0,
            "symbols": {
                "symbol": {
                    "alpha": 1,
                    "clip_to_extent": 1,
                    "type": "fill",
                    "name": 0,
                    "layer": {
                        "pass": 0,
                        "class": "SimpleFill",
                        "locked": 0,
                        "prop": [
                            {"k": "border_width_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "color", "v": [randint(255), randint(255), randint(255), 75]},
                            {"k": "joinstyle", "v": "bevel"},
                            {"k": "offset", "v": 0},
                            {"k": "offset_map_unit_scale", "v": [0, 0, 0, 0, 0, 0]},
                            {"k": "offset_unit", "v": "MM"},
                            {"k": "outline_color", "v": [0, 0, 0, 255]},
                            {"k": "outline_style", "v": "solid"},
                            {"k": "outline_width", "v": 0.26},
                            {"k": "outline_width_unit", "v": "MM"},
                            {"k": "style", "v": "solid"}
                        ]
                    }  # end layer
                }  # end symbol
            },
            "rotation": "",
            "sizescale": {
                "scalemethod": "diameter"
            }
        }  # end renderer-v2
    return {}


def GDAL_MAPLAYER(filename, layername=None):
    """
    GDAL_MAPLAYER
    """
    maplayer = {}
    ext = justext(filename).lower()
    layername = layername if layername else juststem(filename)

    if ext in ("tif",):
        data = gdal.Open(filename, gdalconst.GA_ReadOnly)
        if data:

            band = data.GetRasterBand(1)
            m, n = data.RasterYSize, data.RasterXSize
            gt, prj = data.GetGeoTransform(), data.GetProjection()
            srs = osr.SpatialReference(prj)

            epsg = srs.ExportToProj4() if srs else "AUTO"
            proj4 = epsg if epsg.startswith("+proj") else "init=%s" % epsg
            proj = re.findall(r'\+proj=(\w+\d*)', proj4)
            proj = proj[0] if proj else ""
            ellps = re.findall(r'\+ellps=(\w+\d*)', proj4)
            ellps = ellps[0] if ellps else ""
            geomtype = "raster"
            nodata = band.GetNoDataValue()
            rdata = band.ReadAsArray(0, 0, 1, 1)
            datatype = str(rdata.dtype)

            # Warning!!
            rdata = band.ReadAsArray(0, 0, n, m)
            minValue, maxValue = np.asscalar(np.nanmin(rdata)), np.asscalar(np.nanmax(rdata))

            del data
            (x0, px, rot, y0, rot, py) = gt
            minx = min(x0, x0 + n * px)
            miny = min(y0, y0 + m * py)
            maxx = max(x0, x0 + n * px)
            maxy = max(y0, y0 + m * py)
            extent = (minx, miny, maxx, maxy)
            other = (px, py, nodata, datatype)
            descr = srs.GetAttrValue('projcs')

            maplayer = {

                "minimumScale": 0,
                "maximumScale": 1e+08,
                "type": geomtype,
                "extent": {"xmin": minx, "ymin": miny, "xmax": maxx, "ymax": maxy},
                "id": layername,  # + strftime("%Y%m%d%H%M%S", None),
                "datasource": filename,
                "keywordList": {"value": {}},
                "layername": layername,
                "geometry": "raster",
                "srs": {
                    "spatialrefsys": {
                        "authid": "",
                        "description": descr,
                        "ellipsoidacronym": ellps,
                        "geographicflag": (srs.IsGeographic() > 0),
                        "proj4": proj4,
                        "projectionacronym": proj,
                        "srid": "",
                        "srsid": ""
                    }
                },
                "customproperties": {},
                "provider": "gdal",
                "noData": {"noDataList": {
                    "bandNo": 1,
                    "useSrcNoData": 0
                }},
                "map-layer-style-manager": {},
                "pipe": {
                    "brightnesscontrast": {"brightness": 0, "contrast": 0},
                    "huesaturation": {"colorizeBlue": 128, "colorizeGreen": 128,
                                      "colorizeOn": 0, "colorizeRed": 255, "colorizeStrength": 255, "grayscaleMode": 0,
                                      "saturation": 0},
                    "rasterrenderer": {
                        "alphaBand": -1,
                        "contrastEnhancement": {
                            "algorithm": "StretchToMinimumMaximum",
                            "maxValue": maxValue,
                            "minValue": minValue
                        },
                        "gradient": "BlackToWhite",
                        "grayBand": 1,
                        "opacity": 1,
                        "rasterTransparency": {},
                        "type": "singlebandgray"
                    },
                    "rasterresampler": {"maxOversampling": 2}
                },
                "blendMode": 0
            }
    elif ext in ("shp", "dbf", "sqlite"):
        data = ogr.OpenShared(filename)
        if data and data.GetLayer(layername):
            layer = data.GetLayer(layername)
            #layername = layer.GetName()
            minx, maxx, miny, maxy = layer.GetExtent()
            geomtype = GEOMETRY_TYPE[layer.GetGeomType()]
            n = layer.GetFeatureCount(True)
            srs = layer.GetSpatialRef()
            descr = srs.GetAttrValue('projcs')
            proj4 = srs.ExportToProj4() if srs else "init=epsg:3857"
            proj = re.findall(r'\+proj=(\w+\d*)', proj4)
            proj = proj[0] if proj else ""
            ellps = re.findall(r'\+ellps=(\w+\d*)', proj4)
            ellps = ellps[0] if ellps else ""
            extent = (minx, miny, maxx, maxy)
            ##fieldnames
            definition = layer.GetLayerDefn()
            n = definition.GetFieldCount()
            fieldnames = [definition.GetFieldDefn(j).GetName() for j in range(n)]

            aliases, defaults, edittypes = [], [], []
            for j in range(len(fieldnames)):
                fieldname = fieldnames[j]
                aliases.append({"field": fieldname, "index": j, "name": ""})
                defaults.append({"field": fieldname, "expression": ""})
                edittypes.append({"widgetv2type": "TextEdit", "name": fieldname, "widgetv2config": {
                    "IsMultiline": 0, "fieldEditable": 1, "constraint": "", "UseHtml": 0, "labelOnTop": 0,
                    "constraintDescription": "", "notNull": 0
                }})

            maplayer = {
                "simplifyAlgorithm": 0,
                "minimumScale": 0,
                "maximumScale": 1e+08,
                "simplifyDrawingHints": 1,
                "minLabelScale": 0,
                "maxLabelScale": 1e+08,
                "simplifyDrawingTol": 1,
                "readOnly": 0,
                "geometry": geomtype,
                "simplifyMaxScale": 1,
                "type": "vector",
                "hasScaleBasedVisibilityFlag": 0,
                "simplifyLocal": 1,
                "scaleBasedLabelVisibilityFlag": 1,
                "extent": {"xmin": minx, "ymin": miny, "xmax": maxx, "ymax": maxy},
                "id": layername + strftime("%Y%m%d%H%M%S", None),  # + "190001010000", #
                "datasource": filename,
                "keywordList": {"value": {}},
                "layername": layername,
                "srs": {
                    "spatialrefsys": {
                        "authid": "",
                        "description": descr,
                        "ellipsoidacronym": ellps,
                        "geographicflag": (srs.IsGeographic() > 0),
                        "proj4": proj4,
                        "projectionacronym": proj,
                        "srid": "",
                        "srsid": ""
                    }
                },
                "provider": {"encoding": "System", "content": "ogr"},
                "map-layer-style-manager": {
                    "current": ""
                },
                "edittypes": {"edittype": edittypes},
                "renderer-v2": renderer_v2(geomtype),  # end renderer-v2
                "labeling": {"type": "simple"},
                "customproperties": {},
                "blendMode": 0,
                "featureBlendMode": 0,
                "layerTransparency": 0,
                "displayfield": "VALUE",
                "label": 0,
                "labelattributes": {
                    "label": {"fieldname": "", "text": "Etichetta"},
                    "family": {"fieldname": "", "name": "MS Shell Dlg 2"},
                    "size": {"fieldname": "", "units": "pt", "value": 12},
                    "bold": {"fieldname": "", "on": 0},
                    "italic": {"fieldname": "", "on": 0},
                    "underline": {"fieldname": "", "on": 0},
                    "strikeout": {"fieldname": "", "on": 0},
                    "color": {"fieldname": "", "red": 0, "blue": 0, "green": 0},
                    "x": {"fieldname": ""},
                    "y": {"fieldname": ""},
                    "offset": {"fieldname": "", "x": 0, "y": 0, "units": "pt", "yfieldname": "", "xfieldname": ""},
                    "angle": {"fieldname": "", "value": 0, "auto": 0},
                    "alignment": {"fieldname": "", "value": "center"},
                    "buffercolor": {"fieldname": "", "red": 255, "blue": 255, "green": 255},
                    "buffersize": {"fieldname": "", "units": "pt", "value": 1},
                    "bufferenabled": {"fieldname": "", "on": ""},
                    "multilineenabled": {"fieldname": "", "on": ""},
                    "selectedonly": {"on": ""}
                },
                "aliases": {"alias": aliases},
                "attributetableconfig": {
                    "actionWidgetStyle": "dropDown",
                    "sortExpression": "",
                    "sortOrder": 0,
                    "columns": {}
                },
                "defaults": {"default": defaults}
            }

    return maplayer


if __name__ == "__main__":
    filename = "/Users/vlr20/Projects/BitBucket/OpenSITUA/projects/project88/points.shp"
    print GDAL_MAPLAYER(filename)
