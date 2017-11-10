# -*- coding: utf-8 -*-

from .models import Vip


def get_vip_ip_from_databaseinfra(databaseinfra):
    vip = Vip.objects.get(databaseinfra=databaseinfra)
    return vip.vip_ip


def get_vip_details_from_ip(ip):
    vip = Vip.objects.get(vip_ip=ip)
    return vip
