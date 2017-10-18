from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView


class CaptureLogin(RedirectView):
    url = reverse_lazy('account_login')
    query_string = True


capture_login = CaptureLogin.as_view()


class CaptureLogout(RedirectView):
    url = reverse_lazy('account_logout')
    query_string = True


capture_logout = CaptureLogout.as_view()
