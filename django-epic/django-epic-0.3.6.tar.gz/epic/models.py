#
#   Copyright (c) 2014-2017 eGauge Systems LLC
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
from __future__ import print_function

import hashlib
import math
import re
import os

from datetime import date, datetime, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.html import escape
from django.contrib.humanize.templatetags.humanize import intcomma

PART_PRICE_VALIDATORS = [ MinValueValidator(Decimal('0.000001')) ]

def strchoice(choices, val):
    for key, name in choices:
        if key == val:
            return name
    return val

def part_cost(line_cost, qty):
    if qty <= 0:
        return 0
    return Decimal('%.6f' % (float(line_cost) / qty))

def format_part_number(part):
    return 'EP%05u' % part

def html_part_link(part):
    """Return an HTML link for PART.  PART may be either a Part object or
    a part number.
    """
    if isinstance(part, Part):
        pn = part.id
    else:
        pn = part
    name = format_part_number(pn)
    url = reverse('epic:part_detail', kwargs={'pk': pn})
    return '<a href="%s">%s</a>' % (url, name)

def html_list_or_none(list):
    """If list is empty, return 'none', otherwise, join the list using ','
    as a separator.
    """
    html = ', '.join(list)
    if html != '':
        return html
    return '<em>&mdash;None&mdash;</em>'

class Datasheet(models.Model):
    name = models.CharField(max_length=128, unique=True, blank=False)
    ds_file = models.FileField(
        upload_to=getattr(settings, 'EPIC_DATASHEET_DIR', 'epic/datasheets'),
        blank=False,
        verbose_name='Datasheet File')
    notes = models.CharField(
        max_length=1024, help_text='For misc. information that may be useful '
        'along with the datasheet, such as website retrieved from.',
        blank=True)
    md5sum = models.CharField(max_length=36, null=True)

    class Meta:
        ordering =('name',)

    def __str__(self):
        return '%s' % self.name

    def html_link(self):
        url = reverse('epic:datasheet_detail', kwargs={'pk': self.id})
        return '<a href="%s">%s</a>' % (url, self.name)

    def save(self, *args, **kwargs):
        md5 = hashlib.md5()
        for chunk in self.ds_file.chunks():
            md5.update(chunk)
        self.md5sum = md5.hexdigest()
        super(Datasheet, self).save(*args, **kwargs)

    # See signals.datasheet_delete() for deletion cleanup.

