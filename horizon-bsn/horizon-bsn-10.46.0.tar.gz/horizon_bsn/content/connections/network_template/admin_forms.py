# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.utils.translation import ugettext_lazy as _
from horizon import forms
from horizon import messages
from horizon_bsn.api import neutron

import logging

LOG = logging.getLogger(__name__)


class CreateUpdateNetworkTemplate(forms.SelfHandlingForm):
    id = forms.CharField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(max_length=255, label=_("Name"),
                           help_text=_("Spaces will be trimmed or converted "
                                       "to _ based on their location."),
                           required=True)
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20}),
        max_length=None, label=_("Template Body"), required=True)
    template_name = "horizon/common/_detail_table.html"

    def clean(self):
        cleaned_data = super(CreateUpdateNetworkTemplate, self).clean()
        if cleaned_data['name']:
            cleaned_data['name'] = (cleaned_data['name']
                                    .strip()
                                    .replace(" ", "_"))
        return cleaned_data

    def handle(self, request, data):
        if data['id'] == '':
            # create request
            try:
                # id is not allowed in create
                data.pop("id", None)
                networktemplate = neutron\
                    .networktemplate_create(request, **data)
            except Exception:
                msg = _("Unable to create template. "
                        "Verify that the name is unique.")
                LOG.debug(msg)
                messages.error(request, msg)
                return False
        else:
            # update request
            try:
                networktemplate = neutron\
                    .networktemplate_update(request, data['id'], **data)
            except Exception:
                msg = _("Unable to update template. "
                        "It may have been deleted.")
                LOG.debug(msg)
                messages.error(request, msg)
                return False
        msg = _("Template saved.")
        LOG.debug(msg)
        messages.success(request, msg)
        return networktemplate


class DetailNetworkTemplate(CreateUpdateNetworkTemplate):
    def __init__(self, request, *args, **kwargs):
        id = request.path_info.split('/')[-1]
        try:
            template = neutron.networktemplate_get(request, id)
        except Exception:
            pass
        super(DetailNetworkTemplate, self).__init__(request, *args, **kwargs)
        if template:
            self.fields['id'].initial = template.id
            self.fields['name'].initial = template.name
            self.fields['body'].initial = template.body
