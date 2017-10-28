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
import operator
import re

from copy import deepcopy

from datetime import datetime, timedelta

from django.conf import settings as cfg
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils import timezone

from epic.models import *

class error(Exception):
    pass

def get_assembly_name(part):
    """Get the canonical name for assembly PART.  We leave out
    MANUFACTURER for our own parts, but include the manufacturer name
    for uniqueness for others.

    """
    if part.mfg == cfg.EPIC_MANUFACTURER:
        return part.mfg_pn
    return part.mfg + ' ' + part.mfg_pn


def get_assemblies_using_part(part):
    """Get a list of assemblies that are using PART (or any of its
    substitutes).  Obsolete assemblies are ignored."""
    part_list = [ p.id for p in part.equivalent_parts() ]
    return Part.objects.filter(assembly_item_part__comp_id__in=part_list) \
                       .exclude(status=Part.STATUS_OBSOLETE) \
                       .distinct()

class Part_Count:
    def __init__(self, qty=0):
        self.qty = qty
        self.is_final = False

class Part_Inventory:
    def __init__(self):
        self.warehouse = {}

    def get_entry(self, warehouse_id, part_id):
        if warehouse_id in self.warehouse:
            entry = self.warehouse[warehouse_id]
        else:
            self.warehouse[warehouse_id] = entry = {}
        if part_id not in entry:
            entry[part_id] = Part_Count()
        return entry

    def apply_assembly_item(self, warehouse_id, item, factor):
        # Note: Even though this component might be an assembly itself,
        #  there is no need to recurse down because parts do not
        #  spontaneously transform into assemblies.  That is, even if
        #  we had the pre-requisite sub-components, there still has to
        #  be an assembly order which is where we'd do the proper
        #  sub-component qty adjustments.
        part_id = item.comp.best_part().id
        qty = item.qty_with_overage(factor)
        entry = self.get_entry(warehouse_id, part_id)
        entry[part_id].qty += qty

    def apply_order_line_item(self, item):
        part_id = item.part_id
        order = item.txtn.order
        qty = item.qty_remaining_to_ship()
        if qty <= 0:
            return
        entry = self.get_entry(order.warehouse_id, part_id)
        entry[part_id].qty += qty

        assy_items = item.part.assembly_items()
        if assy_items.exists() > 0:
            vendor_id = Warehouse.by_name(order.vendor).id
            for assy_item in item.part.assembly_items():
                self.apply_assembly_item(vendor_id, assy_item, -qty)

    def apply_delta(self, delta, reverse_chronological_order=False):
        """Adjust inventory according to DELTA.  If applying deltas in reverse
        chronological order (newest first), you must set
        REVERSE_CHRONOLOGICAL_ORDER to True and stop processing deltas
        after as the first delta with "is_absolute==True" has been
        processed.

        """
        entry = self.get_entry(delta.warehouse_id, delta.part_id)
        if entry[delta.part_id].is_final:
            return

        if delta.is_absolute:
            if reverse_chronological_order:
                entry[delta.part_id].qty += delta.adj
                entry[delta.part_id].is_final = True
            else:
                entry[delta.part_id].qty  = delta.adj
        elif not entry[delta.part_id].is_final:
                entry[delta.part_id].qty += delta.adj

    def get_qty(self, warehouse, part):
        if warehouse not in self.warehouse:
            return 0
        if part not in self.warehouse[warehouse]:
            return 0
        return self.warehouse[warehouse][part].qty

    def adj_qty(self, warehouse, part, adj):
        entry = self.get_entry(warehouse, part)
        entry[part].qty += adj

