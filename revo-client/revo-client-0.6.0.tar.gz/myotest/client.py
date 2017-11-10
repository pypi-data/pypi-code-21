import abc
import requests
import fastavro as avro
import logging
import asyncio

from io import BytesIO

from myotest.version import VERSION
from myotest.exception import ClientError, ResourceNotFoundException
from myotest.models import Workout, Profile

logger = logging.getLogger("myotest")


USER_AGENT_VERISON = "python-revo-client/{}".format(VERSION)
PRODUCTION_URL = "https://api.myotest.cloud"
STAGING_URL = "https://api-staging.myotest.cloud"
DEV_URL = "http://localhost:8000"


def wait_async(coroutine):
    """
        Helper function to execute a co-routine code in a new Thread
        This should be use to replace:
        >  await my_function()
        with
        > wait_async(my_function())
        as wait is not available in python notebook
    :param coroutine: co-routine to call
    :return: result of the co-routine call
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)


class Client(object):

    def __init__(self):
        super().__init__()
        self.user_id = None

    @abc.abstractmethod
    async def test(self):
        pass

    @abc.abstractmethod
    async def fetch_resource(self, path, query):
        pass

    @abc.abstractmethod
    async def fetch_avro(self, path):
        pass

    async def get_resource(self, path, query, wrapper_class=None):
        return self._wrap_object(
            await self.fetch_resource(path, query),
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

    async def _workout_query(self, query={}):
        base = dict()
        if self.user_id:
            base["user"] = self.user_id
        else:
            base["user"] = (await self.get_profile()).id
        return {**base, **query}

    async def get_last_workout_with_tags(self, tags, at=None):
        result = await self.fetch_resource(
            "/api/v1/workouts/",
            await self._workout_query({"tag": tags, "at": at}))
        if result["count"] > 0:
            return self._wrap_object(result["results"][0], Workout)
        return None

    async def get_last_workouts_with_tags(self, tags, limit=20, at=None):
        result = await self.fetch_resource(
            "/api/v1/workouts/",
            await self._workout_query({"limit": limit, "tag": tags, "at": at}))
        if result["count"] > 0:
            return self._wrap_object(result["results"], Workout)
        return None

    async def get_last_workout_with_type(self, workout_type, at=None):
        result = await self.fetch_resource(
            "/api/v1/workouts/",
            await self._workout_query({"type": workout_type, "at": at}))
        if result["count"] > 0:
            return self._wrap_object(result["results"][0], Workout)
        return None

    async def get_workout_with_id(self, workout_id):
        return await self.get_resource(
            "/api/v1/workouts/{}/".format(
                workout_id), await self._workout_query(), Workout)

    async def get_last_workouts(self, limit=20, at=None):
        result = await self.fetch_resource(
            "/api/v1/workouts/",
            await self._workout_query({"limit": limit, "at": at}))
        if result["count"] > 0:
            return self._wrap_object(result["results"], Workout)
        return []

    async def get_profile(self, reload=False):
        if not hasattr(self, "_profile") or reload:
            if self.user_id:
                profile = await self.get_resource(
                    "/api/profiles/{}/".format(self.user_id), {}, Profile)
            else:
                profile = await self.get_resource(
                    "/api/profile/", {}, Profile)
            self._profile = profile
        return self._profile

    async def get_slots(self, workout_id):
        slots_json = await self.fetch_resource(
            "/api/workout-validation/{}/".format(workout_id), {})
        if slots_json:
            slot_info = {slot["id"]: slot for slot in slots_json["slots"]}
            return [
                {**slot_info[s["id"]], **s}
                for s in slots_json["validations"]["slots"]]
        else:
            return []

    async def get_slot_with_tags(self, tags, at=None):
        """
        Helper function to get workout with given tags and, if found
        return its first corresponding slot matching tags
        :param tags: list of tags as string
        :param at: optional date
        :return: Slot element
        """
        workout = await self.get_last_workout_with_tags(tags, at=at)
        if workout:
            await workout.load_slots()
            return workout.get_slot_with_tags(tags)
        return None


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

    async def test(self):
        result = await self.fetch_resource("/api/monitor/")
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

    async def fetch_resource(self, path, query={}):
        url = "{}{}".format(self.url, path)
        r = requests.get(url, headers=self.get_headers(), params=query)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            raise ResourceNotFoundException(path)
        else:
            raise ClientError(r.text, code=r.status_code)

    async def fetch_avro(self, avro_url):
        logger.warning(
            "Downloading avro file, this should be avoided in production")
        response = requests.get(avro_url)
        if response.status_code == 200:
            return avro.reader(BytesIO(response.content))
        else:
            raise ClientError(response.text, code=response.status_code)
