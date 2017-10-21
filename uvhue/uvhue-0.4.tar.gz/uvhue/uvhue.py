from uvhttp.http import Session
import asyncio
import json

class HueException(Exception):
    pass

class Hue(Session):
    """
    Hue client for :mod:`uvhttp`.
    """
    def __init__(self, loop, hue_api, **kwargs):
        self.__lights = None
        self.__hue_id = None
        self.hue_api = hue_api
        super().__init__(10, loop, **kwargs)

    @property
    def hue_api(self):
        """
        Return the Hue API to use for requests.
        """
        return self.__hue_api

    @hue_api.setter
    def hue_api(self, hue_api):
        """
        Set the Hue API server to use.
        """
        if not hue_api.endswith(b'/'):
            hue_api = hue_api + b'/'
        hue_api = hue_api + b'api'

        self.__hue_api = hue_api

    @property
    def hue_id(self):
        """
        The hue id that will be used when interacting with the API.
        """
        if self.__hue_id:
            return self.__hue_id.decode()

    @hue_id.setter
    def hue_id(self, hue_id):
        """
        Set the hue id for the API to use.
        """
        self.__hue_id = hue_id.encode()

    async def link(self):
        """
        Link with a hue bridge. Return a user id that can be used.
        """
        response = await self.post(self.hue_api, data=json.dumps({
            "devicetype": "uvhue#device"
        }).encode())

        if response.status_code != 200:
            raise HueException('Bad status: {}'.format(response.status_code))

        link_response = response.json()

        if not isinstance(link_response, list):
            raise HueException('Bad JSON returned: {} {}'.format(response.text))

        if len(link_response) < 1:
            raise HueException('Bad JSON returned: {}'.format(response.text))

        if 'success' not in link_response[0]:
            raise HueException('Hue API returned an error: {}'.format(link_response[0]['error']['description']))

        self.hue_id = link_response[0]['success']['username']
        return self.hue_id

    async def api(self, method, path, *args, **kwargs):
        """
        Make an API request to hue with the given path.

        The path should be everything except for the common part of the URL.

        For example, ``https://hue/api/1209310239/lights`` becomes
        ``/lights``.
        """
        url = self.hue_api + b'/' + self.hue_id.encode() + b'/' + path
        return await self.request(method, url, *args, **kwargs)

    async def lights(self, refresh=False):
        """
        Return all of the lights in the system. It will be served from
        cache, if available, if the refresh parameter is not False.
        """
        if not self.__lights or refresh:
            response = await self.api(b'GET', b'lights')
            self.__lights = response.json()

        return self.__lights

    async def set_state(self, light, state):
        """
        Set a state for a light.
        """
        data = json.dumps(state).encode()

        response = await self.api(b'PUT', 'lights/{}/state'.format(light).encode(), data=data)

        return response.json() == state

    async def set_states(self, state, refresh=False):
        """
        Set a state for all lights.
        """
        lights = await self.lights(refresh=refresh)

        state_coros = []
        for light in lights:
           state_coros.append(self.set_state(light, state))

        state_results, _ = await asyncio.wait(state_coros)
        result = True
        for state_result in state_results:
           if not state_result:
               result = False

        return result
