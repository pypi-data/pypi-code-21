#
#   Copyright (c) 2014-2015 eGauge Systems LLC
# 	4730 Walnut St, Suite 110
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
import re

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from epic import perms
from epic.models import *
from epic import urls

class URL_Iterator:
    def __init__(self, urlpatterns):
        self.urlpattern_iterator = urlpatterns.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            pat = self.urlpattern_iterator.__next__() # Python 3
        except AttributeError:
            pat = self.urlpattern_iterator.next() # Python 2
        args = {}
        for key, value in pat.regex.groupindex.items():
            args[key] = 1
        url = reverse('epic:%s' % pat.name, kwargs=args)
        return url, pat.name

    def next(self):
        """For Python 2 compatibility."""
        return self.__next__()

def create_part(id):
    return Part(pk=id, mfg='mfg', mfg_pn='mfg_pn%d' % id,
                mounting=Part.MOUNTING_SMD, target_price=1, overage=0,
                spq=1, status=Part.STATUS_ACTIVE, lead_time=9)

def create_warehouse(id, name):
    return Warehouse(pk=id, name=name)

def create_vendor(id, name):
    return Vendor(pk=id, name=name)

def create_vendor_part(part_id, vendor_id, vendor_pn, price):
    return Vendor_Part(part_id=part_id, vendor_id=vendor_id,
                       vendor_pn=vendor_pn, price=price)

def create_order(id, vendor_id, warehouse_id):
    now = timezone.now()
    then = now + timedelta(days=30)
    return Order(pk=id, ts=now, warehouse_id=warehouse_id,
                 expected_arrival_date=then,
                 status=Order.STATUS_OPEN, vendor_id=vendor_id)

def create_ship(id, order_id, warehouse_id, tracking,
                cost_freight, cost_other, cost_discount):
    return Shipment(pk=id, ts=timezone.now(), ordr_id=order_id,
                    warehouse_id=warehouse_id,
                    cost_freight=cost_freight, cost_other=cost_other,
                    cost_discount=cost_discount)

def create_inventory(id, warehouse_id):
    return Inventory(pk=id, ts=timezone.now(), warehouse_id=warehouse_id)

def create_assembly_item(assy_id=None, comp_id=None, qty=1):
    return Assembly_Item(assy_id=assy_id, comp_id=comp_id, qty=qty)

def create_line_item(txtn_id, part_id, qty, line_cost, index):
    return Line_Item(txtn_id=txtn_id, part_id=part_id, qty=qty,
                     line_cost=line_cost, index=index)

class Part_Method_Tests(TestCase):

    def test_is_orderable(self):
        p = Part(status=Part.STATUS_PREVIEW)
        self.assertEqual(p.is_orderable(), False)

        p = Part(status=Part.STATUS_ACTIVE)
        self.assertEqual(p.is_orderable(), True)

        p = Part(status=Part.STATUS_DEPRECATED)
        self.assertEqual(p.is_orderable(), True)

        p = Part(status=Part.STATUS_OBSOLETE)
        self.assertEqual(p.is_orderable(), False)

    def test_equivalent_parts(self):
        p1 = create_part(1)
        self.assertEqual(p1.equivalent_parts(), set([ p1 ]))

        p2 = create_part(2)

        p1.substitute = p2
        p1.save()
        p2.save()
        self.assertEqual(p1.equivalent_parts(), set([ p1, p2 ]))
        self.assertEqual(p2.equivalent_parts(), set([ p1, p2 ]))

        p3 = create_part(3)
        p3.substitute = p2
        p3.save()
        self.assertEqual(p1.equivalent_parts(), set([ p1, p2, p3 ]))
        self.assertEqual(p2.equivalent_parts(), set([ p1, p2, p3 ]))
        self.assertEqual(p3.equivalent_parts(), set([ p1, p2, p3 ]))

        p1.substitute = None
        p1.save()
        self.assertEqual(p1.equivalent_parts(), set([ p1 ]))
        self.assertEqual(p2.equivalent_parts(), set([ p2, p3 ]))
        self.assertEqual(p3.equivalent_parts(), set([ p2, p3 ]))

        p1.delete()
        p2.delete()
        p3.delete()