class Part(models.Model):
    MOUNTING_SMD = 0
    MOUNTING_THD = 1
    MOUNTING_CHASSIS = 2
    MOUNTING_FREE = 3
    MOUNTING_CHOICES = (
        (MOUNTING_SMD,		'SMD'),
        (MOUNTING_THD,		'THD'),
        (MOUNTING_CHASSIS,	'chassis'),
        (MOUNTING_FREE,		'free')
    )
    STATUS_PREVIEW = 0
    STATUS_ACTIVE = 1
    STATUS_DEPRECATED = 2
    STATUS_OBSOLETE = 3
    STATUS_CHOICES = (
        (STATUS_PREVIEW,	'preview'),
        (STATUS_ACTIVE,		'active'),
        (STATUS_DEPRECATED,	'deprecated'),
        (STATUS_OBSOLETE,	'obsolete'),
    )
    # deprecated parts are orderable, but preview or obsolete parts
    # are not:
    STATUS_ORDERABLE = ( STATUS_ACTIVE, STATUS_DEPRECATED )
    # what modified the part's BOM (assembly-items list) last (user or tool)?:
    LAST_MOD_TYPE_USER	= 0
    LAST_MOD_TYPE_TOOL	= 1
    LAST_MOD_CHOICES = (
        (LAST_MOD_TYPE_USER,	'user'),
        (LAST_MOD_TYPE_TOOL,	'tool')
    )

    val = models.CharField(max_length=31, verbose_name='Value', blank=True,
                           default='',
                           help_text='The primary value of the part '
                           'such as resistance for a resistor or '
                           'capacitance for a capacitor.')
    descr = models.CharField(max_length=127, verbose_name='Description',
                             blank=True, default='',
                             help_text='Brief listing of key parameters of '
                             'the part, such as temperature range, drift, '
                             'max. voltages, etc.')
    footprint = models.CharField(max_length=63, blank=True, default='',
                                 help_text='The part\'s PCB footprint.')
    mfg = models.CharField(max_length=31, verbose_name='Manufacturer',
                           help_text='The name of the manufacturer of the '
                           'part.')
    mfg_pn = models.CharField(max_length=31,
                              verbose_name='Manufacturer\'s Part #')
    mounting = models.IntegerField(choices=MOUNTING_CHOICES,
                                   default=MOUNTING_SMD, blank=False,
                                   verbose_name='Mounting Type',
                                   help_text='How the part is mounted to a '
                                   'PCB (free if it\'s not mounted at all, '
                                   'such as a plug).')
    target_price = models.DecimalField(max_digits=10, decimal_places=6,
                                       validators=PART_PRICE_VALIDATORS,
                                       verbose_name='Target price [$]',
                                       help_text='The expected price of the '
                                       'part.')
    overage = models.DecimalField(max_digits=6, decimal_places=3,
                                  validators=[
                                      MinValueValidator(Decimal('0')),
                                      MaxValueValidator(Decimal('100')) ],
                                  verbose_name='Overage [%]',
                                  help_text='Worst-case percentage of parts '
                                  'we expect to lose due to attrition at the '
                                  'assembly-house.')
    spq = models.IntegerField(default=1,
                              verbose_name='Standard-Package Qty',
                              help_text='The number of parts in '
                              'a standard package.  For example, 10,000 '
                              'pieces in a reel.')
    lead_time = models.PositiveIntegerField(verbose_name='Lead-time [weeks]',
                                            help_text='Lead-time in weeks.')
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS_PREVIEW, blank=False,
                                 verbose_name='Life-time Status',
                                 help_text='The life-time status of this '
                                 'part. Parts marked `preview\' and '
                                 '`obsolete\' are not considered orderable.')
    substitute = models.ForeignKey('self', null=True, blank=True,
                                   verbose_name='Substitutes',
                                   help_text='List of other parts that are '
                                   '(identical) substitutes for this part.')
    last_bom_mod_type = models.IntegerField(choices=LAST_MOD_CHOICES,
                                            default=LAST_MOD_TYPE_USER,
                                            blank=False)
    last_bom_mod_name = models.CharField(max_length=31, blank=True, default='',
                                         help_text='Name of entity '
                                         'which last modified this part.')
    datasheet = models.ForeignKey(Datasheet, null=True, blank=True)
    notes = models.TextField(blank=True, default='', help_text='Notes '
                             'regarding this part.')

    equiv_parts = None
    best_parts = {}

    class Meta:
        unique_together = ('mfg', 'mfg_pn')
        index_together = [
            [ 'mfg', 'mfg_pn' ]
        ]

    def __str__(self):
        return '%s' % (format_part_number(self.id))

    @classmethod
    def flush_caches(cls, sender, **kwargs):
        """See signals.flush_caches()."""
        # clear the caches when a part changes:
        Part.equiv_parts = None
        Part.best_parts = {}

    def equivalent_parts(self):
        """Return the set of equivalent parts for this part.  The set includes
        the part itself.  However, if the part doesn't have an id yet
        (newly created and not saved yet), the empty set is returned.

        """

        def get_set(part):
            if part.id not in Part.equiv_parts:
                Part.equiv_parts[part.id] = frozenset([ part ])
            return Part.equiv_parts[part.id]

        if self.id is None:
            # newly created parts don't have a valid id yet so they can't
            # be hashed, which also means nobody can be referring to it,
            # which means its equivalent-parts-set is empty.
            return frozenset([ ])

        if Part.equiv_parts is None:
            Part.equiv_parts = {}
            for p in Part.objects.exclude(substitute__isnull=True):
                union  = get_set(p)
                union |= get_set(p.substitute)
                for q in union:
                    Part.equiv_parts[q.id] = union
        return get_set(self)

    def best_part(part):
        """Among the set of parts equivalent to this part, find orderable or
        lowest-cost part.  Returns part itself if nothing better is
        available.

        """
        if part.id in Part.best_parts:
            return Part.best_parts[part.id]

        best_part = part		# may not be orderable...
        for p in part.equivalent_parts():
            if p == part or not p.is_orderable():
                continue
            target_pr = p.target_price
            best_pr = best_part.target_price
            if not best_part.is_orderable() \
               or target_pr < best_pr \
               or (target_pr == best_pr and p.id < best_part.id):
                best_part = p
        for p in part.equivalent_parts():
            Part.best_parts[part.id] = best_part
        return best_part

    def best_vendor(part):
        """Return the vendor that has the lowest price for this part."""
        vps = Vendor_Part.objects.filter(part_id=part.id) \
                                 .order_by('price')
        for vp in vps:
            if vp.status in Part.STATUS_ORDERABLE:
                return vp.vendor
        return None

    def is_orderable(self):
        return self.status in Part.STATUS_ORDERABLE

    def assembly_items(self):
        return Assembly_Item.objects.filter(assy_id=self.id)

    def html_link(self):
        return html_part_link(self)

    def avg_cost(self):
        """Get average cost for a part, including any of its substitutes.  The
        average is calculated across orders with shipments within the past
        365 days.  If there is no shipment within 365, the cost is
        calculated based on the most recent shipment alone.  If there are
        no shipments at all, return the part's target price.
        """
        total_cost = 0
        total_qty = 0
        cut_off_ts = timezone.now() - timedelta(days=365)

        part_id_list = [ p.id for p in self.equivalent_parts() ]
        ship_id_list = Shipment.objects.all() \
                                       .values_list('transaction_ptr_id',
                                                     flat=True)
        deltas = Delta.objects.filter(adj__gt=0) \
                              .filter(part_id__in=part_id_list) \
                              .filter(txtn_id__in=ship_id_list) \
                              .order_by('txtn_id')

        for d in deltas:
            cost = d.txtn.shipment.cost_details()
            overhead_ratio = 0
            if cost['parts'] > 0:
                overhead_ratio = cost['overhead'] / cost['parts']

            for p_id in part_id_list:
                if p_id not in cost['part_detail']:
                    continue
                pc = cost['part_detail'][p_id]
                if d.txtn.shipment.from_warehouse is None:
                    piece_cost = float(pc['cost']) / pc['qty']
                    total_cost += (d.adj * piece_cost) \
                                  * (1 + float(overhead_ratio))
                    total_qty += d.adj
                else:
                    # For inter-warehouse-shipments, allocate the shipping
                    # costs in proportion to the target-cost of the parts
                    part_ratio = (pc['qty'] * d.part.target_price) \
                                 / cost['parts_target']
                    total_cost += float(part_ratio * cost['overhead'])
                if d.txtn.ts <= cut_off_ts:
                    break
        if total_qty == 0:
            return self.target_price
        return part_cost(total_cost, total_qty)

    def best_vendor_part(self, preferred_vendors=None):
        """Find the best (lowest-cost and orderable) part from the specified
        list of preferred vendors (or any vendor if preferred_vendors
        is None).  If the part cannot be ordered from any of the
        preferred vendors, return the vendor part from the
        non-preferred vendor with the lowest cost.

        """
        best_vp_any = None
        best_vp_preferred = None
        for p in self.equivalent_parts():
            if not p.is_orderable():
                continue
            vps = Vendor_Part.objects.filter(part_id=p.id)
            for vp in vps:
                if not vp.is_orderable():
                    continue
                if best_vp_any is None or vp.price < best_vp_any.price:
                    best_vp_any = vp
                if preferred_vendors is None or \
                   vp.vendor not in preferred_vendors:
                    continue
                if best_vp_preferred is None \
                   or vp.price < best_vp_preferred.price:
                    best_vp_preferred = vp
        if best_vp_preferred:
            return best_vp_preferred
        return best_vp_any

    def strstatus(self):
        return strchoice(Part.STATUS_CHOICES, self.status)

    def choice_label(self):
        return '%s: %s %s' % (self, self.mfg, self.mfg_pn)

