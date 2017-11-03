from django.contrib import admin
from .widget import LaporemWidget
from .forms import LaporemImageField


class LaporemAdmin(object):
    formfield_overrides = {
        LaporemImageField: {'widget': LaporemWidget()}
    }