class Access_Tests(TestCase):
    @classmethod
    def setup_part(cls):
        p1 = create_part(1)
        p1.save()
        ai = create_assembly_item(assy_id=1, comp_id=2, qty=3)
        ai.refdes = 'R1,R2,R3'
        ai.save()
        p = create_vendor_part(1, 2, 'ASSY_HOUSE_VENDOR_PART_#1', 325.654321)
        p.save()

    @classmethod
    def setup_vendor(cls):
        v = create_vendor(1, 'Vendor #1')
        v.save()
        p = create_vendor_part(1, 1, 'VENDOR_PART_#1', 535.123456)
        p.save()

    @classmethod
    def setup_warehouse(cls):
        w = create_warehouse(1, 'Warehouse #1')
        w.save()

    @classmethod
    def setUpClass(cls):
        u = get_user_model().objects.create_user('test', 'test@magic.com',
                                                 'magic')
        u.user_permissions = [perms.VIEW_PERM, perms.EDIT_PERM]

        Access_Tests.setup_part()
        p2 = create_part(2)
        p2.save()

        Access_Tests.setup_vendor()
        Access_Tests.setup_warehouse()

        w = create_warehouse(2, 'Assyhouse #1')
        w.save()
        v = create_vendor(2, 'Assyhouse #1')
        v.save()

    # def test_redirect_to_https(self):
    #     url = reverse('epic:epic_index')
    #     response = self.client.get(url, secure=False)
    #     self.assertEqual(response.status_code, 301)
    #     self.assertIsNotNone(re.match('https://', response.url))

    def test_unauthenticated_accesses(self):
        response = self.client.get('/autocomplete/Part_Autocomplete/?q=1')
        self.assertEqual(response.status_code, 403)

        response = self.client.get('/autocomplete/Order_Autocomplete/?q=1')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(
            '/autocomplete/Manufacturer_Autocomplete/?q=1')
        self.assertEqual(response.status_code, 403)

        response = self.client.get('/autocomplete/Footprint_Autocomplete/?q=1')
        self.assertEqual(response.status_code, 403)

        # the remaining URLs return HTTP Status 302 FOUND(temporary redirect)
        # since they redirect to the login page:

        response = self.client.get(reverse('epic:part_info') + '?pid=1',
                                    secure=True)
        self.assertEqual(response.status_code, 302)

        for url, pattern_name in URL_Iterator(urls.urlpatterns):
            response = self.client.get(url, secure=True)
            self.assertEqual(response.status_code, 302)

    def test_authenticated_accesses(self):
        res = self.client.login(username='test', password='magic')

        for url, pattern_name in URL_Iterator(urls.urlpatterns):
            if re.match('order_', pattern_name):
                # order part 1(an assembly) from vendor 'Assyhouse #1'
                o = create_order(1, 2, 1)
                o.save()
                l = create_line_item(1, 1, qty=13, line_cost='15.95', index=1)
                l.save()
            elif re.match('ship_', pattern_name):
                # order part 1(an assembly) from vendor 'Assyhouse #1'
                o = create_order(2, 2, 1)
                o.save()
                l = create_line_item(2, 1, qty=13, line_cost='15.95', index=1)
                l.save()
                s = create_ship(1, 2, 1, '1234,5678', 1.1, 2.2, 3.3)
                s.save()
                l = create_line_item(1, 1, qty=2, line_cost='2', index=1)
                l.save()
            elif re.match('warehouse_inventory_', pattern_name):
                i = create_inventory(1, 1)
                i.save()

            expect = 200
            expect_url = None
            post_action = []
            if pattern_name == 'search_results':
                url += '?q=1'
                # with a unique result, search redirects to the detail page:
                expect = 302
                expect_url = reverse('epic:part_detail', kwargs={'pk': 1})
            elif pattern_name == 'part_delete':
                expect = 302
                expect_url = reverse('epic:part_list')
                post_action.append(Access_Tests.setup_part)
            elif pattern_name == 'ship_delete':
                expect = 302
                expect_url = reverse('epic:ship_list')
            elif pattern_name == 'vendor_delete':
                expect = 302
                expect_url = reverse('epic:vendor_list')
                post_action.append(Access_Tests.setup_vendor)
            elif pattern_name == 'warehouse_delete':
                expect = 302
                expect_url = reverse('epic:warehouse_list')
                post_action.append(Access_Tests.setup_warehouse)
            elif pattern_name == 'warehouse_inventory_delete':
                expect = 302
                expect_url = reverse('epic:warehouse_detail', kwargs={'pk':1})
            elif pattern_name == 'order_delete':
                expect = 302
                expect_url = reverse('epic:order_list')

            print('testing url %s' % url)
            response = self.client.get(url, secure=True)

            # we can't only have one transaction with pk=1...
            Order.objects.all().delete()
            Shipment.objects.all().delete()
            Inventory.objects.all().delete()

            if response.status_code != expect:
                print('access to %s failed' % url)
                if hasattr(response, 'url'):
                    print(' redirect URL: %s' % response.url)
            self.assertEqual(response.status_code, expect)
            if expect_url is not None:
                self.assertEqual(response.url,
                                  'https://testserver' + expect_url)

            for action in post_action:
                action()

    def test_unauthorized_accesses(self):
        """See TODO."""
        pass
