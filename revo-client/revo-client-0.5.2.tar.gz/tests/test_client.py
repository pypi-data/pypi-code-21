import asynctest
import unittest

from asynctest import mock
from unittest import mock as sync_mock

import dateutil.parser
import os

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from tests import load_json, load_content
from myotest import Client, wait_async
from myotest.client import ResourceNotFoundException
from myotest.models import ResultData


class MockResponse(object):

    def __init__(self, content_path, code=200, url=None):
        self.status_code = code
        self.file_name = os.path.join(
            '_data', content_path)
        self.url = url

    def json(self):
        return load_json(self.file_name)

    @property
    def content(self):
        return load_content(self.file_name)

    @property
    def text(self):
        return load_content(self.file_name).decode("utf-8")


def requests_side_effects_errors(path, headers={}, params={}):
    raise ResourceNotFoundException(path)


def requests_side_effects(path, headers={}, params={}):
    mapping = {
        "https://api.myotest.cloud/api/v1/workouts/":
            MockResponse("workout-test.json"),
        "https://test.com/data/001.avro":
            MockResponse("slot-1.avro"),
        "https://test.com/data/002.avro":
            MockResponse("mil-1.avro"),
        "https://api.myotest.cloud/api/workout-validation/"
        "e2fe9005-8d86-418e-976b-634ac374ff1e/":
            MockResponse("workout-validation-test.json"),
        "https://api.myotest.cloud/api/profiles/profile-999/":
            MockResponse("profile-999.json"),
        "https://api.myotest.cloud/api/profile/":
            MockResponse("profile-007.json"),
        "https://api.myotest.cloud/api/monitor/":
            MockResponse("monitor.json")
    }
    if path not in mapping:
        return MockResponse("404", code=404, url=path)
    return mapping[path]


def requests_side_effects_no_slots(path, headers={}, params={}):
    mapping = {
        "https://api.myotest.cloud/api/v1/workouts/":
            MockResponse("workout-test-no-slots.json"),
        "https://test.com/data/001.avro":
            MockResponse("slot-1.avro"),
        "https://test.com/data/002.avro":
            MockResponse("mil-1.avro"),
        "https://api.myotest.cloud/api/profile/":
            MockResponse("profile-007.json")
    }
    if path not in mapping:
        return MockResponse("404", code=404, url=path)
    return mapping[path]


def requests_side_effects_all_workouts(path, headers={}, params={}):
    mapping = {
        "https://api.myotest.cloud/api/v1/workouts/":
            MockResponse("all-workouts-test.json"),
        "https://api.myotest.cloud/api/profile/":
            MockResponse("profile-007.json")
    }
    if path not in mapping:
        return MockResponse("404", code=404, url=path)
    return mapping[path]


class SyncClient(unittest.TestCase):
    @sync_mock.patch(
        'requests.get', mock.Mock(side_effect=requests_side_effects))
    def test_base(self):
        client = Client("token-001")
        result = wait_async(client.test())
        self.assertIn('client-version', result)

    @sync_mock.patch(
        'requests.get', mock.Mock(side_effect=requests_side_effects_errors))
    def test_base_error(self):
        client = Client("token-001")
        with self.assertRaises(ResourceNotFoundException):
            wait_async(client.test())


