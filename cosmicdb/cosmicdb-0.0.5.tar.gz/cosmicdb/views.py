from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView, RedirectView, FormView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, \
    PasswordChangeView
from django.contrib.auth import login

from cosmicdb.forms import CosmicAuthenticationForm, CosmicSignupUserForm, CosmicPasswordResetForm, \
    CosmicSetPasswordForm, CosmicPasswordChangeForm
from cosmicdb.models import User


class CosmicLoginView(LoginView):
    form_class = CosmicAuthenticationForm

    def get_success_url(self):
        return reverse('dashboard')


class CosmicSignupView(FormView):
    form_class = CosmicSignupUserForm
    template_name = 'cosmicdb/signup.html'

    def get_success_url(self):
        return reverse('dashboard')

    def form_valid(self, form):
        new_user = User.objects.create_user(**form.cleaned_data)
        login(self.request, new_user)
        return super(CosmicSignupView, self).form_valid(form)


class CosmicPasswordResetView(PasswordResetView):
    form_class = CosmicPasswordResetForm


class CosmicPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CosmicSetPasswordForm


class CosmicPasswordChangeView(PasswordChangeView):
    form_class = CosmicPasswordChangeForm


class Home(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('dashboard')


class Dashboard(TemplateView):
    template_name = 'cosmicdb/dashboard.html'