class Vendor(models.Model):
    name = models.CharField(max_length=31, verbose_name='Vendor Name',
                             db_index=True, unique=True)
    search_url = models.CharField(max_length=127,
                                   verbose_name='Search URL Pattern',
                                   default='', blank=True,
                                   help_text='This pattern defines how to '
                                   'search for a particular part on the '
                                   'vendor\'s website.  %(vendor_pn)s gets '
                                   'replaced by the vendor\'s part-number, '
                                   '%(mfg)s by the manufacturer\'s name, and '
                                   '%(mfg_pn)s by the manufacturer\'s '
                                   'part-number.')
    def __str__(self):
        return '%s' % self.name

    def html_link(self):
        url = reverse('epic:vendor_detail', kwargs={'pk': self.id})
        return '<a href="%s">%s</a>' % (url, self.name)

    def is_vendor(self):
        return True

    class Meta:
        ordering = [ 'name' ]

class Vendor_Part(models.Model):
    part = models.ForeignKey(Part, verbose_name='Part #')
    vendor = models.ForeignKey(Vendor)
    vendor_pn = models.CharField(max_length=31,
                                 verbose_name='Vendor\'s Part #')
    price = models.DecimalField(max_digits=10, decimal_places=6,
                                validators=PART_PRICE_VALIDATORS)
    status = models.IntegerField(choices=Part.STATUS_CHOICES,
                                 default=Part.STATUS_ACTIVE, blank=False,
                                 verbose_name='Life-time Status',
                                 help_text='The life-time status of this '
                                 'vendor part.')

    class Meta:
        unique_together = (
            ('vendor', 'part'),
            ('vendor', 'vendor_pn')
        )

    def __str__(self):
        return 'Vendor_Part %s: %s %s' % (format_part_number(self.part.id),
                                          self.vendor.name, self.vendor_pn)

    def html_link(self):
        if self.vendor.search_url == '':
            return escape(self.vendor_pn)
        url = self.vendor.search_url % \
              {
                  'mfg'		: escape(self.part.mfg),
                  'mfg_pn'	: escape(self.part.mfg_pn),
                  'vendor_pn'	: escape(self.vendor_pn)
              }
        return '<a href="%s" target="part_lookup">%s</a>' % \
            (url, self.vendor_pn)

    def strstatus(self):
        return strchoice(Part.STATUS_CHOICES, self.status)

    def is_orderable(self):
        return self.status in Part.STATUS_ORDERABLE

    @staticmethod
    def get(part_id, vendor_id):
        result = Vendor_Part.objects \
                            .filter(part_id=part_id) \
                            .filter(vendor_id=vendor_id)
        if len(result) != 1:
            return None
        return result[0]