class AsyncClientTest(asynctest.TestCase):

    @mock.patch('requests.get', mock.Mock(side_effect=requests_side_effects))
    async def test_base(self):
        client = Client("token-001")
        client.test()

    @mock.patch('requests.get', mock.Mock(side_effect=requests_side_effects))
    async def test_get_workout(self):
        client = Client("token-001")
        workout = await client.get_last_workout_with_tags(["test"])
        self.assertEqual(workout.title, "TEST workout 2017-10-06")
        self.assertEqual(workout.type, "data.open")
        self.assertEqual(
            workout.start,
            dateutil.parser.parse("2017-10-06T09:15:55.144470Z"))
        self.assertEqual(
            workout.end,
            dateutil.parser.parse("2017-10-06T09:30:55.144470Z"))
        self.assertEqual(
            workout.target_duration,
            timedelta(seconds=10)
        )
        self.assertEqual(
            workout.effective_duration,
            timedelta(seconds=900)
        )
        datasets = workout.datasets
        self.assertEqual(len(datasets), 3)

        names = set(map(lambda x: x.name, datasets))
        self.assertSetEqual(names, {"mil-1", "gps-1", "slot-1"})
        self.assertEqual(
            sorted(workout.dataset_names()), ["gps-1", "mil-1", "slot-1"])
        self.assertSetEqual(workout.dataset_types(), {"mil", "gps", "slot"})

    @mock.patch(
        'requests.get',
        mock.Mock(side_effect=requests_side_effects_all_workouts))
    async def test_get_workouts(self):
        client = Client("token-001")
        workouts = await client.get_last_workouts()
        self.assertEqual(len(workouts), 2)

    @mock.patch('requests.get', mock.Mock(side_effect=requests_side_effects))
    async def test_get_workout_datasets(self):
        client = Client("token-001")
        workout = await client.get_last_workout_with_tags(["test"])

        datasets = workout.get_datasets("mil")
        self.assertEqual(len(datasets), 1)
        self.assertEqual(datasets[0].name, "mil-1")

        datasets = workout.get_datasets("hot")
        self.assertEqual(len(datasets), 0)

        dataset = workout.get_dataset("mil")
        self.assertEqual(dataset.name, "mil-1")

        dataset = workout.get_dataset("mil-1")
        self.assertEqual(dataset.name, "mil-1")

        dataset = workout.get_dataset("slot")
        self.assertEqual(dataset.name, "slot-1")

        await dataset.load_dataframe()
        self.assertListEqual(
            list(dataset.dataframe.keys()),
            ['event', 'slot_id', 'time'])
        self.assertEqual(dataset.workout, workout)

        self.assertDictEqual(
            dataset.describe["time"],
            {
                '25%': 300.4151147156954,
                '50%': 450.3213799893856,
                '75%': 600.225209236145,
                'count': 6,
                'max': 900.4051049947739,
                'mean': 450.2991078197956,
                'min': 0.1072700023651123,
                'std': 314.6905086959979
            })
        self.assertListEqual(
            dataset.avro_schema.fields,
            [{'name': 'time', 'type': 'double'},
             {'name': 'event', 'type': {
                'name': 'trainingMakerType', 'type': 'enum',
                'symbols': ['SLOT_START', 'SLOT_END']}},
             {'name': 'slot_id', 'type': 'string'}])

    @mock.patch('requests.get', mock.Mock(side_effect=requests_side_effects))
    async def test_get_workout_slots(self):
        client = Client("token-001")
        workout = await client.get_last_workout_with_tags(["test", "other"])

        await workout.load_slots()
        slots = workout.slots
        slot_by_id = {s.id: s for s in slots}

        slot = slot_by_id["c7dd04fd-94a0-9bdd-5d3f-a54f10b43021"]
        self.assertEqual(slot.tags, [
            "max_running_ranges",
            "vma_high"
        ])
        self.assertEqual(slot.text, "MAX 5 minutes")
        self.assertEqual(slot.type, "run")
        self.assertEqual(slot.start_time, timedelta(seconds=600.228))
        self.assertEqual(slot.end_time, timedelta(seconds=900.405))
        self.assertEqual(slot.value.type, "duration")
        self.assertEqual(slot.value.value, 300)

        self.assertEqual(slot.result.power.max, 1)
        self.assertEqual(slot.result.power.min, 0)
        self.assertEqual(slot.result.power.std, 0.5)
        self.assertEqual(slot.result.power.mean, 0.512)
        self.assertEqual(slot.result.power.median, 1.0)
        self.assertEqual(slot.result.power.count, 1000)

        self.assertIsInstance(slot.result.speed, ResultData)
        self.assertIsInstance(slot.result.cadence, ResultData)
        self.assertIsInstance(slot.result.undulation, ResultData)
        self.assertIsInstance(slot.result.stiffness, ResultData)
        self.assertIsInstance(slot.result.stride_length, ResultData)
        self.assertIsInstance(slot.result.effective_flight_time, ResultData)
        self.assertIsInstance(slot.result.effective_contact_time, ResultData)

        slot = workout.get_slot_with_tags(["vma_high"])
        self.assertEqual(slot.id, "c7dd04fd-94a0-9bdd-5d3f-a54f10b43021")
        await slot.load_dataframe("mil")
        mil_slot_df = slot.get_dataframe("mil")
        self.assertTrue(
            mil_slot_df.iloc[0]["time"] >= slot.start_time.total_seconds())
        self.assertTrue(
            mil_slot_df.iloc[0]["time"] <= slot.end_time.total_seconds())

    @mock.patch('requests.get', mock.Mock(side_effect=requests_side_effects))
    async def test_get_profile(self):
        client = Client("token-001")
        profile = await client.get_profile()
        self.assertEqual(profile.full_name, "James Bond")
        self.assertEqual(
            profile.birth_date, dateutil.parser.parse("1972-07-02").date())
        age = relativedelta(
            date.today(),
            dateutil.parser.parse("1972-07-02").date()).years
        self.assertEqual(
            profile.age, age)

    @mock.patch('requests.get', mock.Mock(side_effect=requests_side_effects))
    async def test_get_other_profile(self):
        client = Client("token-001", user_id="profile-999")
        profile = await client.get_profile()
        self.assertEqual(profile.full_name, "Bob Misterio")

    @mock.patch('requests.get', mock.Mock(
        side_effect=requests_side_effects_no_slots))
    async def test_get_workout_no_slots(self):
        client = Client("token-001")
        workout = await client.get_last_workout_with_tags(["test", "other"])

        await workout.load_slots()

        slots = workout.slots
        self.assertEqual(len(slots), 1)
        slot = slots[0]
        self.assertEqual(slot.tags, [
            "max_running_ranges",
            "casual_running_ranges",
            "warm_up_running_ranges",
            "vma_high"
        ])
        self.assertEqual(slot.text, workout.title)
        self.assertEqual(slot.type, "unknown")
        self.assertEqual(slot.start_time, timedelta(seconds=0))
        self.assertEqual(slot.end_time, timedelta(seconds=900))
        self.assertEqual(slot.value.type, "duration")
        self.assertEqual(slot.value.value, 10.0)

        self.assertEqual(slot.result.speed.count, 3001)
        self.assertEqual(slot.result.speed.min, 2.798)
        self.assertEqual(slot.result.speed.max, 6.719)
        self.assertEqual(slot.result.speed.std, 1.516)
        self.assertEqual(slot.result.speed.mean, 5.068)
        self.assertEqual(slot.result.speed.median, 5.068)

    @mock.patch('requests.get', mock.Mock(side_effect=requests_side_effects))
    async def test_get_slots_from_client(self):
        client = Client("token-001")
        slot = await client.get_slot_with_tags(["vma_high"])
        self.assertEqual(slot.tags, [
            "max_running_ranges",
            "vma_high"
        ])
