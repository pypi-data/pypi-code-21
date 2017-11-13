from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from apollo.settings import apollo_settings
from apollo.models import Form
import logging
import csv
import os
import pdb

logger = logging.getLogger(__name__)


class FormManager(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'forms_manager.html', {
            'root_prefix': apollo_settings.ROOT_PREFIX,
            'graphql_path': apollo_settings.GRAPHQL_PATH,
            'themes_url': apollo_settings.ICARUS_THEMES_URL,
        })


class DownloadFormSubmissions(TemplateView):
    def get(self, request, *args, **kwargs):
        form_id = request.GET.get('form_id')

        form = Form.objects.get(id=form_id)
        fields = form.fields.select_related('template').all().order_by('template__name')
        submissions = form.submissions.all()

        # write the submissions to a CSV
        f = NamedTemporaryFile(suffix='.csv')

        logger.debug('writing submission data to tmp file %s' % f.name)

        with open(f.name, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, [f.name for f in fields])

            writer.writeheader()

            for s in submissions:
                writer.writerow(s.cleaned_data)

        response = HttpResponse(f.read(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % smart_str('%s_submissions' % form.name.replace(' ', '_'))

        return response