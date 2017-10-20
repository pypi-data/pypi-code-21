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

"""
Views for managing reachability test.
"""
from django.core.urlresolvers import reverse_lazy
from horizon import forms
from horizon import tabs
from horizon_bsn.api import neutron
from horizon_bsn.content.connections.reachability_tests \
    import forms as project_forms
from horizon_bsn.content.connections.reachability_tests \
    import tabs as project_tabs

LJUST_WIDTH = 50


class CreateView(forms.ModalFormView):
    form_class = project_forms.CreateReachabilityTest
    template_name = 'project/connections/reachability_tests/create.html'
    success_url = reverse_lazy("horizon:project:connections:index")


class RunQuickTestView(forms.ModalFormView):
    form_class = project_forms.RunQuickTestForm
    template_name = 'project/connections/reachability_tests/quick_test.html'
    success_url = reverse_lazy(
        "horizon:project:connections:reachability_tests:quick")


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateForm
    template_name = 'project/connections/reachability_tests/update.html'
    success_url = reverse_lazy('horizon:project:connections:index')

    def get_object(self):
        return neutron.reachabilitytest_get(self.request,
                                            self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['reachabilitytest'] = self.get_object()
        return context

    def get_initial(self):
        reachabilitytest = self.get_object().to_dict()
        return reachabilitytest


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.ReachabilityTestDetailTabs
    template_name = 'project/connections/reachability_tests/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["reachabilitytest"] = self.get_data()
        return context

    def get_data(self):
        id = self.kwargs['id']
        reachabilitytest = neutron.reachabilitytest_get(self.request, id)
        return reachabilitytest

    def get_tabs(self, request, *args, **kwargs):
        reachabilitytest = self.get_data()
        return self.tab_group_class(
            request, reachabilitytest=reachabilitytest, **kwargs)


class QuickDetailView(tabs.TabView):
    tab_group_class = project_tabs.QuickTestDetailTabs
    template_name = 'project/connections/reachability_tests/quick_detail.html'

    def get_context_data(self, **kwargs):
        context = super(QuickDetailView, self).get_context_data(**kwargs)
        context["reachabilityquicktest"] = self.get_data()
        return context

    def get_data(self):
        try:
            reachabilityquicktest = neutron.reachabilityquicktest_get(
                self.request, self.request.user.project_id)
            return reachabilityquicktest
        except Exception:
            return []

    def get_tabs(self, request, *args, **kwargs):
        reachabilityquicktest = self.get_data()
        return self.tab_group_class(
            request, reachabilityquicktest=reachabilityquicktest, **kwargs)


class SaveQuickTestView(forms.ModalFormView):
    form_class = project_forms.SaveQuickTestForm
    template_name = 'project/connections/reachability_tests/save.html'
    success_url = reverse_lazy("horizon:project:connections:index")
