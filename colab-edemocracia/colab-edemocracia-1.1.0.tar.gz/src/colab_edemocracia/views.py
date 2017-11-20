# -*- coding: utf-8 -*-
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, resolve_url
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.http import is_safe_url
from django.conf import settings
from django.http import (
    HttpResponseRedirect, HttpResponseBadRequest, JsonResponse)
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login, update_session_auth_hash
)
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.views.generic import UpdateView, FormView
from django.views.decorators.clickjacking import xframe_options_exempt
from django.template.defaultfilters import slugify

from .forms.accounts import (
    SignUpForm, UserProfileForm, SignUpAjaxForm)
from .models import UserProfile
from colab.accounts.models import EmailAddressValidation, EmailAddress
from colab_edemocracia import captcha
import string
import random

User = get_user_model()


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
        else:
            messages.add_message(request, messages.ERROR,
                                 u"Usuário ou senhas incorretos.")
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }

    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@sensitive_post_parameters()
@csrf_protect
@login_required
def password_change(request,
                    template_name='registration/password_change_form.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    current_app=None, extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('colab_edemocracia:profile')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Senha alterada com sucesso!')
            # Updating the password logs out all other sessions for the user
            # except the current one if
            # django.contrib.auth.middleware.SessionAuthenticationMiddleware
            # is enabled.
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
        'title': 'Alterar senha',
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)


def send_verification_email(email, verification_url):
    html = render_to_string('emails/edemocracia_new_user.html',
                            {'verification_url': verification_url})
    subject = "Confirmação de cadastro"
    mail = EmailMultiAlternatives(subject=subject, to=[email])
    mail.attach_alternative(html, 'text/html')
    mail.send()


def generate_username(name):
    name = slugify(name.split('@')[0])[:29]
    if User.objects.filter(username=name).exists():
        return generate_username(
            name + random.choice(string.letters + string.digits))
    else:
        return name


class SignUpView(View):
    http_method_names = [u'post']

    def post(self, request):
        if request.user.is_authenticated():
            return reverse('colab_edemocracia:home')

        user_form = SignUpForm(request.POST)

        if not user_form.is_valid():
            for error in user_form.errors.values():
                messages.add_message(request, messages.ERROR, error[0])
            return redirect(reverse('colab_edemocracia:home'))

        user = user_form.save(commit=False)
        user.needs_update = False

        user.is_active = False
        user.set_password(user_form.cleaned_data['password'])
        user.save()

        profile = UserProfile.objects.get(user=user)
        profile.uf = user_form.cleaned_data['uf']
        profile.save()

        email = EmailAddressValidation.create(user.email, user)

        location = reverse('email_view',
                           kwargs={'key': email.validation_key})
        verification_url = request.build_absolute_uri(location)
        send_verification_email(user.email, verification_url)

        # Check if the user's email have been used previously in the mainling
        # lists to link the user to old messages
        email_addr, created = EmailAddress.objects.get_or_create(
            address=user.email)
        if created:
            messages.add_message(
                request, messages.SUCCESS,
                u"Usuário criado com sucesso! Por favor, verifique seu email"
                " para concluir seu cadastro."
            )
            email_addr.real_name = user.get_full_name()

        email_addr.user = user
        email_addr.save()

        return redirect(reverse('colab_edemocracia:home'))


class ProfileView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'profile.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        messages.success(self.request, 'Perfil modificado com sucesso!')
        return reverse('colab_edemocracia:profile')


class WidgetLoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'widget/login.html'

    @xframe_options_exempt
    def dispatch(self, *args, **kwargs):
        return super(WidgetLoginView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        next_url = self.request.POST.get('next', None)
        if next_url:
            return next_url
        else:
            raise HttpResponseBadRequest()


class WidgetSignUpView(View):
    http_method_names = [u'post']

    @xframe_options_exempt
    def dispatch(self, *args, **kwargs):
        return super(WidgetSignUpView, self).dispatch(*args, **kwargs)

    def post(self, request):
        if request.user.is_authenticated():
            if request.kwargs['next']:
                return reverse(request.kwargs['next'])
            else:
                return HttpResponseBadRequest()

        user_form = SignUpForm(request.POST)

        if not user_form.is_valid():
            for error in user_form.errors.values():
                messages.add_message(request, messages.ERROR, error[0])
            return redirect(reverse('colab_edemocracia:widget_login'))

        user = user_form.save(commit=False)
        user.needs_update = False

        user.is_active = False
        user.set_password(user_form.cleaned_data['password'])
        user.save()

        email = EmailAddressValidation.create(user.email, user)

        location = reverse('email_view',
                           kwargs={'key': email.validation_key})
        verification_url = request.build_absolute_uri(location)
        send_verification_email(user.email, verification_url)

        # Check if the user's email have been used previously in the mainling
        # lists to link the user to old messages
        email_addr, created = EmailAddress.objects.get_or_create(
            address=user.email)
        if created:
            messages.add_message(
                request, messages.SUCCESS,
                u"Usuário criado com sucesso! Por favor, verifique seu email"
                " para concluir seu cadastro."
            )
            email_addr.real_name = user.get_full_name()

        email_addr.user = user
        email_addr.save()

        return redirect(reverse('colab_edemocracia:widget_login'))


@csrf_exempt
def ajax_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        response_data = {}
        if form.is_valid():
            auth_login(request, form.get_user())
            status_code = 200
        else:
            response_data['data'] = u"Usuário e/ou senha inválidos."
            status_code = 401
        return JsonResponse(response_data, status=status_code)


@csrf_exempt
def ajax_signup(request):
    if request.method == 'POST':
        response_data = {}
        form = SignUpAjaxForm(request.POST)
        if form.is_valid():
            captcha_response = captcha.verify(
                form.data['g-recaptcha-response'])
            if captcha_response['success']:
                user = User.objects.create(
                    username=generate_username(form.cleaned_data['email']),
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    needs_update=False,
                    is_active=False,
                )
                user.set_password(form.cleaned_data['password'])
                user.save()

                profile = UserProfile.objects.get(user=user)
                profile.uf = form.cleaned_data['uf']
                profile.country = form.cleaned_data['country']
                profile.birthdate = form.cleaned_data['birthdate']
                profile.gender = form.cleaned_data['gender']
                profile.save()

                email = EmailAddressValidation.create(user.email, user)
                location = reverse('email_view',
                                   kwargs={'key': email.validation_key})
                verification_url = request.build_absolute_uri(location)
                send_verification_email(user.email, verification_url)

                status_code = 200
                response_data['data'] = (u"Usuário criado com sucesso! Por "
                                         "favor, verifique seu email para "
                                         "concluir seu cadastro.")
            else:
                message = ' '.join(
                    map(lambda x: captcha.ERRORS[x],
                        captcha_response['error-codes'])
                )
                status_code = 401
                response_data['data'] = message
        else:
            status_code = 400
            response_data['data'] = form.errors
        return JsonResponse(response_data, status=status_code)
