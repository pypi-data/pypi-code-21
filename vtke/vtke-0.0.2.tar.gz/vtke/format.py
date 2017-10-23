import sys
import xml.etree.ElementTree as ET

from vtke.data_array import DataArray

_order = sys.byteorder.title() + 'Endian'


class VtkFile(object):
    type = None

    def to_xml(self, **kwargs):
        root = ET.Element('VTKFile', {
            'type': self.type,
            'version': '1.0',
            'header_type': 'UInt32',
            'byte_order': _order,
        })

        if kwargs.get('compress'):
            root.set('compressor', 'vtkZLibDataCompressor')

        return root

    def to_file(self, file_name, compress=False, **kwargs):
        def indent(elem, level=0):
            # taken from https://norwied.wordpress.com/2013/08/27/307/
            i = "\n" + level * "  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for elem in elem:
                    indent(elem, level + 1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i

        xml = self.to_xml(compress=compress, **kwargs)

        indent(xml)

        ET.ElementTree(xml).write(file_name, **kwargs)


class VtkPolyData(VtkFile):

    def __init__(self, points, connectivity, offsets):
        self.type = 'PolyData'

        self._points = DataArray()
        self._points.name = 'points'
        self._points.type = 'Float32'
        self._points.format = 'binary'
        self._points.num_components = 3
        self._points.data = points

        self._connectivity = DataArray()
        self._connectivity.name = 'connectivity'
        self._connectivity.type = 'Int64'
        self._connectivity.data = connectivity

        self._offsets = DataArray()
        self._offsets.name = 'offsets'
        self._offsets.type = 'Int64'
        self._offsets.data = offsets

    def to_xml(self, **kwargs):
        root = super().to_xml(**kwargs)

        piece = ET.SubElement(ET.SubElement(root, self.type), 'Piece', {
            'NumberOfPoints': str(len(self._points)),
            'NumberOfVerts': '0',
            'NumberOfLines': '0',
            'NumberOfStrips': '0',
            'NumberOfPolys': str(len(self._offsets))
        })

        ET.SubElement(piece, 'PointData')
        ET.SubElement(piece, 'CellData')
        ET.SubElement(piece, 'Verts')
        ET.SubElement(piece, 'Lines')
        ET.SubElement(piece, 'Strips')

        points = ET.SubElement(piece, 'Points')
        points.append(self._points.to_xml(**kwargs))

        polys = ET.SubElement(piece, 'Polys')
        polys.append(self._connectivity.to_xml(**kwargs))
        polys.append(self._offsets.to_xml(**kwargs))

        return root