def get_stock(warehouses=None, as_of_date=None, exclude_txtn_id=None):
        """Get the current stock as a Part_Inventory instance for the
        specified list of warehouses.  If WAREHOUSES is None, the
        stock for all warehouses is returned.

        If AS_of_date is not None, only deltas with timestamps up
        to and including that time are considered.

        If EXCLUDE_TXTN_ID is not None, any deltas for that
        transaction id are ignored.
        """
        inv = Part_Inventory()

        qs = Delta.objects.order_by('-txtn__ts')
        if warehouses is not None:
            qs = qs.filter(warehouse__in=warehouses)
        if exclude_txtn_id is not None:
            qs = qs.exclude(txtn_id=exclude_txtn_id)
        if as_of_date is not None:
            as_of_ts = timezone.make_aware(
                datetime.combine(as_of_date, datetime.min.time()),
                timezone.utc)
            qs = qs.filter(txtn__ts__lte=as_of_ts)

        for d in qs:
            inv.apply_delta(d, reverse_chronological_order=True)

        if False:
            for w in inv.warehouse:
                s = ''
                for p in inv.warehouse[w]:
                    if inv.warehouse[w][p].qty != 0:
                        s += (' %d*%s' % (inv.warehouse[w][p].qty,
                                          format_part_number(p)))
                print('Warehouse %s stock:%s' % (w, s))
        return inv

def get_stock_summary(warehouse=None, as_of_date=None):
    """Get a summary of the stock at WAREHOUSE (or all of them if
    WAREHOUSE is None).  Returns a list and the total cost of the
    parts in stock.  The list contains dictionaries that break down
    the parts inventory: part_list is the list of equivalent parts and
    their sub-quantities, total_qty is the total_qty (across
    equivalent parts), 'price' is the average price of the best part
    and 'amount' is simply 'price' * 'total_qty'.

    """
    inv = get_stock([ warehouse ] if warehouse else None,
                    as_of_date=as_of_date)

    if warehouse is None:
        parts = {}
        for w in inv.warehouse:
            for p in inv.warehouse[w]:
                if p not in parts:
                    parts[p] = Part_Count(0)
                parts[p].qty += inv.warehouse[w][p].qty
    elif warehouse.id in inv.warehouse:
        parts = inv.warehouse[warehouse.id]
    else:
        parts = {}

    best_parts = {}
    for p in parts:
        part = Part.objects.get(pk=p)
        best = part.best_part()
        if best.id in best_parts:
            continue
        best_parts[best.id] = best

    stock = []
    stock_total = 0
    for best_part_id, best_part in best_parts.items():
        qty = parts[best_part_id].qty if best_part_id in parts else 0
        total_qty = qty

        # always list best part first:
        part_list = [ ( best_part,  qty ) ]
        for p in best_part.equivalent_parts():
            if p == best_part or p.id not in parts:
                continue
            qty = parts[p.id].qty
            part_list.append(( p, qty ) )
            total_qty += qty

	# do not suppress negative counts, as those are useful to be seen
        if total_qty == 0:
            continue

        price = best_part.avg_cost()
        amount = total_qty * price
        stock_total += amount
        stock.append({ 'part_list': part_list, 'total_qty': total_qty,
                       'price': price, 'amount': amount})
    return stock, stock_total

def get_inventory_summary(warehouse_id, inventory):
    inv = get_stock(warehouses=[ warehouse_id ], as_of_date=inventory.ts,
                    exclude_txtn_id=inventory.id)

    total_value_change = 0
    has_relative_deltas = False
    inv_items = {}
    for d in Delta.objects.filter(txtn_id=inventory.id):
        best_part = d.part.best_part()

        if best_part.id in inv_items:
            item = inv_items[best_part.id]
        else:
            item = {
                # relative inventory items are no longer supported:
                'is_relative':  False,
                'part':		best_part,
                'value_diff':	0,
                'qty_old_list':	[],
                'qty_new_list': [],
                'qty_dif_list': []
            }
            inv_items[best_part.id] = item
        old_qty = inv.get_qty(warehouse_id, d.part_id)
        if d.is_absolute:
            new_qty = d.adj
        else:
            new_qty = old_qty + d.adj
            item['is_relative'] = True
            has_relative_deltas = True
        dif_qty = new_qty - old_qty
        dif_val = dif_qty * d.part.avg_cost()
        item['qty_old_list'].append( (old_qty, d.part) )
        item['qty_new_list'].append( (new_qty, d.part) )
        item['qty_dif_list'].append( (dif_qty, d.part) )
        item['value_diff'] += dif_val
        total_value_change += dif_val

    inventory_list = []
    for part, item in inv_items.items():
        inventory_list.append (item)
    inventory_list.sort(key=lambda x: x['part'].id)
    inventory_list.sort(key=operator.itemgetter('value_diff'))
    return inventory_list, total_value_change, has_relative_deltas

