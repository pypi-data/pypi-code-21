from math import sqrt

SHAPE = u'shape'


class Point(object):
    def __init__(self,
                 point_or_x,
                 y=None):
        u"""
        2D point object.

        If a Point instance is supplied as the first parameter,
        it's just returned. e.g. Point(point_instance)

        If an (x, y) tuple is provided, the values are used to
        create the instance. e.g. Point((x, y))

        If x and y are supplied in point_or_x and y, then they're
        used to create the object. e.g. Point(x, y)

        :param point_or_x: x coordinate, (x, y) tuple or a Point instance
        :param y: y_coordinate
        """
        if isinstance(point_or_x, Point):
            self.x = point_or_x.x
            self.y = point_or_x.y
        try:
            self.x = point_or_x[0]
            self.y = point_or_x[1]
        except TypeError:
            self.x = point_or_x
            self.y = y

    def distance_to_point(self,
                          point):
        return sqrt((point.x - self.x) ** 2 + (point.y - self.y) ** 2)


class Shape(object):
    def point_is_inside(self,
                        point):
        raise NotImplementedError(u"Shape class is abstract.")

    def point_is_outside(self,
                         point):
        return not self.point_is_inside(point)


class Rectangle(Shape):
    def __init__(self,
                 top_left,
                 bottom_right):
        self.top_left = Point(top_left)
        self.bottom_right = Point(bottom_right)

    def point_is_inside(self,
                        point):
        return ((self.top_left.x <= point.x <= self.bottom_right.x)
                and (self.top_left.y <= point.y <= self.bottom_right.y))


class Circle(Shape):
    def __init__(self,
                 center,
                 radius):
        self.centre = Point(center)
        self.radius = radius

    @property
    def center(self):
        return self.centre

    def point_is_inside(self,
                        point):
        return point.distance_to_point(self.centre) <= self.radius


class Polygon(Shape):
    def __init__(self,
                 *vertices):
        u"""
        :param vertices: a number of Points or (x, y) tuples
        """
        self.vertices = [Point(vertex) for vertex in vertices]

    def point_is_inside(self,
                        point):
        """Adapted from https://stackoverflow.com/a/30436297/2916546"""
        edge_end = self.vertices[-1]
        point_is_inside = False

        for edge_start in self.vertices:
            try:
                a = (edge_start.y > point.y) != (edge_end.y > point.y)
                b = (point.x < (edge_end.x - edge_start.x) * (point.y - edge_start.y) / (edge_end.y - edge_start.y) + edge_start.x)
                if a and b:
                    point_is_inside = not point_is_inside
            except ZeroDivisionError:
                pass
            edge_end = edge_start
        return point_is_inside


class ImageMap(object):

    def __init__(self,
                 map=None):
        u"""
        :param map: Either None, so the mapping is undefined
                    or a dictionary of key to shapes. The shape
                    can be contained inside a secondary
                    dictionary with a key of SHAPE, if it's
                    convenient to store other associated
                    fields (e.g. 'tooltip'.

                    e.g.
                    {'A': Rectangle((10, 10), (20, 20))
                     'B': Rectangle((20, 10), (30, 20))}

                    or

                    {'A': {SHAPE: Rectangle((10, 10), (20, 20)), 'tooltip': 'This is A'}
                     'B': {SHAPE: Rectangle((20, 10), (30, 20)), 'tooltip': 'This is B'}}
        """
        self.map = map if map else {}

    def add_shape(self,
                  key,
                  shape):
        self.map[key] = shape

    def key(self,
            point_or_x,
            y=None):
        u"""
        Returns the key of the first shape that contains
        the point.

        :param point_or_x:
        :param y:
        :return:
        """
        point = Point(point_or_x, y)
        for key, value in self.map.iteritems():

            try:
                shape = value[SHAPE]
            except TypeError:
                shape = value

            if shape.point_is_inside(point):
                return key
        return None

    def value(self,
              key):
        return self.map[key]


def main():

    IMG_KEY_MAP = {u'a': Circle((100, 61), 10),
                   u'b': Rectangle((62, 129), (82, 149)),
                   u'c': Rectangle((30, 168), (49, 186)),
                   u'd': Polygon((10, 10),
                                 (20, 10),
                                 (20, 30),
                                 (40, 30),
                                 (40, 50),
                                 (10, 50))
                   }

    image_map = ImageMap(IMG_KEY_MAP)

    assert image_map.key(90, 51) == None
    assert image_map.key(110, 71) == None
    assert image_map.key(100, 51) == u'a'
    assert image_map.key(100, 71) == u'a'
    assert image_map.key(90, 61) == u'a'
    assert image_map.key(110, 61) == u'a'
    assert image_map.key(62, 129) == u'b'
    assert image_map.key(82, 149) == u'b'
    assert image_map.key(83, 149) == None
    assert image_map.key(35, 170) == u'c'
    assert image_map.key(9, 9) == None
    assert image_map.key(11, 11) == u'd'
    assert image_map.key(21, 11) == None
    assert image_map.key(39, 35) == u'd'

if __name__ == u"__main__":
    main()
