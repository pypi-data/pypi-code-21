import re
import pandas as pd
from uuid import uuid4

from datetime import date
from dateutil.relativedelta import relativedelta

from myotest.wrapper import (
    WrapperObject, StringField, DateTimeField, ListField,
    IDField, FloatField, DurationField, LinkField,
    DictField, DateField, IntegerField, BooleanField,
    DataframeField
)

from myotest.exception import ResourceNotFoundException


class AvroSchemaField(WrapperObject):
    fields = ListField(DictField())
    name = StringField()
    type = StringField()


class Dataset(WrapperObject):
    name = StringField()
    workout = LinkField()
    describe = DictField()
    avro_schema = AvroSchemaField()

    async def load_dataframe(self):
        if hasattr(self, "_dataframe"):
            # Already loaded
            return
        reader = await self.client.fetch_avro(self._json["cloud_url"])
        self._dataframe = DataframeField().convert(
            pd.DataFrame(list(reader)).sort_values("time"),
            self.client
        )

    @property
    def dataframe(self):
        if not hasattr(self, "_dataframe"):
            raise ValueError(
                "Dataframe not loaded, call "
                "'await workout.load_dataframe()' on workout or "
                "'await slot.load_dataframe(name)' on slot first")
        return self._dataframe

    def dataframe_for_slot(self, slot):
        start_time = slot.start_time.total_seconds()
        end_time = slot.end_time.total_seconds()
        df = self.dataframe
        return df[
            (df["time"] < end_time) &
            (df["time"] >= start_time)
        ]

    @property
    def type(self):
        return self.name.split("-")[0]


class SlotValue(WrapperObject):
    type = StringField()
    value = FloatField()


class ResultData(WrapperObject):
    min = FloatField()
    max = FloatField()
    count = IntegerField()
    mean = FloatField()
    median = FloatField()
    std = FloatField()


class SlotResult(WrapperObject):
    power = ResultData()
    speed = ResultData()
    cadence = ResultData()
    undulation = ResultData()
    stiffness = ResultData()
    stride_length = ResultData()
    generic_stride_length = ResultData()
    effective_flight_time = ResultData()
    effective_contact_time = ResultData()
    distance = FloatField()
    regularity_90 = FloatField()
    step_count_ratio = FloatField()
    regularity_median = FloatField()
    gps_valid = BooleanField()
    cmj_note = FloatField()


class Slot(WrapperObject):
    id = IDField()
    tags = ListField(StringField())
    type = StringField()
    value = SlotValue()
    text = StringField()
    result = SlotResult()
    end_time = DurationField()
    start_time = DurationField()
    power_type = StringField()
    analysis = ListField(DictField())
    workout = LinkField()

    async def load_dataframe(self, dataset_name):
        return await self.workout.load_dataframe(dataset_name)

    def get_dataframe(self, dataset_name):
        return self.workout.get_dataset(
            dataset_name).dataframe_for_slot(self)

    @property
    def duration(self):
        return self.end_time - self.start_time


