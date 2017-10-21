from nose.tools import *
from uvhttp.utils import HttpServer
from sanic.response import json
import os
import hashlib

class HueServer(HttpServer):
    def press_button(self):
        self.is_pressed = True

    def add_user(self):
        user = hashlib.md5(os.urandom(8)).hexdigest()
        self.valid_users.append(user)
        return user

    def add_routes(self):
        super().add_routes()

        self.is_pressed = False
        self.valid_users = []

        self.lights = {
            "1": {
                "state": {
                    "on": True,
                    "bri": 144,
                    "hue": 13088,
                    "sat": 212,
                    "xy": [0.5128,0.4147],
                    "ct": 467,
                    "alert": "none",
                    "effect": "none",
                    "colormode": "xy",
                    "reachable": True
                },
                "type": "Extended color light",
                "name": "Hue Lamp 1",
                "modelid": "LCT001",
                "swversion": "66009461",
                "pointsymbol": {
                    "1": "none",
                    "2": "none",
                    "3": "none",
                    "4": "none",
                    "5": "none",
                    "6": "none",
                    "7": "none",
                    "8": "none"
                }
            },
            "2": {
                "state": {
                    "on": False,
                    "bri": 0,
                    "hue": 0,
                    "sat": 0,
                    "xy": [0,0],
                    "ct": 0,
                    "alert": "none",
                    "effect": "none",
                    "colormode": "hs",
                    "reachable": True
                },
                "type": "Extended color light",
                "name": "Hue Lamp 2",
                "modelid": "LCT001",
                "swversion": "66009461",
                "pointsymbol": {
                    "1": "none",
                    "2": "none",
                    "3": "none",
                    "4": "none",
                    "5": "none",
                    "6": "none",
                    "7": "none",
                    "8": "none"
                }
            }
        }

        self.app.add_route(self.link, '/api', methods=['POST'])
        self.app.add_route(self.get_lights, '/api/<user>/lights')
        self.app.add_route(self.set_state, '/api/<user>/lights/<light>/state', methods=['PUT'])

    def link(self, request):
        assert_in('devicetype', request.json)
        if not self.is_pressed:
            return json([
                {
                    "error": {
                        "type":101, "address": "", "description": "link button not pressed"
                    }
                }
            ])
        else:
            self.is_pressed = False
            return json([
                {
                    "success": {
                        "username": self.add_user()
                    }
                }
            ])

    def get_lights(self, request, user):
        if user not in self.valid_users:
            return json([
                {
                    "error": {
                        "type": 1,
                        "address": "/",
                        "description": "unauthorized user"
                    }
                }
            ])
       
        return json(self.lights)

    def set_state(self, request, user, light):
        if user not in self.valid_users:
            return json([
                {
                    "error": {
                        "type": 1,
                        "address": "/",
                        "description": "unauthorized user"
                    }
                }
            ])

        self.lights[light]["state"].update(request.json)
        return json(request.json)
