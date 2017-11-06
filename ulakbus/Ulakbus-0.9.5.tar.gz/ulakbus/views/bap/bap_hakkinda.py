# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import AbstractRole
from ulakbus.models import Personel
from ulakbus.models import Role
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _


class BAPHakkindaView(CrudView):
    def hakkinda_bilgilerini_goster(self):
        self.current.output["meta"]["allow_search"] = False
        self.current.output["meta"]["allow_actions"] = False
        self.output['object_title'] = _(u"BAP Bilgileri burada yer alacak")
        self.output['objects'] = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]