def get_open_order_line_items(last_order=None):
    """Return query-set of line-items on open orders.  If LAST_ORDER is
    not None, do not consider any orders that are expected to arrive
    later than that LAST_ORDER.

    """
    qs = Line_Item.objects.filter(txtn__order__status=Order.STATUS_OPEN)
    if last_order is not None:
        qs = qs.exclude(txtn__order__expected_arrival_date__gt=\
                        last_order.expected_arrival_date)
    return qs

def get_open_order_summary(last_order=None):
    """Return a list of open orders, sorted by expected arrival date.  If
       LAST_ORDER is not None, orders after the expected arrival date
       of LAST_ORDER are not considered.

       For each open order, return a dictionary with the order ('order')
       and the list of line-items in that order ('items').
    """
    qs = get_open_order_line_items(last_order)
    txtns = []
    prev_txtn = None
    for item in qs.order_by('txtn_id'):
        if prev_txtn != item.txtn_id:
            prev_txtn = item.txtn_id
            entry = {
                'order': item.txtn.order,
                'items': []
            }
            txtns.append(entry)
        entry['items'].append(item)
    txtns.sort(key=lambda x: x['order'].expected_arrival_date)
    return txtns

class Part_Event:
    KIND_CURRENT_INVENTORY = 'current inventory'
    KIND_EXPECTED_SHIPMENT = 'expected shipment'
    KIND_ABSOLUTE_COUNT	   = 'count'

    def __init__(self, event_obj, ts, overdue=False):
        self.event_obj = event_obj
        self.ts = ts
        self.warehouse = None
        self.txtn = None
        self.kind = None
        self.part = None
        self.desc = None
        self.inv  = None
        self.part = None
        self.part_qty = None
        self.overdue = overdue

    def __str__(self):
        return 'obj %s ts %s whouse %s txtn %s kind %s part %s desc %s' % \
            (self.event_obj, self.ts, self.warehouse, self.txtn, self.kind,
             self.part, self.desc)

