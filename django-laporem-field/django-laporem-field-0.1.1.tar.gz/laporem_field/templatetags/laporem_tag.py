from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()


@register.filter
def get_admin_url(obj,func):
        content_type = ContentType.objects.get_for_model(obj)
        try:
            if func=="change":
                return reverse("admin:%s_%s_change" % (
                content_type.app_label,
                content_type.model),
                args=(obj.id,))
            elif func=="add":
                return reverse("admin:%s_%s_add" % (
                content_type.app_label,
                content_type.model))
            elif func=="delete":
                return reverse("admin:%s_%s_delete" % (
                content_type.app_label,
                content_type.model),
                args=(obj.id,))
            elif func=="changelist":
                return reverse("admin:%s_%s_changelist" % (
                content_type.app_label,
                content_type.model))
            elif func=="history":
                return reverse("admin:%s_%s_history" % (
                content_type.app_label,
                content_type.model),
                args=(obj.id,))
        except NoReverseMatch:
            return None

