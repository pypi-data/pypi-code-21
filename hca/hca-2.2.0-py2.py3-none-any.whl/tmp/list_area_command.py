import requests

from .config_store import ConfigStore


class ListAreaCommand:

    STAGING_API_URL = "https://upload.dev.data.humancellatlas.org/v1"

    @classmethod
    def add_parser(cls, staging_subparsers):
        list_areas_parser = staging_subparsers.add_parser('list',
                                                          description="List contents of currently selected upload area.")
        list_areas_parser.set_defaults(func=ListAreaCommand)

    def __init__(self, args):
        config = ConfigStore()
        url = self.STAGING_API_URL + "/area/{uuid}".format(uuid=config.current_area())
        params = {}
        response = requests.get(url, params)
        for f in response.json()['files']:
            print(f['name'])