def get_part_history(part):
    """Get the purchase history for PART.  Returns a list of Part_Event
       instances ordered by descending timestamp.  Each Part_Event has
       a timestamp (ts) when the event occurred, the number of the
       transaction that resulted in the event (txtn), a string
       describing the kind of event it was (kind), a verbose
       descrption of the event (desc), and the inventory-level *after*
       the event occurred (inv).

    """
    part_list = [ p.id for p in part.equivalent_parts() ]
    open_order_list = [ o.txtn_id for o in get_open_order_line_items() ]
    event = []

    # List of assembly IDs that use any parts in PART_LIST:
    assy_ids = Assembly_Item.objects.filter(comp_id__in=part_list) \
                                    .values_list('assy_id', flat=True)

    part_or_assy_list = part_list[:]
    part_or_assy_list.extend(assy_ids)

    inv = Part_Inventory()

    # get open orders for the part:
    for item in Line_Item.objects.filter(part_id__in=part_or_assy_list) \
                                 .filter(txtn_id__in=open_order_list):
        order = item.txtn.order

        # sort overdue orders as if they arrive tomorrow:
        dt = order.expected_arrival_date
        ts = timezone.make_aware(datetime.combine(dt, datetime.min.time()),
                                  timezone.utc)
        limit = timezone.now() + timedelta(days=1)
        overdue = False
        if ts < limit:
            overdue = True
            ts = limit

        if item.qty_remaining_to_ship() > 0:
            if item.part_id in assy_ids:
                qs = item.part.assembly_items().filter(comp_id__in=part_list)
                if not qs.exists():
                    continue
                comp = None
                qty = 0
                for assy_item in qs:
                    comp = assy_item.comp
                    qty += assy_item.qty_with_overage(item.qty)
                pe = Part_Event(item, ts, overdue=overdue)
                pe.part = comp.best_part()
                pe.part_qty = qty
            else:
                pe = Part_Event(item, ts, overdue=overdue)
            event.append(pe)

    # get deltas for the part:
    for delta in Delta.objects.filter(part_id__in=part_list):
        event.append(Part_Event(delta, delta.txtn.ts))

    todays_inventory = Part_Event(None, timezone.now())
    todays_inventory.kind = Part_Event.KIND_CURRENT_INVENTORY
    event.append(todays_inventory)

    # sort from oldest to newest:
    event.sort(key=lambda pe: pe.ts)

    for pe in event:
        if pe.event_obj is None:
            pass
        elif isinstance(pe.event_obj, Line_Item) \
             and hasattr(pe.event_obj.txtn, 'order'):
            inv.apply_order_line_item(pe.event_obj)
            item = pe.event_obj
            txtn = order = item.txtn.order
            order_url = reverse('epic:order_detail',
                                 kwargs={'pk': item.txtn_id})

            if pe.part_qty:
                part_html = html_part_link(pe.part)
                pe.desc = 'Expect use of %d&times;%s by %s ' \
                          '<a href="%s">order</a> placed on %s.' % \
                          (pe.part_qty, part_html, order.vendor, order_url,
                           order.ts.strftime('%x'))
                if pe.overdue:
                    pe.desc += '<br>Shipment is overdue!  ' \
                               'Originally expected on %s.' \
                               % (order.expected_arrival_date.strftime('%x'))
                pe.warehouse = Warehouse.by_name(order.vendor)
            else:
                part_html = html_part_link(item.part_id)
                pe.desc = 'Expect delivery of %d&times;%s from %s ' \
                          '<a href="%s">order</a> placed on %s, ' \
                          'shipping to %s.' % \
                          (item.qty, part_html, order.vendor, order_url,
                           order.ts.strftime('%x'),
                           order.warehouse.name)
                pe.warehouse = order.warehouse_id
            if txtn.notes:
                pe.desc += '<br><em>%s</em>' % txtn.notes
            pe.txtn = txtn.id
            pe.kind = Part_Event.KIND_EXPECTED_SHIPMENT
            pe.part = item.part_id
        elif isinstance(pe.event_obj, Delta):
            delta = pe.event_obj
            inv.apply_delta(delta)
            part_html = html_part_link(delta.part_id)
            txtn = delta.txtn
            omit_dst_warehouse = False
            if hasattr(txtn, 'order'):
                raise error('Unexpected order %s' % txtn.id)
            elif hasattr(txtn, 'shipment'):
                kind = 'shipment'
                txtn_url = reverse('epic:ship_detail', kwargs={'pk': txtn.id})
                ship = txtn.shipment
                if delta.adj < 0:
                    if ship.ordr is not None:
                        desc = '<a href="%s">Used</a> %u&times;%s at' % \
                               (txtn_url, -delta.adj, part_html)
                    else:
                        desc = '<a href="%s">Sent</a> %u&times;%s from %s' % \
                               (txtn_url, -delta.adj, part_html,
                                ship.from_warehouse)
                        omit_dst_warehouse = True
                else:
                    if ship.ordr is not None:
                        url = reverse('epic:order_detail',
                                      kwargs={'pk': ship.ordr_id})
                        frm = '%s <a href="%s">order</a>' \
                              % (ship.ordr.vendor, url)
                        desc = '<a href="%s">Shipped</a> %u&times;%s ' \
                               'from %s to' % \
                               (txtn_url, delta.adj, part_html, frm)
                    else:
                        desc = '<a href="%s">Received</a> %u&times;%s at' % \
                               (txtn_url, delta.adj, part_html)
            elif hasattr(txtn, 'inventory'):
                kind = 'inventory'
                txtn_url = reverse('epic:warehouse_inventory_detail',
                                   kwargs={'warehouse': txtn.warehouse.id,
                                           'pk': txtn.id })
                if delta.is_absolute:
                    desc = '<a href="%s">Counted</a> %u&times;%s at' % \
                           (txtn_url, delta.adj, part_html)
                    kind = Part_Event.KIND_ABSOLUTE_COUNT
                else:
                    desc = '<a href="%s">Adjusted</a> by %d&times;%s at' % \
                           (txtn_url, delta.adj, part_html)
            else:
                raise error('Unexpected transaction %s' % txtn.id)
            if not omit_dst_warehouse:
                desc += ' %s' % delta.warehouse.name
            desc += '.'
            if txtn.notes:
                desc = desc + '<br><em>%s</em>' % \
                       txtn.notes
            pe.warehouse = delta.warehouse_id
            pe.txtn = txtn.id
            pe.kind = kind
            pe.part = delta.part_id
            pe.desc = desc
        else:
            raise error('Unexpected event object %s' % str(pe.event_obj))
        pe.inv = deepcopy(inv)

    todays_inventory.desc = 'Current warehouse stock as of today.'

    # Now reverse so that we have newest to oldest:
    event.reverse()
    return event

