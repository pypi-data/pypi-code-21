# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from colab_edemocracia.models import UserProfile
from datetime import datetime


User = get_user_model()


class SignUpForm(forms.ModelForm):
    confirm_password = forms.CharField()
    uf = forms.CharField()
    error_messages = {
        'duplicate_email': _(u"Email já cadastrado."),
        'duplicate_username': _(u"Nome de usuário já cadastrado."),
        'wrong_password': _(u"As senhas não são iguais."),
    }

    required = ('username', 'email', 'password', 'uf')

    class Meta:
        fields = ('username', 'email', 'password')
        model = User

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            msg = self.error_messages.get('wrong_password')
            raise forms.ValidationError(mark_safe(msg))

    def clean_username(self):
        username = self.cleaned_data.get('username').strip().lower()
        if not username:
            raise forms.ValidationError(_('This field cannot be blank.'))

        if User.objects.filter(username=username).exists():
            msg = self.error_messages.get('duplicate_username')
            raise forms.ValidationError(mark_safe(msg))

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')

        user_qs = User.objects.filter(email=email).exclude(username=username)

        if email and user_qs.exists():
            msg = self.error_messages.get('duplicate_email')
            raise forms.ValidationError(mark_safe(msg))

        return email


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].initial = kwargs['instance'].user.first_name
        self.fields['last_name'].initial = kwargs['instance'].user.last_name
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field and isinstance(field, forms.TypedChoiceField):
                field.choices = field.choices[1:]

    class Meta:
        fields = ('gender', 'uf', 'birthdate', 'first_name', 'last_name',
                  'avatar')
        model = UserProfile

    def save(self, commit=True):
        instance = super(UserProfileForm, self).save(commit=False)
        instance.save()
        instance.user.first_name = self.cleaned_data['first_name']
        instance.user.last_name = self.cleaned_data['last_name']
        if commit:
            instance.user.save()
        return instance


class PasswordResetForm(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.filter(email__iexact=email, is_active=True)
        if not users.exists():
            raise forms.ValidationError(
                "Não existe usuário registrado com esse "
                "email ou usuário está inativo."
            )

        return email


class SignUpAjaxForm(forms.ModelForm):
    uf = forms.CharField(required=False)
    country = forms.CharField(required=False)
    birthdate = forms.DateField(required=False)
    gender = forms.CharField(required=False)

    required = ('email', 'password', 'first_name')

    error_messages = {
        'empty_email': _(
            u"Este campo é obrigatório."),
        'exists_email': _(
            u"Já existe um usuário cadastrado com este email."),
        'length_password': _(
            u"O campo senha deve possuir no mínimo 6 caracteres."),
        'empty_uf_country': _(
            u"Os campos estado ou país devem ser preenchidos."),
        'empty_uf': _(
            u'Selecione uma UF, caso seja estrangeiro,'
            u' clique em "sou estrangeiro".'),
        'empty_country': _(
            u'Selecione um país, caso não seja estrangeiro,'
            u' clique em "sou brasileiro".'),
    }

    class Meta:
        fields = ('email', 'password', 'first_name')
        model = User

    def clean(self):
        cleaned_data = super(SignUpAjaxForm, self).clean()
        uf = cleaned_data.get("uf", None)
        country = cleaned_data.get("country", None)

        if not uf and not country:
            self.add_error('uf', mark_safe(
                self.error_messages.get('empty_uf')))
            self.add_error('country', mark_safe(
                self.error_messages.get('empty_country')))
            raise forms.ValidationError(mark_safe(
                self.error_messages.get('empty_uf_country')))

        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get("password", None)

        if len(password) < 6:
            raise forms.ValidationError(
                mark_safe(self.error_messages.get('length_password')))

        return password

    def clean_email(self):
        email = self.cleaned_data.get("email", None)
        users = User.objects.filter(email=email)

        if not email:
            raise forms.ValidationError(
                mark_safe(self.error_messages.get('empty_email')))

        if users.exists():
            raise forms.ValidationError(
                mark_safe(self.error_messages.get('exists_email')))

        return email
