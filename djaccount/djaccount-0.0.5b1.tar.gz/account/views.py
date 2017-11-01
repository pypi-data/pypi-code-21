from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from .models import Account


class AccountView(LoginRequiredMixin, DetailView):
    model = Account

    def get_object(self, queryset=None):
        self.kwargs.setdefault('pk', self.request.user.id)
        return super().get_object()
