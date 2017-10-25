#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, current_app
from flask_login import current_user
from .forms import RegistrationForm, ProfileForm


def save_form_to_db(data):
    """save data in form to db"""
    # TODO
    pass


def login(data):
    pass


@current_app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # 存到　datastore
        data = form.data
        data.pop('csrf_token')
        data.pop('password2')
        login(data)
        return redirect(url_for('profile.html'))
    return render_template('register.html', form=form)


@current_app.route('/profile/', methods=['GET'])
def profile():
    form = ProfileForm()
    for k, v in current_user.get_data().items():
        if hasattr(form, k):
            setattr(getattr(form, k), 'data', v)
    return render_template('profile.html', form=form)