def part_history_summary(part, events, full_history=False):
    def warehouse_done(e, w):
        if w not in e.inv.warehouse:
            return True
        if w not in warehouse_absolute:
            return False
        return all(part in warehouse_absolute[w] for part in part_list)

    def warehouse_part_done(w, p):
        return w in warehouse_absolute and p in warehouse_absolute[w]

    def update_warehouse_absolute(e):
        if full_history:
            return
        if isinstance(e.event_obj, Delta) and e.event_obj.is_absolute:
            if e.warehouse not in warehouse_absolute:
                warehouse_absolute[e.warehouse] = {}
            warehouse_absolute[e.warehouse][e.part] = True

    part_list = [ p.id for p in part.equivalent_parts() ]

    # Only show warehouses that have non-zero part counts or expected
    # shipments in the period that we display:
    warehouse_absolute = {}
    warehouses_to_show = {}
    for e in events:
        if warehouse_done(e, e.warehouse):
            continue
        if e.kind == Part_Event.KIND_EXPECTED_SHIPMENT:
            warehouses_to_show[e.warehouse] = True
        else:
            for w in e.inv.warehouse:
                if warehouse_done(e, w):
                    continue
                part_qtys = e.inv.warehouse[w]
                for p in part_list:
                    if p not in part_qtys:
                        continue
                    if part_qtys[p].qty != 0:
                        if not warehouse_part_done(w, p):
                            warehouses_to_show[w] = True
        update_warehouse_absolute(e)
    for w in warehouses_to_show:
        warehouses_to_show[w] = Warehouse.objects.get(pk=w)

    now = timezone.now()
    first_present = True
    warehouse_absolute = {}
    event_summary = []
    for e in events:
        if (e.kind != Part_Event.KIND_CURRENT_INVENTORY
            and e.kind != Part_Event.KIND_EXPECTED_SHIPMENT
            and (e.warehouse not in warehouses_to_show
                 or warehouse_part_done(e.warehouse, e.part))):
            continue

        summary = {}
        cls = ''
        if e.ts > now:
            cls = 'danger' if e.overdue else 'warning'
        elif first_present and e.ts <= now:
            cls = 'success'
            first_present = False
        summary['class'] = cls
        summary['ts'] = e.ts
        summary['desc'] = e.desc
        summary['warehouses'] = []
        for w in warehouses_to_show:
            items = []
            if w in e.inv.warehouse:
                part_qtys = e.inv.warehouse[w]
                for p in part_list:
                    if p not in part_qtys or warehouse_part_done(w, p):
                        continue
                    part = Part.objects.get(pk=p)
                    items.append({ "qty": part_qtys[p].qty, "part": part })
            summary['warehouses'].append(items)
        event_summary.append(summary)
        update_warehouse_absolute(e)

    return {
        "warehouses": warehouses_to_show.values(),
        "events": event_summary
    }