class Warehouse(models.Model):
    name = models.CharField(max_length=31, unique=True,
                            help_text='The name of the warehouse.')
    address = models.TextField(blank=True, default='', help_text='The '
                               'shipping address for the warehouse.')

    def __str__(self):
        return '%s' % self.name

    def html_link(self):
        url = reverse('epic:warehouse_detail', kwargs={'pk': self.id})
        return '<a href="%s">%s</a>' % (url, self.name)

    def inventories(self):
        return Inventory.objects.filter(warehouse_id=self.id)

    @staticmethod
    def by_name(name):
        return Warehouse.objects.get(name=name)

    class Meta:
        ordering = [ 'name' ]

class Delta(models.Model):
    """Deltas are used to track all quantity adjustments to a part at a
    given warehouse.  The adjustment may be relative to existing
    quantity or absolute.
    """
    part = models.ForeignKey(Part, verbose_name='Part #',
                             help_text='The part whose quantity gets '
                             'adjusted.')
    is_absolute = models.BooleanField(verbose_name='Absolute Adjustment',
                                      default=False,
                                      help_text='If set, the adjustment is '
                                      'absolute otherwise it is relative.')
    adj = models.IntegerField(verbose_name='Adjustment Count',
                              help_text='The amount by which the part '
                               'quantity should be adjusted by.')
    txtn = models.ForeignKey('Transaction', verbose_name='Transaction #')
    warehouse = models.ForeignKey(Warehouse)

    def line_item(self):
        """For order or shipments items, return associated line-item."""
        line_items = Line_Item.objects.filter(txtn_id=self.txtn.id) \
                                      .filter(part_id=self.part_id)
        if len(line_items) != 1:
            return None
        return line_items[0]

    def line_cost(self):
        """For order or shipments items, return line-cost for this delta."""
        line_item = self.line_item()
        if line_item is None:
            return None
        return Decimal('%.2f' % (self.adj *
                                 float(line_item.line_cost) / line_item.qty))

    def __str__(self):
        return 'Delta %s' % self.id

