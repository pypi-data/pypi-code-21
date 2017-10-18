class Color(object):
    COMPARISON_THRESHOLD = 0.001

    def __init__(self, r, g, b):
        if not (0 <= r <= 1 and 0 <= g <= 1 and 0 <= b <= 1):
            raise ValueError('args should be in range [0.0; 1.0]')
        self.r = r
        self.g = g
        self.b = b

    def __eq__(self, o):
        return self.distance_to(o) < Color.COMPARISON_THRESHOLD

    def __hash__(self):
        return hash(self.get_tuple())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "%s %s %s" % self.get_tuple()

    def get_tuple(self):
        return self.r, self.g, self.b

    def distance_to(self, c):
        return ((self.r - c.r) ** 2 + (self.g - c.g) ** 2 + (self.b - c.b) ** 2) ** 0.5

    @classmethod
    def with_full_format_tuple(cls, t):
        return cls(t[0] / 255, t[1] / 255, t[2] / 255)

    @classmethod
    def with_tuple(cls, t):
        return cls(t[0], t[1], t[2])
