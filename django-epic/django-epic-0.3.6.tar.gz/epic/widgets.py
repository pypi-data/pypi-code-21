from bootstrap3_datetime.widgets import DateTimePicker as DTPickerNoMedia


class DateTimePicker(DTPickerNoMedia):
    """The current bootstrap3_datetime flavor on PyPi has no static files."""
    class Media:
        css = {
            'all': (
                'bootstrap3_datetime/css/bootstrap-datetimepicker.min.css',)
        }
        js = ('bootstrap3_datetime/js/moment-with-locales.min.js',
              'bootstrap3_datetime/js/bootstrap-datetimepicker.min.js')