class Assembly_Item(models.Model):
    assy = models.ForeignKey(Part, related_name='assembly_item_part',
                             verbose_name='Assembly Part #',
                             help_text='The part number of the assembly this '
                             'item belongs to.')
    comp = models.ForeignKey(Part, related_name='assembly_item_comp',
                             verbose_name='Component Part #',
                             help_text='The part number of the component of '
                             'this item.')
    qty = models.PositiveIntegerField(help_text='The quantity of this '
                                      'component required by the assembly.')
    refdes = models.TextField(blank=True, default='',
                              verbose_name='Refdes List',
                              help_text='A list of comma-separated reference '
                              'designators e.g., "R101,R304". '
                              'The length of this list should match Quantity.')

    def qty_with_overage(self, factor):
        q = math.ceil(abs(factor) * self.qty * (1 + self.comp.overage / 100))
        return int(math.copysign(q, factor))

    def __str__(self):
        return 'Assembly_Item %s.%s' % (format_part_number(self.assy_id),
                                        format_part_number(self.comp_id))

    def clean(self):
        refdes_list = re.findall(r'([^, ]+)', self.refdes)
        self.refdes = ','.join(refdes_list)

    class Meta:
        unique_together = ('assy', 'comp')
        index_together = [
            [ 'assy', 'comp' ]
        ]

class Line_Item(models.Model):
    txtn = models.ForeignKey('Transaction', verbose_name='Transaction #',
                              db_index=True)
    part = models.ForeignKey(Part, verbose_name='Part #')
    qty = models.PositiveIntegerField(help_text='The quantity of this part.')
    line_cost = models.DecimalField(max_digits = 9, decimal_places = 2,
                                    verbose_name='Amount',
                                    help_text='The total cost of this '
                                    'line-item.  Part-cost is line-item cost '
                                    'divided by quantity.',
                                    validators=[MinValueValidator(
                                        Decimal('0.00'))])
    index = models.PositiveIntegerField(help_text='Sequential and unchanging '
                                        'index of this line-item.')
    class Meta:
        ordering = [ 'index' ]
        unique_together = (
            ('txtn', 'part'),
            ('txtn', 'index')
        )
        index_together = [
            [ 'txtn', 'part' ]
        ]

    def vendor_part(self):
        result = Vendor_Part.objects \
                            .filter(part_id=self.part_id) \
                            .filter(vendor_id=self.txtn.order.vendor.id)
        if len(result) != 1:
            return None
        return result[0]

    def part_cost(self):
        return part_cost(self.line_cost, self.qty)

    def order_line_item(self):
        """For shipment line-items, return associated order line-item."""
        line_items = Line_Item.objects \
                              .filter(txtn_id=self.txtn.shipment.ordr.id) \
                              .filter(part_id=self.part_id)
        if len(line_items) != 1:
            return None
        return line_items[0]

    def qty_remaining_to_ship(self):
        if not hasattr(self.txtn, 'order'):
            return None

        shipment_ids = Shipment.objects.filter(ordr_id=self.txtn_id) \
                                       .values_list('transaction_ptr_id',
                                                    flat=True)
        already_shipped = sum(Line_Item.objects \
                              .filter(txtn_id__in=shipment_ids) \
                              .filter(part_id=self.part_id) \
                              .values_list('qty', flat=True))
        return self.qty - already_shipped

