import requests

from .base import BaseClient
from overlock.state import client_state


DEFAULT_SOCK_LOCATION = "/run/overlock.sock"


class OverlockRequestsClient(BaseClient):
    def __init__(self, sock_location=DEFAULT_SOCK_LOCATION):
        self._sock_location = sock_location

    def _construct(self, vals):
        r = {
            "version": client_state.version,
            "process_name": client_state.process_name,
        }
        r.update(vals)

        return r

    def _post(self, path, vals):
        requests.post(
            self._loc(path),
            self._construct(vals),
        )

    def _loc(self, path):
        return "http+unix://{:s}/{:s}".format(self._sock_location, path),

    def update_state(self, new_state):
        self._post(
            "/state",
            {"state_update": new_state}
        )

    def update_metadata(self, new_state):
        self._post(
            "/metadata",
            {"device_id": new_state}
        )

    def update_lifecycle(self, key_type, comment):
        self._post(
            "/lifecycle",
            {
                "type": key_type,
                "comment": comment,
            }
        )

    def associate_device(self, device_id):
        self._post(
            "/associate_device",
            {"other_id": device_id},
        )
