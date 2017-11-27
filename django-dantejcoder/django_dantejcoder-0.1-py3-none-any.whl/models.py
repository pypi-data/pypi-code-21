from django.db import models
import datetime


class RegionTest(models.Model):
    name = models.CharField(max_length=32)

    __to_json_fields__ = ('name',)


class CityTest(models.Model):
    name = models.CharField(max_length=32)
    region = models.ForeignKey(RegionTest)

    def __to_json_dict__(self):
        return {'name': self.name, 'region': self.region, 'test': True}


class EmptyModel(models.Model):
    empty = models.BooleanField(default=True)


class StandardModel(models.Model):
    name = models.CharField(max_length=32, default='Standard')
    val = models.IntegerField(default=1)


class TypeModel(models.Model):
    mbool = models.BooleanField(default=False)
    mdate = models.DateField(default=datetime.date(2017, 11, 25))
    mdatetime = models.DateTimeField(default=datetime.datetime(2017,11,25,9,41,6))
    mtime = models.TimeField(default=datetime.time(9,52,7))