class Transaction(models.Model):
    """Orders, shipments, and inventories are all transactions."""
    ts = models.DateTimeField(verbose_name='Creation Time',
                              help_text='Date and time when this transaction '
                              'was created.')
    warehouse = models.ForeignKey(Warehouse,
                                  verbose_name='Warehouse',
                                  help_text='The (destination) warehouse '
                                  'this transaction applies to.')
    notes = models.TextField(blank=True,
                             verbose_name='Notes',
                             help_text='Comments and notes for this '
                             'transaction')

    def __str__(self):
        return 'Transaction %u' % (self.id)

    def first_available_index(self):
        max_index = 0
        for item in Line_Item.objects.filter(txtn_id=self.id):
            if item.index > max_index:
                max_index = item.index
        return max_index + 1

    def update_order_status(self):
        if hasattr(self, 'order'):
            order = self.order
        elif hasattr(self, 'shipment'):
            if self.ordr is None:
                return
            order = self.ordr
        else:
            return

        status = Order.STATUS_CLOSED
        for line_item in Line_Item.objects.filter(txtn_id=order.id):
            if line_item.qty_remaining_to_ship() > 0:
                status = Order.STATUS_OPEN
                break

        if status != order.status:
            order.status = status
            order.save()

    def update_deltas(self):
        if hasattr(self, 'order') or hasattr(self, 'inventory'):
            # orders never have deltas and inventories directly edit the deltas
            return

        # delete all existing deltas for this transaction:
        Delta.objects.filter(txtn_id=self.id).delete()

        if hasattr(self, 'shipment'):
            ship = self.shipment
            src_warehouse = ship.src_warehouse()

            for line_item in Line_Item.objects.filter(txtn_id=ship.id):
                d = Delta(part_id=line_item.part_id, is_absolute=False,
                          adj=line_item.qty, txtn_id=self.id,
                          warehouse_id=ship.warehouse_id)
                d.save()

                assy_items = d.part.assembly_items()
                if ship.ordr and assy_items.exists():
                    # assemblies ordered from an assembly-house are created
                    # from parts at the assembly-house:
                    for assy_item in assy_items:
                        qty = -assy_item.qty_with_overage(line_item.qty)
                        part = assy_item.comp.best_part ()
                        d = Delta(part_id=part.id, is_absolute=False,
                                  adj=qty, txtn_id=self.id,
                                  warehouse_id=src_warehouse.id)
                        d.save()
                elif ship.from_warehouse is not None:
                    d = Delta(part_id=line_item.part_id, is_absolute=False,
                              adj=-line_item.qty, txtn_id=self.id,
                              warehouse_id=src_warehouse.id)
                    d.save()

    def finalize(self):
        self.update_order_status()
        self.update_deltas()

    def description(self):
        if hasattr(self, 'order'):
            ttl = self.order.days_until_past_due()
            extra = ''
            if ttl and ttl <= 0:
                extra = ' (expected %d days ago)' % -ttl
            desc = '%s PO %s shipping to %s%s.' % \
                (self.order.vendor.html_link(), self.order.html_link(),
                 self.warehouse.html_link(), extra)
        elif hasattr(self, 'shipment'):
            ship = self.shipment
            if ship.ordr_id:
                desc = 'Shipment %s to %s for %s PO %s.' % \
                       (ship.html_link(), ship.warehouse.html_link(),
                        ship.ordr.vendor.html_link(), ship.ordr.html_link())
            else:
                desc = 'Shipment %s from %s to %s.' % \
                       (ship.html_link(), ship.from_warehouse.html_link(),
                        ship.warehouse.html_link())
        elif hasattr(self, 'inventory'):
            desc = 'Inventory %s at %s.' % (self.inventory.html_link(),
                                            self.warehouse.html_link())
        else:
            desc = 'Unknown transaction %d.' % self.id
        return desc

    def html_link(self):
        if hasattr(self, 'order'):
            return 'Order&nbsp;%s' % self.order.html_link()
        elif hasattr(self, 'shipment'):
            return 'Shipment&nbsp;%s' % self.shipment.html_link()
        elif hasattr(self, 'inventory'):
            return 'Inventory&nbsp;%s' % self.inventory.html_link()
        else:
            return 'Transaction&nbsp;%d' % (self.id)

class Order(Transaction):
    STATUS_OPEN = 0
    STATUS_CLOSED = 1
    STATUS_CHOICES = (
        (STATUS_OPEN,	'open'),
        (STATUS_CLOSED,	'closed'),
    )
    expected_arrival_date = models.DateField(verbose_name='Expected Arrival '
                                             'Date', help_text='Date when '
                                             'the order is expected to '
                                             'arrive.')
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS_OPEN, blank=False,
                                 verbose_name='Order Status')
    vendor = models.ForeignKey(Vendor, help_text='The name of the '
                               'vendor (distributor) where the order '
                               'was placed.')

    def __str__(self):
        return '%u' % (self.id)

    def total_cost(self):
        return sum(Line_Item.objects
                   .filter(txtn_id=self.id) \
                   .values_list('line_cost', flat=True))

    def is_open(self):
        return self.status == Order.STATUS_OPEN

    def days_until_past_due(self):
        if self.status != Order.STATUS_OPEN:
            return None
        return (self.expected_arrival_date - date.today()).days

    def assembly_line_items(self):
        """Returns the list of line-items that are assemblies."""
        assemblies = Assembly_Item.objects.values_list('assy_id', flat=True) \
                                          .distinct()
        return Line_Item.objects.filter(txtn_id=self.id) \
                                .filter(part_id__in=assemblies)

    def html_link(self):
        url = reverse('epic:order_detail', kwargs={'pk': self.id})
        return '<a href="%s">%s</a>' % (url, self.id)

    def choice_label(self):
        return '%s: %s $%s' % (self.id, self.vendor.name,
                               intcomma(self.total_cost()))

