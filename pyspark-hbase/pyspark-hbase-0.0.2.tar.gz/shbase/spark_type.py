# -*- coding: utf-8 -*-
from pyspark.sql.types import AtomicType, DataTypeSingleton
import datetime


class DateTimeType(AtomicType):
	"""DateTime (datetime.datetime) data type.
	"""

	__metaclass__ = DataTypeSingleton

	EPOCH_ORDINAL = datetime.datetime(1970, 1, 1, 0, 0, 0).toordinal()

	def needConversion(self):
		return True

	def toInternal(self, d):
		if d is not None:
			return d.toordinal() - self.EPOCH_ORDINAL

	def fromInternal(self, v):
		if v is not None:
			return datetime.datetime.fromordinal(v + self.EPOCH_ORDINAL)
