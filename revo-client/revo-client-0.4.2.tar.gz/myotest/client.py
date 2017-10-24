import abc
import requests
import fastavro as avro
import logging

from io import BytesIO

from myotest.version import VERSION
from myotest.exception import ClientError, ResourceNotFoundException
from myotest.models import Workout, Profile

logger = logging.getLogger("myotest")


USER_AGENT_VERISON = "python-revo-client/{}".format(VERSION)
PRODUCTION_URL = "https://api.myotest.cloud"
STAGING_URL = "https://api-staging.myotest.cloud"
DEV_URL = "http://localhost:8000"


class Client(object):

    def __init__(self):
        super().__init__()
        self.user_id = None

    @abc.abstractmethod
    def test(self):
        pass

    @abc.abstractmethod
    def fetch_resource(self, path, query):
        pass

    @abc.abstractmethod
    def fetch_avro(self, path):
        pass

    def get_resource(self, path, query, wrapper_class=None):
        return self._wrap_object(
            self.fetch_resource(path, query),
            wrapper_class=wrapper_class
        )

    def _wrap_object(self, json, wrapper_class=None):
        if isinstance(json, dict):
            return wrapper_class(client=self, json=json)
        elif isinstance(json, list):
            return [self._wrap_object(x, wrapper_class=wrapper_class)
                    for x in json]
        elif json is None:
            return None
        raise ValueError("Unknown type to wrap")

    def _workout_query(self, query={}):
        base = dict()
        if self.user_id:
            base["user"] = self.user_id
        else:
            base["user"] = self.get_profile().id
        return {**base, **query}

    def get_last_workout_with_tags(self, tags, at=None):
        result = self.fetch_resource(
            "/api/v1/workouts/", self._workout_query({"tag": tags, "at": at}))
        if result["count"] > 0:
            return self._wrap_object(result["results"][0], Workout)
        return None

    def get_workout_with_id(self, workout_id):
        return self.get_resource(
            "/api/v1/workouts/{}/".format(
                workout_id), self._workout_query(), Workout)

    def get_last_workouts(self, limit=20, at=None):
        result = self.fetch_resource(
            "/api/v1/workouts/",
            self._workout_query({"limit": limit, "at": at}))
        if result["count"] > 0:
            return self._wrap_object(result["results"], Workout)
        return []

    def get_profile(self, reload=False):
        if not hasattr(self, "_profile") or reload:
            if self.user_id:
                profile = self.get_resource(
                    "/api/profiles/{}/".format(self.user_id), {}, Profile)
            else:
                profile = self.get_resource(
                    "/api/profile/", {}, Profile)
            self._profile = profile
        return self._profile

    def get_slots(self, workout_id):
        slots_json = self.fetch_resource(
            "/api/workout-validation/{}/".format(workout_id), {})
        if slots_json:
            slot_info = {slot["id"]: slot for slot in slots_json["slots"]}
            return [
                {**slot_info[s["id"]], **s}
                for s in slots_json["validations"]["slots"]]
        else:
            return []


class RemoteClient(Client):
    def __init__(self, token, server=None, user_id=None):
        super().__init__()
        assert token is not None

        if server == "staging":
            self.url = STAGING_URL
        elif server == "production":
            self.url = PRODUCTION_URL
        elif server == "dev":
            self.url = DEV_URL
        else:
            self.url = server or PRODUCTION_URL

        self.authorization = "Token {}".format(token)
        self.user_id = user_id

    def test(self):
        result = self.fetch_resource("/api/monitor/")
        if isinstance(result, dict):
            return {
                "client-version": VERSION,
                "storage": result["storage"]
            }

    def get_headers(self):
        return {
            "user-agent": USER_AGENT_VERISON,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.build_authorization()
        }

    def build_authorization(self):
        return self.authorization

    def fetch_resource(self, path, query={}):
        url = "{}{}".format(self.url, path)
        r = requests.get(url, headers=self.get_headers(), params=query)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            raise ResourceNotFoundException(path)
        else:
            raise ClientError(r.text, code=r.status_code)

    def fetch_avro(self, avro_url):
        logger.warning(
            "Downloading avro file, this should be avoided in production")
        response = requests.get(avro_url)
        if response.status_code == 200:
            return avro.reader(BytesIO(response.content))
        else:
            raise ClientError(response.text, code=response.status_code)
