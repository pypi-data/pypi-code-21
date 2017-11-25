from django.forms import (
    DateInput as BaseDateInput,
    DateTimeInput as BaseDateTimeInput,
    TimeInput as BaseTimeInput,
)


class DateInput(BaseDateInput):
    input_type = 'date'


class DateTimeInput(BaseDateTimeInput):
    input_type = 'datetime'


class TimeInput(BaseTimeInput):
    input_type = 'time'