def page_sibling(model, pk, backward):
    op_name = 'pk__' + ('lt' if backward else 'gt')
    qs = model.objects.order_by('-pk' if backward else 'pk') \
                      .filter(**{ op_name: pk })[:1] \
                      .values_list('pk', flat=True)
    return qs[0] if qs.exists() else None

def html_page_sibling(url_name, model, pk, backward):
    sibling_pk = page_sibling(model, pk, backward)
    html = '<a class="btn btn-default" '
    if sibling_pk is None:
        html += 'disabled="disabled"'
    else:
        url = reverse(url_name, kwargs={'pk': sibling_pk})
        html += 'href="%s"' % (url)
    html += '>'
    if backward:
        btn_dir = 'Prev.'
        icon_name = 'left'
    else:
        btn_dir = 'Next'
        icon_name = 'right'
    html += '%s %s <i class="glyphicon glyphicon-chevron-%s">' \
            % (btn_dir, model.__name__, icon_name)
    html += '</i></a>'
    return html

def html_page_nav(url_name, model, pk):
    """Create the 'Previous' and 'Next' navigation buttons for a paginator."""
    html  = html_page_sibling(url_name, model, pk, backward=True)
    html += ' '
    html += html_page_sibling(url_name, model, pk, backward=False)
    return html

def html_list_pager(page_obj, num_neighbors=5, page_name=lambda pg: pg,
                    queries=None, key='page'):
    """Given a Django Page object, return a bootstrap pageinator which
    provides direct access for a couple (NUM_NEIGHBORS) of neighboring
    pages.  If not all pages are directly accessible, ellipses are
    used to provide access on a neighbor-group by neighbor-group
    basis.  PAGE_NAME can be used to translate the page number to a custom
    page name.

    """
    def url(page_number):
        if page_number < 1 or page_number > num_pages:
            return ""
        q = queries[:]
        q.append('%s=%d' % (key, page_number))
        return '?' + "&".join(q)

    if queries is None:
        queries=[]

    num_pages = page_obj.paginator.num_pages

    if num_pages <= 1:
        return ""
    html  = '<nav><ul class="pagination">'
    # previous-page button:
    prev_symbol = '<span aria-hidden="true">&laquo;</span>'
    if page_obj.number <= 1:
        html += '<li class="disabled">%s</li>' % (prev_symbol)
    else:
        html += '<li><a href="%s">%s</a></li>' % (url(page_obj.number - 1),
                                                  prev_symbol)
    first_page = page_obj.number - num_neighbors
    if first_page < 1:
        first_page = 1
    if first_page > 1:
        right = first_page - 1
        left  = right - (num_neighbors - 1)
        if left < 1:
            left = 1
        ellipsis_page = (right + left) / 2
        html += '<li><a href="%s">&hellip;</a></li>' % (url(ellipsis_page))
        first_page += 1 # ellipsis occupies one of the neighbor blocks...
    for pg in range(first_page, page_obj.number):
        html += '<li><a href="%s">%s</a></li>' % (url(pg), page_name(pg))
    html += '<li class="active"><a>%s</a></li>' % page_name(page_obj.number)

    last_page = page_obj.number + num_neighbors
    if last_page > num_pages:
        last_page = num_pages
    if last_page < num_pages:
        left  = last_page + 1
        right = left + (num_neighbors - 1)
        if right > num_pages:
            right = num_pages
        ellipsis_page = (right + left) / 2
        last_page -= 1 # ellipsis occupies one of the neighbor blocks...

    for pg in range(page_obj.number + 1, last_page + 1):
        html += '<li><a href="%s">%s</a></li>' % (url(pg), page_name(pg))
    if last_page < num_pages:
        html += '<li><a href="%s">&hellip;</a></li>' % (url(ellipsis_page))

    # next-page button:
    next_symbol = '<span aria-hidden="true">&raquo;</span>'
    if page_obj.number >= num_pages:
        html += '<li class="disabled">%s</li>' % (next_symbol)
    else:
        html += '<li><a href="%s">%s</a></li>' % (url(page_obj.number + 1),
                                                  next_symbol)
    html += '</ul></nav>'
    return html

