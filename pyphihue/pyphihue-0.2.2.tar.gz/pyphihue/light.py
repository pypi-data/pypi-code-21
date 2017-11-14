import requests


class Light(object):
    """Class for creating and manipulating lights."""
    def __init__(self, bridge, id):
        """Constructor. """
        self.bridge = bridge
        self.id = id
        self.url = bridge.url() + '/lights/' + str(id)

    def __repr__(self):
        """Representation of the Light object."""
        return "Light(bridgeobject, {})".format(self.id)

    def __str__(self):
        """Representation of the Light object."""
        return 'Philips Hue light with id: ' + str(self.id)

    def turnon(self):
        """Turns this light on and returns the response."""
        url = self.url + '/state'
        body = {}
        body['on'] = True
        response = requests.put(url, json=body).json()
        return response

    def turnoff(self):
        """Turns this light off and returns the response."""
        url = self.url + '/state'
        body = {}
        body['on'] = False
        response = requests.put(url, json=body).json()
        return response

    def effect(self, effect):
        """Set the effect of the light and return the response.

        Keyword argument:
        effect - none|colorloop
        """
        valideffects = ['none', 'colorloop']
        if effect in valideffects:
            url = self.url + '/state'
            body = {}
            body['effect'] = effect
            response = requests.put(url, json=body).json()
        else:
            response = [{'error': {'type': 'not a valid effect'}}]
        return response

    def bri(self, bri):
        """Set the brightness of a light and return the response.

        Keyword argument:
        bri - integer on a scale from 1 to 254
        """
        if bri in range(0, 255):
            url = self.url + '/state'
            body = {}
            body['bri'] = bri
            response = requests.put(url, json=body).json()
        else:
            response = [{'error': {'type': 'bri not in range 1 - 254'}}]
        return response

    def rgb(self, r, g, b):
        """Convert rgb to xy, set the lightcolor using xy values and
        return the repsonse.

        Keyword arguments:
        r - red value (0-255)
        g - green value (0-255)
        b - blue value (0-255)
        """
        rgb = [r, g, b]
        url = self.url + '/state'
        body = {}
        for i in range(len(rgb)):
            rgb[i] = float(rgb[i]) / 255
            if rgb[i] > 0.04045:
                rgb[i] = ((rgb[i] + 0.055) / 1.055) ** 2.4
            else:
                rgb[i] = rgb[i] / 12.92
        x = rgb[0] * 0.664511 + rgb[1] * 0.154324 + rgb[2] * 0.162028
        y = rgb[0] * 0.283881 + rgb[1] * 0.668433 + rgb[2] * 0.047685
        z = rgb[0] * 0.000088 + rgb[1] * 0.072310 + rgb[2] * 0.986039
        if x + y + z != 0:
            x = round(x / (x + y + z), 4)
            y = round(y / (x + y + z), 4)
        body['xy'] = [x, y]
        response = requests.put(url, json=body).json()
        return response
