from superset.views.base import SupersetModelView
from superset.utils import SupersetException
from flask import Markup
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _

class DatasourceModelView(SupersetModelView):
    def pre_delete(self, obj):
        if obj.slices:
            raise SupersetException(Markup(
                __("Cannot delete a datasource that has slices attached to it."
                + "Here's the list of associated slices: ") +
                "".join([o.slice_link for o in obj.slices])))