class Workout(WrapperObject):
    id = IDField()
    title = StringField()
    start = DateTimeField()
    end = DateTimeField()
    type = StringField()
    target_duration = DurationField()
    effective_duration = DurationField()
    tags = ListField(StringField())

    datasets = ListField(Dataset(), source="data")

    def _get_datasets(self, base_name):
        if "-" in base_name:
            regexp = re.compile("^{}$".format(base_name))
        else:
            regexp = re.compile("^{}-[0-9]+$".format(base_name))
        return [x for x in self.datasets if re.match(regexp, x.name)]

    def post_resolve_datasets(self, datasets):
        for ds in datasets:
            ds.workout = self

    def get_datasets(self, name):
        return list(self._get_datasets(name))

    def get_dataset(self, name):
        datasets = self._get_datasets(name)
        if len(datasets) > 0:
            return datasets[0]
        else:
            return None

    async def load_dataframe(self, name):
        datasets = self._get_datasets(name)
        if len(datasets) > 0:
            await datasets[0].load_dataframe()
            return True
        return False

    async def load_slots(self):
        if hasattr(self, "_slots"):
            # Already loaded
            return
        try:
            slots = await self.client.get_slots(self._json["id"])
        except ResourceNotFoundException:
            slots = None
        if slots is None:
            slots = self.create_fake_slots()
        self._slots = ListField(Slot()).convert(slots, self.client)
        for s in self._slots:
            s.workout = self

    @property
    def slots(self):
        if not hasattr(self, "_slots"):
            raise ValueError(
                "Slots not loaded, call 'await workout.load_slots()' first")
        return self._slots

    def create_fake_slots(self):
        """
        Create a single slot matching the full workout
        This is for legacy workout without validation and slots
        :return: Slot
        """
        single_slot = {
            "id": str(uuid4()),
            "text": self.title,
            "tags": self.tags,
            "type": "unknown",
            "value": {
                "type": "duration",
                "value": self.target_duration.total_seconds(),
            },
            "end_time": self.effective_duration.total_seconds(),
            "power_type": "",
            "start_time": 0,
            "result": {
                "regularity_90": 1.0,
                "regularity_median": 1.0,
                "step_count_ratio": 0.0,
                "speed": None,
                "distance": 0,
                "power": None,
                "cadence": None,
                "undulation": None,
                "stiffness": None,
                "stride_length": None,
                "generic_stride_length": None,
                "effective_flight_time": None,
                "effective_contact_time": None,
                "gps_valid": None,
                "cmj_note": 0
            }
        }

        mil_ds = self.get_dataset("mil")
        if mil_ds:
            rounding = 3

            def extract_result(key):
                if key not in mil_ds.describe:
                    return {
                        "max": 0,
                        "min": 0,
                        "std": 0,
                        "mean": 0,
                        "count": 0,
                        "median": 0,
                    }
                return {
                    "max": round(mil_ds.describe[key]["max"], rounding),
                    "min": round(mil_ds.describe[key]["min"], rounding),
                    "std": round(mil_ds.describe[key]["std"], rounding),
                    "mean": round(mil_ds.describe[key]["mean"], rounding),
                    "count": round(mil_ds.describe[key]["count"], rounding),
                    # We don't have median in describe
                    "median": round(mil_ds.describe[key]["mean"], rounding),
                }
            step_count_walk = extract_result("stepCountWalk")["max"]
            step_count_run = extract_result("stepCountRun")["max"]
            step_count_ratio = round(
                step_count_walk / step_count_run, rounding
            ) if step_count_run > 0 else 0.0
            output_source = extract_result("outputSource")

            single_slot["result"] = {
                "speed": extract_result("gpsRecoverySpeed"),
                "distance": extract_result("gpsRecoveryDistance")["max"],
                "power": extract_result("gpsRecoveryPower"),
                "cadence": extract_result("cadence"),
                "undulation": extract_result("undulation"),
                "stiffness": extract_result("stiffness"),
                "generic_stride_length": extract_result("genericStrideLength"),
                "stride_length": extract_result("strideLength"),
                "effective_flight_time":
                    extract_result("effectiveFlightTime"),
                "effective_contact_time":
                    extract_result("effectiveContactTime"),
                "gps_valid": bool(
                    (output_source is not None) and
                    (output_source["min"] == 4.0) and
                    (output_source["max"] == 4.0)),
                "regularity_90": 1,
                "step_count_ratio": step_count_ratio,
                "regularity_median": 1
            }
        return [single_slot]

    def post_resolve_slots(self, slots):
        for s in slots:
            s.workout = self

    def _get_slots(self, tags):
        return [x for x in self.slots if
                x.tags and set(tags).issubset(set(x.tags))]

    def get_slot_with_tags(self, tags):
        slots = self._get_slots(tags)
        if len(slots) > 0:
            return slots[0]
        else:
            return None

    def get_all_slots_with_tags(self, tags):
        return self._get_slots(tags)

    def dataset_names(self):
        return [x.name for x in self.datasets]

    def dataset_types(self):
        return set([x.type for x in self.datasets])


class Profile(WrapperObject):
    id = IDField()
    full_name = StringField()
    gender = StringField()
    weight = FloatField()
    height = FloatField()
    leg_length = FloatField()
    waist = FloatField()
    vma = FloatField()
    pma = FloatField()
    vo2_max = FloatField()
    birth_date = DateField()
    age = FloatField()
    running_style_score = FloatField()
    aerobic_capacity_score = FloatField()
    muscular_strength_score = FloatField()
    body_composition_score = FloatField()
    running_fitness_score = FloatField()

    def resolve_age(self, json, field):
        if not self.birth_date:
            return 0
        return relativedelta(date.today(), self.birth_date).years
