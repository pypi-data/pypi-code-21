from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.views.generic import TemplateView

class PublicView(TemplateView):
    template_name = 'public.html'

class PrivateView(LoginRequiredMixin, TemplateView):
    template_name = 'private.html'