class Shipment(Transaction):
    tracking = models.CharField(max_length=127, default='', blank=True,
                                verbose_name='Tracking #s',
                                help_text='Comma-separated list of tracking '
                                'numbers.')
    # order is a reserved word in django...
    ordr = models.ForeignKey(Order, verbose_name='Order #',
                             null=True, blank=True,
                             help_text='For an order shipment, the '
                             'order that resulted in this shipment.')
    from_warehouse = models.ForeignKey(Warehouse, null=True, blank=True,
                                       help_text='For an inter-warehouse '
                                       'shipment, the warehouse '
                                       'the shipment originates from.')
    cost_freight = models.DecimalField(max_digits=9, decimal_places=2,
                                       verbose_name='Freight Cost',
                                       validators=[MinValueValidator(
                                           Decimal('0.00'))])
    cost_other = models.DecimalField(max_digits=9, decimal_places=2,
                                     verbose_name='Other Costs',
                                     help_text='Other costs assessed by the '
                                     'shipper, such as handling costs.',
                                     validators=[MinValueValidator(
                                         Decimal('0.00'))])
    cost_discount = models.DecimalField(max_digits=9, decimal_places=2,
                                        verbose_name='Discount Given',
                                        help_text='Discounts given by the '
                                        'shipper, such as early payment '
                                        'discount.',
                                        validators=[
                                            MinValueValidator(
                                                Decimal('0.00'))])

    costs = {}		# cache of cost-details

    @classmethod
    def flush_caches(cls, sender, **kwargs):
        """See signals.flush_caches()."""
        # cache of shipment costs, indexed by transaction id
        cls.costs = {}

    def __str__(self):
        return 'Shipment %u' % self.id

    def clean(self):
        tracking_list = re.findall(r'([^, ]+)', self.tracking)
        self.tracking = ','.join(tracking_list)

    def html_link(self):
        url = reverse('epic:ship_detail', kwargs={'pk': self.id})
        return '<a href="%s">%s</a>' % (url, self.id)

    def html_tracking_links(self):
        trk_list = self.tracking.split(',')
        url_pattern = 'https://www.packagetrackr.com/track/%s'
        result = []
        for trk in trk_list:
            trk = trk.strip()
            url = url_pattern % trk
            result.append('<a target="trk_lookup" href="%s">%s</a>' \
                           % (url, trk))
        return html_list_or_none(result)

    def src_warehouse(self):
        if self.ordr is not None:
            try:
                return Warehouse.by_name(self.ordr.vendor)
            except:
                return None
        else:
            return self.from_warehouse

    def overhead_cost(self):
        """Return the cost of overheads of this shipment."""
        return self.cost_freight + self.cost_other - self.cost_discount

    def cost_details(self):
        if self.id not in Shipment.costs:
            parts_cost = 0
            parts_target_cost = 0
            part_detail = {}
            for line_item in Line_Item.objects.filter(txtn_id=self.id):
                if part_detail is not None:
                    part_detail[line_item.part_id] = {
                        'cost': line_item.line_cost,
                        'qty': line_item.qty
                    }
                if self.from_warehouse is None:
                    parts_cost += line_item.line_cost
                else:
                    # for inter-warehouse shipments, each line_item.line_cost
                    # is zero but we need an approximation of part cost so
                    # we can allocate the cost of the shipment properly
                    parts_target_cost += line_item.qty \
					 * line_item.part.target_price
            Shipment.costs[self.id] = {
                'overhead': self.overhead_cost(),
                'parts': parts_cost,
                'parts_target': parts_target_cost,
                'part_detail': part_detail
            }
        return Shipment.costs[self.id]

    def parts_cost(self):
        """Return the total cost of all parts in this shipment."""
        return self.cost_details()['parts']

    def total_cost(self):
        return self.overhead_cost() + self.parts_cost()

class Inventory(Transaction):
    def __str__(self):
        return 'Inventory %u' % self.id

    def html_link(self):
        url = reverse('epic:warehouse_inventory_detail',
                       kwargs={'warehouse': self.warehouse.id, 'pk': self.id})
        return '<a href="%s">%s</a>' % (url, self.id)
