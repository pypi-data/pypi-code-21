from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView, RedirectView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, \
    PasswordChangeView
from django.contrib import messages as django_messages
from django.contrib.auth import login
from django_tables2 import RequestConfig

from cosmicdb.forms import CosmicAuthenticationForm, CosmicSignupUserForm, CosmicPasswordResetForm, \
    CosmicSetPasswordForm, CosmicPasswordChangeForm
from cosmicdb.models import User
from cosmicdb.tables import NotificationTable, MessageTable


class CosmicSaveErrorDialogsMixin(object):
    success_message = 'Saved'
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(CosmicSaveErrorDialogsMixin, self).get_context_data(**kwargs)
        context['extra_context'] = self.extra_context
        return context

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data

    def form_valid(self, form):
        self.extra_context['page_error'] = False
        response = super(CosmicSaveErrorDialogsMixin, self).form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            django_messages.success(self.request, success_message)
        return response

    def form_invalid(self, form):
        self.extra_context['page_error'] = True
        return super(CosmicSaveErrorDialogsMixin, self).form_invalid(form)


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


def notifications(request, id = None):
    if not request.user.is_authenticated:
        return redirect(reverse('home'))
    if id is None:
        notifications = request.user.usersystemnotification_set.order_by('-created_at')
        table = NotificationTable(notifications)
        RequestConfig(request, paginate={'per_page': 10}).configure(table)
        return render(request, 'cosmicdb/notifications_all.html', {'table': table})
    else:
        notification = request.user.usersystemnotification_set.get(id=id)
        notification.read = True
        notification.save()
        return render(request, 'cosmicdb/notifications_single.html', {'notification': notification})


def messages(request, id=None):
    if not request.user.is_authenticated:
        return redirect(reverse('home'))
    if id is None:
        messages = request.user.usersystemmessage_set.order_by('-created_at')
        table = MessageTable(messages)
        RequestConfig(request, paginate={'per_page': 10}).configure(table)
        return render(request, 'cosmicdb/messages_all.html', {'table': table})
    else:
        message = request.user.usersystemmessage_set.get(id=id)
        message.read = True
        message.save()
        return render(request, 'cosmicdb/messages_single.html', {'message': message})
