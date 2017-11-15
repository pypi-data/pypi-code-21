
import json

from django.conf import settings

from modeltranslation import admin
from modeltranslation.utils import build_localized_fieldname


class TranslationAdmin(admin.TranslationAdmin):

    change_form_template = 'trans/admin/change_form.html'

    def _get_translation_options(self, origin_lang):

        options = {}

        languages = dict(settings.LANGUAGES).keys()

        languages.remove(origin_lang)

        for field in self.trans_opts.fields.keys():
            options[build_localized_fieldname(field, origin_lang)] = {
                l: build_localized_fieldname(field, l) for l in languages
            }

        return options

    def changeform_view(
            self, request, object_id=None, form_url='', extra_context=None):

        if getattr(settings, 'IS_ADMIN_FIELDS_TRANSLATION_ENABLED', False):
            extra_context = {
                'trans_options': json.dumps(self._get_translation_options(
                    request.LANGUAGE_CODE
                ))
            }

        return super(TranslationAdmin, self).changeform_view(
            request, object_id, form_url, extra_context)