#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EAccount(base.EBase):

    username = appier.field()

    password = appier.field()

    email = appier.field()

    first_name = appier.field()

    last_name = appier.field()

    gender = appier.field()

    birth_date = appier.field(
        type = int
    )

    country = appier.field()

    phone_number = appier.field()

    receive_newsletters = appier.field(
        type = bool,
        initial = False
    )

    avatar = appier.field(
        type = appier.File
    )

    facebook_id = appier.field()

    facebook_token = appier.field(
        private = True
    )

    google_id = appier.field()

    google_token = appier.field(
        private = True
    )

    bag = appier.field(
        type = appier.reference(
            "EBag",
            name = "id"
        )
    )

    wishlist = appier.field(
        type = appier.reference(
            "EWishlist",
            name = "id"
        )
    )

    def tokens(self):
        return ["user"]

    @classmethod
    def validate(cls):
        return super(EAccount, cls).validate() + [
            appier.not_null("username"),
            appier.not_empty("username"),
            appier.string_gt("username", 3),
            appier.not_duplicate("username", cls._name()),

            appier.not_null("email"),
            appier.not_empty("email"),
            appier.is_email("email"),
            appier.not_duplicate("email", cls._name()),

            appier.not_null("first_name"),
            appier.not_empty("first_name"),
            appier.string_gt("first_name", 2),

            appier.is_regex("phone_number", "^\+?[0-9\s]{2,}$"),

            appier.equals("password_confirm", "password"),
            appier.equals("new_password_confirm", "new_password")
        ]

    @classmethod
    def validate_new(cls):
        return super(EAccount, cls).validate_new() + [
            appier.not_null("password"),
            appier.not_empty("password"),

            appier.not_null("password_confirm"),
            appier.not_empty("password_confirm")
        ]

    @property
    def full_name(self):
        name = self.first_name
        name += " " + self.last_name if self.last_name else ""
        return name

    @property
    def birth_date_s(self):
        if not self.birth_date: return None
        return self.string_from_timestamp(self.birth_date)