def get_field(cls, field_name):
    for f in cls._meta.fields:
        if f.name == field_name:
            return f
    return None

def get_model_fields(obj, fields,
                     map = lambda name, val, vname: (vname, val)):
    """Get the model fields and values for OBJ.  Any model fields not
    listed in FIELDS are skiiped.  The values are HTML-escaped so they
    are safe to be output directly.
    """
    field_list = []
    for field_name in fields:
        f = get_field(obj.__class__, field_name)
        if f is None:
            continue
        if f.name + '_ptr_id' in obj.__dict__:
            v = obj.__dict__[f.name + '_ptr_id']
        elif f.name + '_id' in obj.__dict__:
            v = obj.__dict__[f.name + '_id']
        else:
            v = obj.__dict__[f.name]
        get_name = 'get_' + f.name + '_display'
        if hasattr(obj, get_name):
            v = getattr(obj, get_name)()
        vname = f.verbose_name
        if not vname[0].isupper():
            vname = vname.capitalize()
        name, v = map(f.name, escape(v), vname)
        field_list.append([name, v])
    return field_list

def get_initial_from_post(request, item_prefix, txtn_model, item_model):
    """Parses the POST data from a form that provides initial data for a
    transaction object (e.g., Order or Shipment) and the associated
    items.  ITEM_PREFIX is the prefix used for the items, TXTN_MODEL is
    the Django model for the transaction and ITEM_MODEL tha of the items.
    These are used to convert the form data to the Python data needed for
    initialization.  Returns two lists: the initial data of the transaction
    and that of the items.

    """
    prefix_pattern = re.compile(r'^%s-(\d+)-(.*)' % item_prefix)
    items = {}
    txtn_initial = {}
    for name, value in request.POST.items():
        m = prefix_pattern.match(name)
        if m:
            idx = m.group(1)
            field_name = m.group(2)
            if idx not in items:
                items[idx] = {}
            for f in item_model._meta.fields:
                if f.name == field_name:
                    items[idx][field_name] = f.to_python(value)
        else:
            for f in txtn_model._meta.fields:
                if f.name == name:
                    txtn_initial[name] = f.to_python(value)
    items_initial = []
    for key, val in items.items():
        items_initial.append(val)
    return txtn_initial, items_initial

def breadcrumb(path):
    if path[len(path) - 1] == '/':
        path = path[:-1]
    comps = path.split('/')
    content = ''
    for i in range(len(comps)):
        if i == 0:
            continue
        else:
            path = '/'.join(comps[0:i+1])
            name = comps[i]
            if name == 'epic':
                name = 'EPIC'
            elif name == 'bom':
                name = 'BOM'
            else:
                name = name.capitalize()
        if i == len(comps) - 1:
            content += '<li class="active">%s</li>' % name
        else:
            content += '<li><a href="%s">%s</a></li>' % (path, name)
    return ('<ol class="breadcrumb">%s</ol>' % content)
