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
import crispy_forms.helper
import hashlib
import json
import math
import operator
import os
import re

from collections import OrderedDict
from dal import autocomplete
from datetime import date, datetime, timedelta

from django import forms
from django.db import transaction
from django.conf import settings as cfg
from django.contrib.auth.decorators import permission_required
from django.contrib.staticfiles import finders
from django.core.exceptions import ObjectDoesNotExist, ValidationError, \
    PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.forms import ModelForm, TextInput
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms.utils import ErrorList
from django.http import Http404, HttpResponse, HttpResponseRedirect, \
    HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import defaultfilters
from django.utils import timezone
from django.views import generic

from epic import perms
from epic.apps import EPIC_App_Config
from epic.footprints import Footprints
from epic.lib import *
from epic.models import *
from epic.widgets import DateTimePicker

KiB = 1024
MiB = (KiB*KiB)

def crispy_form_helper():
    helper = crispy_forms.helper.FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-3'
    helper.field_class = 'col-md-9'
    helper.form_tag = False
    return helper

def crispy_inline_form_helper():
    helper = crispy_forms.helper.FormHelper()
    # See https://github.com/maraujop/django-crispy-forms/issues/376
    # as to why we can't used bootstrap3/table_inline_formset.html
    # directly.  It results in a mangled 'Delete' checkbox column.
    helper.template = 'epic/inline_formset.html'
    helper.form_tag = False
    return helper

def assert_permission(request, perm):
    if not request.user.has_perm(perm):
        raise PermissionDenied

class Part_Autocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        assert_permission(self.request, perms.VIEW)
        if self.q:
            if re.match(r'\d+$', self.q, re.I):
                # if search if for a number, return that part alone:
                qs = Part.objects.filter(id=self.q)
                if len(qs) == 1:
                    return qs
            qs  = Part.objects.filter(mfg__icontains=self.q)
            qs |= Part.objects.filter(mfg_pn__icontains=self.q)
        else:
            qs = Part.objects.all()
        self.q = None
        return qs

    def get_result_label(self, result):
        return result.choice_label()

    @staticmethod
    def widget(**kwargs):
        return autocomplete.ModelSelect2(
            url='epic:part-dal', attrs={'data-placeholder': 'Part #?'},
            **kwargs)

    @staticmethod
    def widget_multiple():
        return autocomplete.ModelSelect2Multiple(
            url='epic:part-dal',
            attrs={'data-placeholder': 'Part #?'})


class Order_Autocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        assert_permission(self.request, perms.VIEW)
        # It would be nice to limit the choices to just open orders, but
        # that doesn't work when we open an existing shipment which is
        # associated with a closed order.  In that case, we lose the order
        # because that closed order won't be a valid choice...
        #qs = qs.filter (status=Order.STATUS_OPEN)
        if self.q:
            if re.match(r'\d+$', self.q):
                # q is numeric: search open orders for transaction
                # numbers containing that numeric string:
                for c in Order.objects.all():
                    if re.match('\d*%s\d*' % self.q, '%d' % c.id):
                        qs |= Order.objects.filter(id=c.id)
                if qs.exists():
                    return qs.order_by('-id')
            qs  = Order.objects.filter(vendor__name__contains=self.q)
            qs |= Order.objects.filter(warehouse__name__contains=self.q)
        else:
            qs = Order.objects.all()
        self.q = None
        return qs.order_by('-id')

    def get_result_label(self, result):
        return result.choice_label()

    @staticmethod
    def widget():
        return autocomplete.ModelSelect2(url='epic:order-dal',
                                         attrs={
                                             'data-placeholder': 'Order #?'
                                         })

def get_mfg_list():
    return Part.objects.values_list('mfg', flat=True).distinct()

class Mfg_Autocomplete(autocomplete.Select2ListView):
    create = lambda self, text: text

    def __init__(self, *args, **kwargs):
        super(Mfg_Autocomplete, self).__init__(*args, **kwargs)
        self.choice_list = get_mfg_list()

    def get_list(self):
        assert_permission(self.request, perms.VIEW)
        return self.choice_list

    @staticmethod
    def widget():
        return autocomplete.ListSelect2(url='epic:mfg-dal',
                                    attrs={
                                        'data-placeholder': 'Manufacturer?'
                                    })

class Footprint_Autocomplete(autocomplete.Select2ListView):
    choices = Footprints.get()

    def get_list(self):
        assert_permission(self.request, perms.VIEW)
        return self.choices

    @staticmethod
    def widget():
        return autocomplete.Select2(url='epic:footprint-dal',
                                    attrs={
                                        'data-placeholder': 'Footprint?'
                                    })

@permission_required(perms.VIEW)
def part_info(request):
    """This lets Javascript query for part info.  The query-format is:

    /epic/part/info/?pid=PART_ID&vid=VENDOR_ID

    where PID is the part id and VID is the id of the vendor.  If only
    PID is specified, the part-id (pid), manufacturer (mfg),
    manufacturer's part-number (mfg_pn), and the target-price (price)
    are returned.  The values are returned as a dictionary, indexed by
    the part-number.

    If PID and VID are specified and the part is available from the
    specified vendor, additionally the vendor's part-number (vendor_pn)
    is returned.  Also, instead of the part's target-price, the
    vendor's price is returned (price).

    PID may also be a comma-separated list of part-ids, in which case
    info for each of those parts is returned.

    If only VID is specified, all that vendor's parts are returned.

    """
    pid = request.GET.get('pid', '')
    if pid:
        try:
            pid_list = [ int(pid_str) for pid_str in pid.split(',')]
        except ValueError:
            pid = None
    vid = request.GET.get('vid', None)
    qs = Part.objects.none()
    if vid:
        try:
            qs = Vendor_Part.objects.filter(vendor_id=int(vid))
            if pid:
                qs = qs.filter(part_id__in=pid_list)
                if len(qs) == 0:
                    qs = Part.objects.filter(id__in=pid_list)
        except ValueError:
            vid = None
    elif pid:
        qs = Part.objects.filter(id__in=pid_list)

    info = {}
    for part in qs:
        i = {}
        if isinstance(part, Vendor_Part):
            vp = part
            part = vp.part
            i['vendor_pn'] = vp.vendor_pn
            i['price'] = '%s' % vp.price
        else:
            i['price'] = '%s' % part.target_price
        i['mfg'] = part.mfg
        i['mfg_pn'] = part.mfg_pn
        info[part.id] = i
    json_info = json.dumps(info)
    return HttpResponse(json_info, content_type='application/json')

class PartMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.choice_label()

class Part_Edit_Form(ModelForm):
    substitutes = PartMultipleChoiceField(
        required=False, queryset=Part.objects.all(),
        widget=Part_Autocomplete.widget_multiple()
    )
    mfg = autocomplete.Select2ListCreateChoiceField(
        choice_list=get_mfg_list,
        widget=Mfg_Autocomplete.widget()
    )
    footprint = autocomplete.Select2ListChoiceField(
        required=False, choice_list=Footprints.get(),
        widget=autocomplete.ListSelect2(
            url='epic:footprint-dal',
            attrs={'data-placeholder': 'Footprint?'})
    )

    def __init__(self, *args, **kwargs):
        super(Part_Edit_Form, self).__init__(*args, **kwargs)

        if kwargs['instance']:
            substitutes_initial = list(self.instance.equivalent_parts())
            substitutes_initial.remove(self.instance)
            self.fields['substitutes'].initial = substitutes_initial

        self.helper = crispy_form_helper()

    def clean_footprint(self):
        return self.cleaned_data.get('footprint').strip()

    def save(self, commit=True):
        instance = super(Part_Edit_Form, self).save(commit)

        old_set = set(instance.equivalent_parts())
        new_set = set([ instance ])

        for sub in self.cleaned_data['substitutes']:
            new_set.add(sub)

        added = new_set - old_set
        deleted = old_set - new_set
        current = old_set.copy()
        changed = set()

        for d in deleted:
            current.remove(d)
            for prev in current:
                if prev.substitute == d:
                    prev.substitute = d.substitute
                    changed.add(prev)
            if d.substitute is not None:
                d.substitute = None
                changed.add(d)

        for a in added:
            for prev in current:
                if prev.substitute is None:
                    prev.substitute = a
                    changed.add(prev)
            current.add(a)

        for c in changed:
            c.save()

        return instance

    def clean_substitutes(self):
        instance_equivalent = (
            None if self.instance is None else self.instance.equivalent_parts()
        )
        for part in self.cleaned_data['substitutes']:
            params = {'part': format_part_number(int(part.id))}
            if part == self.instance:
                raise ValidationError(
                    'Part %(part)s cannot be its own substitute.',
                    params=params)
            if (part not in instance_equivalent and
                len(part.equivalent_parts()) != 1 and
                len(instance_equivalent) != 1):
                raise ValidationError(
                    'Part %(part)s is already in a different '
                    'substitute set.  Remove it from that set '
                    'before adding it to this set.',
                    params=params)

        return self.cleaned_data['substitutes']

    class Meta:
        model = Part
        fields = [ 'mfg', 'mfg_pn', 'descr', 'val', 'footprint', 'mounting',
                   'target_price', 'overage', 'spq', 'lead_time',
                   'status', 'datasheet', 'notes' ]


class Vendor_Part_Edit_Formset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(Vendor_Part_Edit_Formset, self).__init__(*args, **kwargs)
        self.helper = crispy_inline_form_helper()

    def add_fields(self, form, index):
        super(Vendor_Part_Edit_Formset, self).add_fields(form, index)
        form.fields['status'].help_text = ''

    def clean(self):
        super(Vendor_Part_Edit_Formset, self).clean()

        for form in self.forms:
            vendor = form.cleaned_data.get('vendor')
            if vendor and form.cleaned_data.get(DELETION_FIELD_NAME):
                qs = Order.objects.filter(vendor_id=vendor.id) \
                                  .filter(line_item__part_id=self.instance.id)
                if qs.exists():
                    errors = form._errors.setdefault('vendor_pn',
                                                     ErrorList())
                    errors.append('Vendor Part # cannot be deleted as it is '
                                  'referenced by one or more orders.')
                    raise ValidationError('Vendor Part # in use')

class Vendor_Part_Edit_Form(ModelForm):
    class Meta:
        model = Vendor_Part
        fields = [ 'vendor', 'vendor_pn', 'price', 'status' ]

    def __init__(self, *args, **kwargs):
        super(Vendor_Part_Edit_Form, self).__init__(*args, **kwargs)
        self.fields['vendor_pn'].widget \
                                .attrs['placeholder'] = 'Vendor\'s Part #?'
        self.fields['price'].widget.attrs['placeholder'] = 'Price?'

@permission_required(perms.VIEW)
def part_list(request):
    return Part_List_View.as_view()(request)

@permission_required(perms.VIEW)
def part_detail(request, pk):
    return Part_Detail_View.as_view()(request, pk=pk)

@permission_required(perms.VIEW)
def part_bom_detail(request, pk):
    # Part detail already includes BOM:
    return Part_Detail_View.as_view()(request, pk=pk)

class Assembly_Item_Edit_Formset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(Assembly_Item_Edit_Formset, self).__init__(*args, **kwargs)
        self.helper = crispy_inline_form_helper()

    def add_fields(self, form, index):
        super(Assembly_Item_Edit_Formset, self).add_fields(form, index)
        ndict = OrderedDict()
        # first, copy all hidden fields:
        for f in form.fields:
            if form.fields[f].widget.is_hidden:
                ndict[f] = form.fields[f]
        # second, rearrange the order of the visible fields and add
        # virtual (calculated) fields:
        if 'qty' in form.fields:
            ndict['qty'] = form.fields['qty']
            ndict['qty'].widget.attrs['size'] = 6
            ndict['qty'].widget.attrs['placeholder'] = 'Quantity?'
            ndict['qty'].help_text = ''
        ndict['comp'] = PartChoiceField(
            queryset=Part.objects.all(), widget=Part_Autocomplete.widget())
        ndict['refdes'] = form.fields['refdes']
        ndict['refdes'].widget.attrs['rows'] = 2
        ndict['refdes'].help_text = ''
        ndict[DELETION_FIELD_NAME] = form.fields[DELETION_FIELD_NAME]

        form.fields = ndict

    def initialize_virtual_fields(self):
        # setup initial data for calculated (virtual) fields:
        for form in self:
            init = form.initial
            if 'refdes' in init:
                refdes_list = re.findall(r'([^, ]+)', init['refdes'])
                init['refdes'] = ' '.join(refdes_list)

    def clean(self):
        super(Assembly_Item_Edit_Formset, self).clean()

        for form in self.forms:
            if 'comp' in form.cleaned_data:
                comp = form.cleaned_data['comp']
                if comp.id == self.instance.id:
                    errors = form._errors.setdefault('comp', ErrorList())
                    errors.append('BOM may contain the assembly-part '
                                  'itself.')

@transaction.atomic
@permission_required(perms.EDIT)
def part_bom_edit(request, pk):
    part = get_object_or_404(Part, pk=pk)
    my_url = reverse('epic:part_bom_edit', kwargs={'pk': pk})
    prev_url = reverse('epic:part_detail', kwargs={'pk': pk})

    BOM_Formset = inlineformset_factory(Part, Assembly_Item,
                                        formset=Assembly_Item_Edit_Formset,
                                        fk_name='assy',
                                        fields= [ 'comp', 'qty', 'refdes' ])
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(prev_url)

        bom_form = BOM_Formset(request.POST, instance=part)
        if bom_form.is_valid():
            part.last_bom_mod_type = Part.LAST_MOD_TYPE_USER
            part.last_bom_mod_name = request.user.get_username()
            part.save()

            bom_form.save()
            if 'save-and-done' in request.POST:
                return HttpResponseRedirect(prev_url)
            return HttpResponseRedirect(my_url)
    else:
        bom_form = BOM_Formset(instance=part)

    bom_form.initialize_virtual_fields()
    crumb = breadcrumb(my_url)
    return render(request, 'epic/bom_edit.html',
                  {
                      'pk': pk,
                      'bom_form': bom_form,
                      'breadcrumb': crumb,
                  })

@transaction.atomic
@permission_required(perms.EDIT)
def part_edit(request, pk):
    def prev_url(pk):
        if pk is None:
            return reverse('epic:part_list')
        return reverse('epic:part_detail', kwargs={'pk': pk})

    if pk is None:
        part = None
        my_url = reverse('epic:part_add')
    else:
        part = get_object_or_404(Part, pk=pk)
        my_url = reverse('epic:part_edit', kwargs={'pk': pk})

    Vendor_Part_Formset = inlineformset_factory(Part, Vendor_Part,
                                                form=Vendor_Part_Edit_Form,
                                            formset=Vendor_Part_Edit_Formset)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(prev_url(pk))

        part_form = Part_Edit_Form(request.POST, instance=part)
        vendor_form = Vendor_Part_Formset(request.POST, instance=part)
        if part_form.is_valid() and vendor_form.is_valid():
            new_part = part_form.save()
            pk = new_part.pk

            new_part = get_object_or_404(Part, pk=pk)
            new_vendor_form = Vendor_Part_Formset(request.POST,
                                                  instance=new_part)
            new_vendor_form.is_valid()	# re-create cleaned data for .save()
            new_vendor_form.save()
            return HttpResponseRedirect(prev_url(pk))
    else:
        part_form = Part_Edit_Form(instance=part)
        vendor_form = Vendor_Part_Formset(instance=part)

    crumb = breadcrumb(my_url)
    return render(request, 'epic/part_edit.html',
                  {
                      'pk': pk,
                      'part_form': part_form,
                      'breadcrumb': crumb,
                      'vendor_form': vendor_form
                  })

@permission_required(perms.EDIT)
def part_add(request):
    return part_edit(request, None)

def here_are_all_or_some(item_name_prefix, suffix_singular, suffix_plural,
                         items, max_items=5):
    msg = 'Here '
    msg += 'is' if len(items) == 1 else 'are'
    msg += '' if len(items) <= max_items else ' some of'
    msg += ' the ' + item_name_prefix \
           + (suffix_singular if len(items) == 1 else suffix_plural) + ': '
    msg += ', '.join(items[:max_items])
    if len(items) > max_items:
        msg += ', &hellip;'
    else:
        msg += '.'
    return msg

def get_parent_url(url):
    m = re.match(r'(.*/)[^/]+/?$', url)
    if not m:
        raise Http404
    return m.group(1)

@permission_required(perms.EDIT)
def part_delete(request, pk):
    part = get_object_or_404(Part, pk=pk)
    my_url = reverse('epic:part_delete', kwargs={'pk': pk})
    parent_url = get_parent_url(my_url)

    # Check if the part is being referenced:
    #	1) In any Delta
    #	2) As a component in an assembly
    #	3) In any Line_Item
    # If so, refuse to delete, as that could throw everything off balance.
    # Note that it is OK if the Part is an Assembly_Item itself
    # or if a Vendor_Part refers to it (as long as the above conditions are
    # satisfied).  Those will be deleted automatically and there are no
    # negative effects in doing so.
    txtns  = Transaction.objects.filter(delta__part_id=part.id)
    txtns |= Transaction.objects.filter(line_item__part_id=part.id)
    txtns  = txtns.distinct().order_by('-id')
    assys  = Part.objects.filter(assembly_item_part__comp_id=part.id) \
                         .distinct()
    if txtns.exists() or assys.exists():
        messages = [ 'Sorry, part %s cannot be deleted because ' \
                     % part.html_link()]
        sep = ''
        if txtns.exists():
            messages[0] += '%d transaction%s refer%s to it' \
                           % (len(txtns), '' if len(txtns) == 1 else 's',
                              's' if len(txtns) == 1 else '')
            messages.append(here_are_all_or_some('transaction', '', 's',
                                                 [ txtn.html_link() \
                                                   for txtn in txtns ]))
            sep  = ' and '
        if assys.exists():
            messages[0] += '%s%d assembl%s use%s it' % \
                           (sep, len(assys),
                            'y' if len(assys) == 1 else 'ies',
                            's' if len(assys) == 1 else '')
            messages.append(here_are_all_or_some('assembl', 'y', 'ies',
                                                 [ assy.html_link() \
                                                   for assy in assys ]))
        messages[0] += '.'

        return render(request, 'epic/delete_error.html',
                      {
                          'breadcrumb': breadcrumb(my_url),
                          'parent_url': parent_url,
                          'messages': messages
                      })
    part.delete()
    return HttpResponseRedirect(get_parent_url(parent_url))

class Part_List_View(generic.ListView):
    model = Part
    paginate_by = 100	# this makes the the paging match the 3rd digit of PN

    def get_queryset(self):
        return super(Part_List_View, self).get_queryset().order_by('id')

    def get_context_data(self, **kwargs):
        context = super(Part_List_View, self).get_context_data(**kwargs)

        context['breadcrumb'] = breadcrumb(reverse('epic:part_list'))
        context['list_pager'] = html_list_pager(context['page_obj'],
                                                page_name=lambda pg: pg - 1)
        return context

class Part_Detail_View(generic.DetailView):
    model = Part
    fields = [ 'mfg', 'mfg_pn', 'val', 'descr', 'datasheet',
               'footprint', 'mounting',
               'target_price', 'overage', 'spq', 'lead_time', 'status',
               'notes' ]

    def get_history_filter(self):
        if 'ht' in self.request.GET:
            return self.request.GET['ht']
        return 'truncated'

    def get_context_data(self, **kwargs):

        def map_fields(name, value, verbose_name):
            if name != 'mfg_pn':
                return verbose_name, value
            args = {
                'mfg'   : self.object.mfg,
                'mfg_pn': self.object.mfg_pn
            }
            ds_link = ''
            if self.object.datasheet:
                ds_link = ('&ensp;<a href="%s" target="datasheet">'
                           '<i class="glyphicon glyphicon-book"></i></a>'
                           % self.object.datasheet.ds_file.url)
            else:
                ds_link = ('&ensp;<a href="%s" target="datasheet_add">'
                           '<i class="glyphicon glyphicon-plus"></i></a>'
                           % reverse('epic:datasheet_add_part',
                                     kwargs={'pk': self.object.id}))

            url = 'https://octopart.com/partsearch#!?q={mfg}%20{mfg_pn}' \
                .format(**args)
            return verbose_name, \
                ('%s%s&ensp;<a href="%s" target="part_lookup">'
                 '<img src="%s" alt=''></a>'
                 % (value, ds_link, url, os.path.join(cfg.STATIC_URL,
                                                      'epic/img/octopart.ico')))

        assemblies = get_assemblies_using_part(self.object)
        part_users = []
        for assy in assemblies:
            name = get_assembly_name(assy)
            url = reverse('epic:part_detail', kwargs={'pk': assy.id})
            part_users.append('<a href="%s">%s</a>' % (url, name))

        fields = get_model_fields(self.object, self.fields, map_fields)

        subs = set(self.object.equivalent_parts())
        subs.remove(self.object)
        subs = sorted(subs, key = lambda x: x.id)
        subs = html_list_or_none(map(lambda s: html_part_link(s), subs))

        fields.append([ 'Substitutes', subs ])

        vendor_parts = Vendor_Part.objects.filter(part_id=self.object.id)

        bom = [ ]
        total_target_cost = 0
        for item in self.object.assembly_items():
            best_part = item.comp.best_part()
            refdes_list = item.refdes.split(',')
            total_target_cost += item.qty * best_part.target_price
            avg_cost = best_part.avg_cost()
            bom.append({
                'best_part':		best_part,
                'assy_item':		item,
                'refdes_list':		refdes_list,
                'avg_cost':		avg_cost,
                'amount':		item.qty * avg_cost,
                'cumulative_cost':	0
            })
        bom.sort(key = lambda x: x['amount'], reverse=True)
        cumulative_cost = 0
        for row in bom:
            cumulative_cost += row['amount']
            row['cumulative_cost'] = cumulative_cost
        cost_summary = { 'part': {}, 'cmp': {}, 'tot': { 'tgt': 0, 'avg': 0 } }
        cost_summary['part']['tgt'] = self.object.target_price
        cost_summary['part']['avg'] = self.object.avg_cost()
        cost_summary['cmp']['avg'] = cumulative_cost
        cost_summary['cmp']['tgt'] = total_target_cost
        for kind in [ 'tgt', 'avg' ]:
            cost_summary['tot'][kind] += (cost_summary['part'][kind] +
                                          cost_summary['cmp'][kind])

        history = get_part_history(self.object)

        part_list = [ p.id for p in self.object.equivalent_parts() ]
        open_order_items = get_open_order_line_items() \
            .filter(part_id__in=part_list)

        pk = self.object.id
        ht = self.get_history_filter()

        context = super(Part_Detail_View, self).get_context_data(**kwargs)
        context['breadcrumb'] = breadcrumb(reverse('epic:part_detail',
                                                   kwargs={'pk': pk}))
        context['fields'] = fields
        context['vendor_parts'] = vendor_parts
        context['part_users'] = html_list_or_none(part_users)
        context['bom'] = bom
        context['cost_summary'] = cost_summary
        context['page_nav'] = html_page_nav('epic:part_detail', Part, pk)
        context['history'] = part_history_summary(self.object, history,
                                                  ht == 'full')
        context['ht'] = ht
        context['open_order_items'] = open_order_items
        return context

class Warehouse_Edit_Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super(Warehouse_Edit_Form, self).__init__(*args, **kwargs)
        self.helper = crispy_form_helper()

    class Meta:
        model = Warehouse
        fields = [ 'name', 'address' ]

class Warehouse_List_View(generic.ListView):
    model = Warehouse
    paginate_by = 50

    def get_queryset(self):
        return super(Warehouse_List_View, self).get_queryset() \
                                               .order_by('name')

    def get_context_data(self, **kwargs):
        crumb = breadcrumb(reverse('epic:warehouse_list'))
        context = super(Warehouse_List_View, self).get_context_data(**kwargs)
        context['breadcrumb'] = crumb
        context['list_pager'] = html_list_pager(context['page_obj'])
        return context

class Warehouse_Detail_View(generic.DetailView):
    model = Warehouse
    fields = [ 'name', 'address' ]

    def get_context_data(self, **kwargs):
        pk = self.object.id

        inventories = self.object.inventories().order_by('-ts')
        paginator = Paginator(inventories, 50)
        page = self.request.GET.get('ipg')
        try:
            inventories = paginator.page(page)
        except PageNotAnInteger:
            inventories = paginator.page(1)
        except EmptyPage:
            inventories = paginator.page(paginator.num_pages)

        txtns  = Transaction.objects.filter(warehouse_id=pk)
        txtns |= Transaction.objects.filter(shipment__from_warehouse_id=pk)
        txtns = txtns.distinct().order_by('-ts')
        paginator = Paginator(txtns, 50)
        page = self.request.GET.get('tpg')
        try:
            txtns = paginator.page(page)
        except PageNotAnInteger:
            txtns = paginator.page(1)
        except EmptyPage:
            txtns = paginator.page(paginator.num_pages)

        context = super(Warehouse_Detail_View, self).get_context_data(**kwargs)
        # we don't want to depend on having
        # django.core.context_processors.request enabled:
        context['request'] = self.request
        context['fields'] = get_model_fields(self.object, self.fields)
        context['breadcrumb'] = breadcrumb(reverse('epic:warehouse_detail',
                                                   kwargs={'pk': pk}))
        context['inventories'] = inventories
        context['inventories_pager'] = html_list_pager(inventories, key='ipg')
        context['txtns'] = txtns
        context['txtns_pager'] = html_list_pager(txtns, key='tpg')
        return context

class Vendor_List_View(generic.ListView):
    model = Vendor
    paginate_by = 50

    def get_queryset(self):
        return super(Vendor_List_View, self).get_queryset().order_by('name')

    def get_context_data(self, **kwargs):
        crumb = breadcrumb(reverse('epic:vendor_list'))
        context = super(Vendor_List_View, self).get_context_data(**kwargs)
        context['breadcrumb'] = crumb
        context['list_pager'] = html_list_pager(context['page_obj'])
        return context

class Vendor_Detail_View(generic.DetailView):
    model = Vendor
    fields = [ 'name', 'search_url' ]

    def get_context_data(self, **kwargs):
        pk = self.object.id

        vps = Vendor_Part.objects.filter(vendor_id=pk).order_by('id')
        paginator = Paginator(vps, 50)
        page = self.request.GET.get('vpg')
        try:
            vps = paginator.page(page)
        except PageNotAnInteger:
            vps = paginator.page(1)
        except EmptyPage:
            vps = paginator.page(paginator.num_pages)

        txtns  = Transaction.objects.filter(order__vendor__id=pk)
        txtns |= Transaction.objects.filter(shipment__ordr__vendor_id=pk)
        txtns  = txtns.distinct().order_by('-ts')
        paginator = Paginator(txtns, 50)
        page = self.request.GET.get('tpg')
        try:
            txtns = paginator.page(page)
        except PageNotAnInteger:
            txtns = paginator.page(1)
        except EmptyPage:
            txtns = paginator.page(paginator.num_pages)

        context = super(Vendor_Detail_View, self).get_context_data(**kwargs)
        # we don't want to depend on having
        # django.core.context_processors.request enabled:
        context['request'] = self.request
        context['vps'] = vps
        context['vps_pager'] = html_list_pager(vps, key='vpg')
        context['txtns'] = txtns
        context['txtns_pager'] = html_list_pager(txtns, key='tpg')
        context['breadcrumb'] = breadcrumb(reverse('epic:vendor_detail',
                                                   kwargs={'pk': pk}))
        context['fields'] = get_model_fields(self.object, self.fields)
        return context

class Vendor_Edit_Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super(Vendor_Edit_Form, self).__init__(*args, **kwargs)
        self.helper = crispy_form_helper()

    class Meta:
        model = Vendor
        fields = [ 'name', 'search_url' ]

@permission_required(perms.VIEW)
def vendor_list(request):
    return Vendor_List_View.as_view()(request)

@permission_required(perms.VIEW)
def vendor_detail(request, pk):
    return Vendor_Detail_View.as_view()(request, pk=pk)

@transaction.atomic
@permission_required(perms.EDIT)
def vendor_edit(request, pk):
    def prev_url(pk):
        if pk is None:
            return reverse('epic:vendor_list')
        return reverse('epic:vendor_detail', kwargs={'pk': pk})

    if pk is None:
        vendor = None
        my_url = reverse('epic:vendor_add')
    else:
        vendor = get_object_or_404(Vendor, pk=pk)
        my_url = reverse('epic:vendor_edit', kwargs={'pk': pk})

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(prev_url(pk))

        form = Vendor_Edit_Form(request.POST, instance=vendor)
        if form.is_valid():
            new_form = form.save()
            return HttpResponseRedirect(prev_url(new_form.pk))
    else:
        form = Vendor_Edit_Form(instance=vendor)

    data_lists = ''
    crumb = breadcrumb(my_url)
    return render(request, 'epic/vendor_edit.html',
                  {
                      'form': form,
                      'pk': pk,
                      'breadcrumb': crumb,
                      'data_lists': data_lists
                  })

@permission_required(perms.EDIT)
def vendor_add(request):
    return vendor_edit(request, None)

@permission_required(perms.EDIT)
def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    my_url = reverse('epic:vendor_delete', kwargs={'pk': pk})
    parent_url = get_parent_url(my_url)

    # Check if the vendor is being referenced:
    #	1) In any Order
    #	2) In any Vendor_Part
    # If so, refuse to delete, as that could throw everything off balance.
    orders  = Order.objects.filter(vendor_id=vendor.id).order_by('-id')
    vps = Vendor_Part.objects.filter(vendor_id=vendor.id).order_by('id')
    if orders.exists() or vps.exists():
        messages = [ 'Sorry, vendor %s cannot be deleted because ' \
                     % vendor.html_link() ]
        sep = ''
        if orders.exists():
            messages[0] += '%d order%s refer%s to it' \
                           % (len(orders), '' if len(orders) == 1 else 's',
                              's' if len(orders) == 1 else '')
            messages.append(here_are_all_or_some('order', '', 's',
                                                 [ order.html_link() \
                                                   for order in orders ]))
            sep  = ' and '
        if vps.exists():
            messages[0] += '%s%d vendor part%s refer%s to it' % \
                           (sep, len(vps), '' if len(vps) == 1 else 's',
                            's' if len(vps) == 1 else '')
            messages.append(here_are_all_or_some('part', '', 's',
                                                 [ vp.part.html_link() \
                                                   for vp in vps ]))
        messages[0] += '.'
        return render(request, 'epic/delete_error.html',
                      {
                          'breadcrumb': breadcrumb(my_url),
                          'parent_url': parent_url,
                          'messages': messages
                      })
    vendor.delete()
    return HttpResponseRedirect(get_parent_url(parent_url))

@permission_required(perms.VIEW)
def warehouse_stock(request, pk=None):
    context = {}

    title = 'Current Stock '
    if pk is None:
        warehouse = None
        title += 'for all warehouses together'
        my_url = reverse('epic:warehouse_stock_all')
    else:
        warehouse = get_object_or_404(Warehouse, pk=pk)
        title += 'at warehouse %s' % warehouse.name
        my_url = reverse('epic:warehouse_stock', kwargs={'pk': pk})

    if request.method == 'POST':
        return HttpResponseRedirect(my_url + '?as_of_date=%s' \
                                    % request.POST.get('as_of_date'))
    elif 'as_of_date' in request.GET:
        as_of_date = datetime.strptime(request.GET['as_of_date'],
                                       '%Y-%m-%d').date()
    else:
        as_of_date = date.today()

    title += ' as of %s' % defaultfilters.date(as_of_date, 'Y-m-d')

    stock, stock_total = get_stock_summary(warehouse, as_of_date=as_of_date)

    context['pk'] = pk
    context['breadcrumb'] = breadcrumb(my_url)
    context['title'] = title
    context['stock'] = stock
    context['stock_total'] = stock_total
    context['as_of_date'] = as_of_date
    return render(request, 'epic/warehouse_stock.html', context)

@permission_required(perms.VIEW)
def warehouse_stock_all(request, ):
    return warehouse_stock(request, pk=None)

@permission_required(perms.VIEW)
def warehouse_list(request):
    return Warehouse_List_View.as_view()(request)

@permission_required(perms.VIEW)
def warehouse_detail(request, pk):
    return Warehouse_Detail_View.as_view()(request, pk=pk)

@permission_required(perms.VIEW)
def warehouse_inventory(request, pk):
    # dummy to make breadcrumbs work...
    return warehouse_detail(request, pk)

@transaction.atomic
@permission_required(perms.EDIT)
def warehouse_edit(request, pk):
    def prev_url(pk):
        if pk is None:
            return reverse('epic:warehouse_list')
        return reverse('epic:warehouse_detail', kwargs={'pk': pk})

    if pk is None:
        warehouse = None
        my_url = reverse('epic:warehouse_add')
    else:
        warehouse = get_object_or_404(Warehouse, pk=pk)
        my_url = reverse('epic:warehouse_edit', kwargs={'pk': pk})

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(prev_url(pk))
        form = Warehouse_Edit_Form(request.POST, instance=warehouse)
        if form.is_valid():
            new_form = form.save()
            return HttpResponseRedirect(prev_url(new_form.pk))
    else:
        form = Warehouse_Edit_Form(instance=warehouse)

    crumb = breadcrumb(my_url)
    return render(request, 'epic/warehouse_edit.html', { 'form': form,
                                                         'pk': pk,
                                                         'breadcrumb': crumb })

@permission_required(perms.EDIT)
def warehouse_add(request):
    return warehouse_edit(request, None)

@permission_required(perms.EDIT)
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    my_url = reverse('epic:warehouse_delete', kwargs={'pk': pk})
    parent_url = get_parent_url(my_url)

    # Check if the warehouse is being referenced:
    #	1) In any Delta
    #	2) In any Transaction
    # If so, refuse to delete, as that could throw everything off balance.
    # Note: we don't check explicitly if there are any shipments where
    # Shipment.from_warehouse is set: if the shipment has no deltas, it's
    # ok to delete it (which will happen automatically) and if it does,
    # then it'd show up as a delta and line-item.
    txtns  = Transaction.objects.filter(delta__warehouse_id=warehouse.id)
    txtns |= Transaction.objects.filter(warehouse_id=warehouse.id)
    txtns  = txtns.distinct().order_by('-id')
    if txtns.exists():
        messages = [ 'Sorry, warehouse %s cannot be deleted because ' \
                     % warehouse.html_link()]
        sep = ''
        if txtns.exists():
            messages[0] += '%d transaction%s refer%s to it' \
                           %(len(txtns), '' if len(txtns) == 1 else 's',
                             's' if len(txtns) == 1 else '')
            messages.append(here_are_all_or_some('transaction', '', 's',
                                                 [ txtn.html_link() \
                                                   for txtn in txtns ]))
        messages[0] += '.'
        return render(request, 'epic/delete_error.html',
                      {
                          'breadcrumb': breadcrumb(my_url),
                          'parent_url': parent_url,
                          'messages': messages
                      })
    warehouse.delete()
    return HttpResponseRedirect(get_parent_url(parent_url))

@permission_required(perms.EDIT)
def warehouse_add_shipment(request, pk):
    return ship_edit(request, None, from_warehouse_id=pk)

@permission_required(perms.EDIT)
def warehouse_add_inventory(request, pk):
    return inventory_edit(request, None, warehouse=pk)

class Warehouse_Inv_Detail_View(generic.DetailView):
    model = Inventory
    template_name = 'epic/inventory_detail.html'

    def __init__(self, *args, **kwargs):
        super(Warehouse_Inv_Detail_View, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        pk = self.object.id
        warehouse_id = int(self.kwargs['warehouse'])

        if warehouse_id != self.object.warehouse_id:
            raise Http404

        inventory_items, total_value_change, has_relative_deltas \
            = get_inventory_summary(warehouse_id, self.object)

        context = super(Warehouse_Inv_Detail_View, self) \
            .get_context_data(**kwargs)
        context['pk'] = pk
        context['breadcrumb'] = breadcrumb(
            reverse('epic:warehouse_inventory_detail',
                    kwargs={'warehouse': warehouse_id, 'pk': pk}))
        context['warehouse'] = warehouse_id
        context['inventory_items'] = inventory_items
        context['total_value_change'] = total_value_change
        context['has_relative_deltas'] = has_relative_deltas
        return context

@permission_required(perms.VIEW)
def warehouse_inv_detail(request, warehouse, pk):
    return Warehouse_Inv_Detail_View.as_view()(request,
                                               warehouse=warehouse, pk=pk)

class Inventory_Edit_Form(ModelForm):
    def __init__(self, fixed, *args, **kwargs):
        super(Inventory_Edit_Form, self).__init__(*args, **kwargs)
        self.fixed = fixed
        self.helper = crispy_form_helper()
        self.has_assemblies = False
        self.fields['ts'].label = 'Created on'

    class Meta:
        model = Inventory
        fields = [ 'ts', 'notes' ]

class Inventory_Edit_Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super(Inventory_Edit_Form, self).__init__(*args, **kwargs)
        self.helper = crispy_form_helper()
        self.has_assemblies = False
        self.fields['ts'].label = 'Inventory Date'
        self.fields['ts'].input_formats = [ '%Y-%m-%d %I:%M %p']

    class Meta:
        model = Inventory
        fields = [ 'ts', 'notes' ]
        widgets = {
            'ts': DateTimePicker(
                options={'format': 'YYYY-MM-DD hh:mm a'}),
            'part': Part_Autocomplete.widget()
        }

@transaction.atomic
@permission_required(perms.EDIT)
def inventory_edit(request, pk, warehouse):
    def prev_url(pk):
        if pk is None:
            return reverse('epic:warehouse_list')
        return reverse('epic:warehouse_inventory_detail',
                       kwargs={'warehouse': warehouse, 'pk': pk})

    if pk is None:
        inventory = None
        my_url = reverse('epic:warehouse_add_inventory',
                          kwargs={'pk': warehouse})
    else:
        inventory = get_object_or_404(Inventory, pk=pk)
        if int(warehouse) != inventory.warehouse_id:
            raise Http404
        for d in Delta.objects.filter(txtn_id=pk):
            if not d.is_absolute:
                raise Http404
        my_url = reverse('epic:warehouse_inventory_edit',
                         kwargs={'warehouse': warehouse, 'pk': pk})

    Delta_Formset = inlineformset_factory(Transaction, Delta,
                                          form=Line_Item_Edit_Form,
                                          formset=Line_Item_Edit_Formset,
                                          fields=[ 'part', 'adj' ])
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(prev_url(pk))

        inv_form = Inventory_Edit_Form(request.POST, instance=inventory)
        item_form = Delta_Formset(request.POST, instance=inventory)

        if inv_form.is_valid() and item_form.is_valid():
            pk = item_form.save_with_transaction(request, Delta_Formset,
                                                 inv_form, item_form,
                                                 int(warehouse))
            if 'save-and-done' in request.POST:
                return HttpResponseRedirect(prev_url(pk))
            return HttpResponseRedirect(
                reverse('epic:warehouse_inventory_edit',
                        kwargs={'warehouse': warehouse, 'pk': pk}))
    else:
        inv_form = Inventory_Edit_Form(instance=inventory)
        if inventory is None:
            inv_form.fields['ts'].initial = timezone.now()
        item_form = Delta_Formset(instance=inventory)

    item_form.initialize_virtual_fields(None)

    return render(request, 'epic/inventory_edit.html',
                  {
                      'pk': pk,
                      'breadcrumb': breadcrumb(my_url),
                      'warehouse': warehouse,
                      'inv_form': inv_form,
                      'item_form': item_form
                  })

@permission_required(perms.EDIT)
def inventory_delete(request, pk, warehouse):
    inv = get_object_or_404(Inventory, pk=pk)
    if inv.warehouse_id != int(warehouse):
        raise Http404
    my_url = reverse('epic:warehouse_inventory_delete',
                     kwargs={'warehouse': warehouse, 'pk': pk})
    parent_url = get_parent_url(my_url)

    # Inventories are easy: nothing else refers to them so we can always delete
    # them.
    inv.delete()
    return HttpResponseRedirect(get_parent_url(get_parent_url(parent_url)))

class Order_List_View(generic.ListView):
    model = Order
    paginate_by = 50

    def get_status_filter(self):
        if self.request.method == 'GET' and('st' in self.request.GET):
            return self.request.GET['st']
        return 'open'

    def get_queryset(self):
        qs = Order.objects.order_by('-expected_arrival_date')
        st = self.get_status_filter()
        if st == 'open':
            qs = qs.filter(status=Order.STATUS_OPEN)
        elif st == 'closed':
            qs = qs.filter(status=Order.STATUS_CLOSED)
        return qs

    def get_context_data(self, **kwargs):
        st = self.get_status_filter()
        query_string = ''
        if st != 'open':
            query_string = 'st=%s' % st

        context = super(Order_List_View, self).get_context_data(**kwargs)
        context['breadcrumb'] = breadcrumb(reverse('epic:order_list'))
        context['list_pager'] = html_list_pager(context['page_obj'],
                                                queries=[ query_string ])
        context['st'] = st
        return context

class Order_Detail_View(generic.DetailView):
    model = Order
    fields = [ 'status', 'ts', 'expected_arrival_date' ]

    def get_context_data(self, **kwargs):
        def map_fields(name, value, verbose_name):
            if name == 'ts':
                # Python 3 includes microsecs; Python 2 does not:
                try:
                    ts = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f+00:00')
                except ValueError:
                    ts = datetime.strptime(value, '%Y-%m-%d %H:%M:%S+00:00')
                return 'Order Date', \
                    defaultfilters.date(ts.replace(tzinfo=timezone.utc),
                                        'Y-m-d')
            return verbose_name, value

        order = self.object

        shipments = []
        for s in Shipment.objects.filter(ordr_id=order.id):
            shipments.append(s.html_link())

        order_items = Line_Item.objects.filter(txtn_id=order.id)

        pk = order.id

        context = super(Order_Detail_View, self).get_context_data(**kwargs)
        context['breadcrumb'] = breadcrumb(reverse('epic:order_detail',
                                                   kwargs={'pk': pk}))
        context['fields'] = get_model_fields(order, self.fields, map_fields)
        context['page_nav'] = html_page_nav('epic:order_detail', Order, pk)
        context['order'] = order
        context['order_items'] = order_items
        context['shipments'] = html_list_or_none(shipments)
        return context

class Transaction_Edit_Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super(Transaction_Edit_Form, self).__init__(*args, **kwargs)
        self.helper = crispy_form_helper()

    class Meta:
        model = Transaction
        fields = [ 'notes' ]

class Order_Edit_Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super(Order_Edit_Form, self).__init__(*args, **kwargs)
        self.helper = crispy_form_helper()
        self.has_assemblies = False
        self.fields['ts'].label = 'Order Date'
        self.fields['warehouse'].label = 'Ship-To Warehouse'

    def clean(self):
        cleaned_data = super(Order_Edit_Form, self).clean()
        if self.has_assemblies:
            vendor = cleaned_data['vendor']
            try:
                warehouse = Warehouse.by_name(vendor.name)
            except ObjectDoesNotExist:
                raise forms.ValidationError(
                    {'vendor': ['Order contains assemblies but this '
                                'vendor has no warehouse of the same name.  '
                                'Please change vendor or create a warehouse '
                                'for this vendor.']})

    class Meta:
        model = Order
        fields = [ 'ts', 'vendor', 'warehouse', 'expected_arrival_date',
                   'notes' ]
        widgets = {
            'ts': DateTimePicker(options={'format': 'YYYY-MM-DD'}),
            'expected_arrival_date': DateTimePicker(options={'format':
                                                             'YYYY-MM-DD'})
        }


class PartChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.choice_label()


class Line_Item_Edit_Form(ModelForm):
    class Meta:
        model = Line_Item
        fields = '__all__'

    part = PartChoiceField(
        queryset=Part.objects.all(), widget=Part_Autocomplete.widget())


class Line_Item_Edit_Formset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(Line_Item_Edit_Formset, self).__init__(*args, **kwargs)
        self.helper = crispy_inline_form_helper()

    def add_fields(self, form, index):
        super(Line_Item_Edit_Formset, self).add_fields(form, index)
        ndict = OrderedDict()
        # first, copy all hidden fields:
        for f in form.fields:
            if form.fields[f].widget.is_hidden:
                ndict[f] = form.fields[f]
        # second, rearrange the order of the visible fields and add
        # virtual (calculated) fields:
        if 'qty' in form.fields:
            ndict['qty'] = form.fields['qty']
            ndict['qty'].widget.attrs['size'] = 6
            ndict['qty'].widget.attrs['placeholder'] = 'Quantity?'
            ndict['qty'].help_text = ''
        elif 'adj' in form.fields:
            ndict['adj'] = form.fields['adj']
            ndict['adj'].widget.attrs['size'] = 6
            ndict['adj'].widget.attrs['placeholder'] = 'Quantity?'
            ndict['adj'].label = 'Qty'
            ndict['adj'].help_text = ''
        ndict['part'] = form.fields['part']
        ndict['part'].widget.attrs['size'] = 9
        ndict['part'].help_text = ''
        if 'qty' in form.fields:
            ndict['vendor_pn'] = forms.CharField(label='Vendor\'s Part #')
            ndict['vendor_pn'].widget.attrs['readonly'] = 'True'
            ndict['vendor_pn'].widget \
                              .attrs['placeholder'] = 'Vendors\'s Part #?'
            ndict['part_cost'] = forms.CharField(label='Price')
            ndict['part_cost'].widget.attrs['size'] = 8
            ndict['part_cost'].widget.attrs['placeholder'] = 'Price?'
        if 'line_cost' in form.fields:
            ndict['line_cost'] = form.fields['line_cost']
            ndict['line_cost'].widget.attrs['size'] = 8
            ndict['line_cost'].widget \
                              .attrs['placeholder'] = 'Line-item cost?'
            ndict['line_cost'].help_text = ''
        ndict[DELETION_FIELD_NAME] = form.fields[DELETION_FIELD_NAME]

        form.fields = ndict

    def clean(self):
        super(Line_Item_Edit_Formset, self).clean()

        parts_listed = {}
        line = 0
        for form in self.forms:
            line += 1
            if 'part' not in form.cleaned_data or \
               'part_cost' not in form.cleaned_data or \
               'vendor_pn' not in form.cleaned_data:
                continue
            part = form.cleaned_data['part']
            if part is None:
                continue
            if part in parts_listed:
                # same part is listed multiple times
                errors = form._errors.setdefault('part', ErrorList())
                errors.append('Line %d already lists this part.' \
                              % parts_listed[part])
                continue
            else:
                parts_listed[part] = line
            if form.instance.pk is None:
                # When adding a new line-item, make sure it's part # doesn't
                # conflict with one that's already existing.  If it doesn,
                # add error messages that tell the user how to fix the problem.
                # Since this runs
                # after django.db.models._perform_unique_checks,
                # we can't fix the problem automatically.
                qs = form.instance.__class__.objects \
                                            .filter(txtn_id=self.instance.id) \
                                            .filter(part_id=part.id)
                if qs.exists():
                    existing_pk = qs[0].pk
                    for other_form in self.forms:
                        if other_form == form:
                            continue
                        if other_form.instance.pk == existing_pk:
                            other_form.instance._set_pk_val(None)
                            errors = other_form._errors.setdefault('part',
                                                                   ErrorList())
                            errors.append('Please use this for part %s.' \
                                          % part)
                            errors = form._errors.setdefault('part',
                                                             ErrorList())
                            errors.append('Please use this for part %s.' \
                                          % other_form.instance.part)
                            break
            part_cost = Decimal(form.cleaned_data['part_cost'])
            vendor_pn = form.cleaned_data['vendor_pn']
            delete = form.cleaned_data[DELETION_FIELD_NAME]
            txtn = self.instance
            if not delete and hasattr(txtn, 'order') \
               and txtn.order.vendor_id is not None:
                # Update Vendor_Part number if necessary:
                vp = Vendor_Part.get(part_id=part.id,
                                     vendor_id=txtn.order.vendor_id)
                if vp is None:
                    nvp = Vendor_Part(part_id=part.id,
                                      vendor_id=txtn.order.vendor_id,
                                      vendor_pn=vendor_pn,
                                      price=part_cost)
                    try:
                        nvp.full_clean()
                        nvp.save()
                    except ValidationError as e:
                        errors = form._errors.setdefault('vendor_pn',
                                                         ErrorList())
                        for msg in e.message_dict[NON_FIELD_ERRORS]:
                            errors.append(msg)
                elif part_cost != vp.price:
                    vp.price = part_cost
                    vp.save()

                # Update target_price of part if it's higher than part_cost:
                if part_cost < part.target_price:
                    part.target_price = part_cost
                    part.save()

    def initialize_virtual_fields(self, vendor_id):
        # setup initial data for calculated (virtual) fields:
        for form in self:
            init = form.initial
            if 'part' in init:
                if vendor_id is not None:
                    vp = Vendor_Part.get(part_id=init['part'],
                                         vendor_id=vendor_id)
                    if vp is not None:
                        init['vendor_pn'] = vp.vendor_pn
            if 'line_cost' in init and 'qty' in init:
                init['part_cost'] = part_cost(init['line_cost'], init['qty'])

    def save_with_transaction(self, request, formset_create,
                              txtn_form, item_form, warehouse_id=None):
        """Handle the common steps of saving the line-items and it's
        transaction.  txtn_form and item_form must have been validated
        before calling this function.

        """
        txtn = txtn_form.save(commit=False)
        if txtn.ts is None:
            txtn.ts = timezone.now()
        if txtn.warehouse_id is None:
            txtn.warehouse_id = warehouse_id
        txtn.save()

        new_item_form = formset_create(request.POST, instance=txtn)
        new_item_form.is_valid()	# re-create cleaned data for .save()

        new_line_items = new_item_form.save(commit=False)

        for item in new_item_form.deleted_objects:
            # With Django 1.7, formset.save (..., commit=False) does
            # not delete automatically.  We need to delete before saving
            # because otherwise we might end up with two entries of the
            # same part...
            item.delete()

        next_index = txtn.first_available_index()
        for item in new_line_items:
            if hasattr(item, 'index'):
                if item.index is None:
                    item.index = next_index
                    next_index += 1
            if hasattr(item, 'warehouse_id'):
                # initialize Delta fields that are not editable:
                item.warehouse_id = warehouse_id
                item.is_absolute = True
            item.save()
        txtn.finalize()
        return txtn.id

@permission_required(perms.VIEW)
def order_list(request):
    return Order_List_View.as_view()(request)

@permission_required(perms.VIEW)
def order_detail(request, pk):
    return Order_Detail_View.as_view()(request, pk=pk)

@transaction.atomic
@permission_required(perms.EDIT)
def order_edit(request, pk, order_initial=None, items_initial=None):
    def prev_url(pk):
        if pk is None:
            return reverse('epic:order_list')
        return reverse('epic:order_detail', kwargs={'pk': pk})

    if pk is None:
        order = None
        my_url = reverse('epic:order_add')
    else:
        order = get_object_or_404(Order, pk=pk)
        my_url = reverse('epic:order_edit', kwargs={'pk': pk})

    # See http://bit.ly/1wfFNKa:
    if order_initial is None:
        order_initial = {}
    if items_initial is None:
        items_initial = []

    num_extra = len(items_initial) + 3
    Line_Item_Formset = inlineformset_factory(Order, Line_Item,
                                              form=Line_Item_Edit_Form,
                                              formset=Line_Item_Edit_Formset,
                                              fields=[ 'part', 'qty',
                                                       'line_cost' ],
                                              extra=num_extra)

    if request.method == 'POST' and 'preset' not in request.POST:
        if 'cancel' in request.POST:
            return HttpResponseRedirect(prev_url(pk))

        order_form = Order_Edit_Form(request.POST, instance=order)
        item_form = Line_Item_Formset(request.POST, instance=order)

        #
        # First, do a partial validation of the order items so we can check
        # if any assemblies are being ordered.
        #
        if item_form.is_valid():
            for form in item_form.forms:
                if not 'part' in form.cleaned_data:
                    continue
                if form.cleaned_data['part'].assembly_items().exists():
                    order_form.has_assemblies = True
                    break

            if order_form.is_valid():
                pk = item_form.save_with_transaction(request,
                                                     Line_Item_Formset,
                                                     order_form, item_form)
                if 'save-and-done' in request.POST:
                    return HttpResponseRedirect(prev_url(pk))
                return HttpResponseRedirect(reverse('epic:order_edit',
                                                    kwargs={'pk': pk}))
    else:
        if order is None and len(order_initial) == 0:
            order_initial['ts'] = datetime.today()
        order_form = Order_Edit_Form(instance=order, initial=order_initial)
        item_form = Line_Item_Formset(instance=order, initial=items_initial)

    item_form.initialize_virtual_fields(order_form.initial.get('vendor'));

    crumb = breadcrumb(my_url)
    return render(request, 'epic/order_edit.html',
                  {
                      'order_form': order_form,
                      'item_form': item_form,
                      'pk': pk,
                      'breadcrumb': crumb,
                  })

@permission_required(perms.EDIT)
def order_add(request):
    order_initial = {}
    items_initial = []
    if request.method == 'POST' and 'preset' in request.POST:
        order_initial, \
            items_initial = get_initial_from_post(request, 'item_set',
                                                  Order, Line_Item)
    return order_edit(request, None, order_initial, items_initial)

@permission_required(perms.EDIT)
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    my_url = reverse('epic:order_delete', kwargs={'pk': pk})
    parent_url = get_parent_url(my_url)

    # Check if the order is being referenced:
    #	1) In any Shipment
    # If so, refuse to delete, as that could throw everything off balance.
    ships  = Shipment.objects.filter(ordr_id=order.id).order_by('-id')
    if ships.exists():
        messages = [ 'Sorry, order %s cannot be deleted because '
                     '%d shipment%s refer%s to it.'
                     % (order.html_link(),
                        len(ships), '' if len(ships) == 1 else 's',
                        's' if len(ships) == 1 else '') ]
        messages.append(here_are_all_or_some('shipment', '', 's',
                                             [ ship.transaction_ptr.html_link()
                                               for ship in ships ]))
        return render(request, 'epic/delete_error.html',
                      {
                          'breadcrumb': breadcrumb(my_url),
                          'parent_url': parent_url,
                          'messages': messages
                      })
    order.delete()
    return HttpResponseRedirect(get_parent_url(parent_url))

class Makeup_Order_Item:
    def __init__(self, src, part, qty):
        self.part = part
        self.amount = None
        if isinstance(src, Vendor):
            self.vendor_part = Vendor_Part.get(part.id, src.id)
        else:
            self.vendor_part = None
        self.set_qty(qty)

    def set_qty(self, qty):
        self.qty = qty
        if self.vendor_part:
            self.amount = self.qty * self.vendor_part.price

    def __repr__(self):
        rest = ''
        if self.vendor_part:
            rest =(',vendor_part=%s,amount=%s' % (repr(self.vendor_part),
                                                  self.amount))
        return 'Makeup_Order_Item(part=%s,qty=%s%s)' % (self.part,
                                                        self.qty, rest)

class Makeup_Order:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self.items = []

    def add_part(self, part, qty):
        self.items.append(Makeup_Order_Item(self.src, part, qty))

    def finalize(self):
        for item in self.items:
            if isinstance(self.src, Vendor):
                spq = item.part.spq
                if spq > 1:
                    item.set_qty(int(math.ceil(float(item.qty) / spq)) * spq)
        self.items.sort(key=operator.attrgetter('part.id'))

    def __repr__(self):
        return 'Makeup_Order(%s->%s): %s' % \
           (self.src.name, self.dst.name, repr(self.items))

def add_to_makeup_orders(orders, for_warehouse, part, qty_short, inv):
    # first, see if we can ship parts from another warehouse:
    for w in inv.warehouse:
        if w == for_warehouse.id:
            continue
        for p in part.equivalent_parts():
            have = inv.get_qty(w, p.id)
            # only arrange for inter-warehouse shipment for this part if the
            # other warehouse has enough parts to satisfy the shortage or
            # it has at least standard-package-quantity pieces:
            if have >= qty_short or have >= part.spq:
                if have >= qty_short:
                    take = qty_short
                else:
                    take = have
                warehouse = get_object_or_404(Warehouse, pk=w)
                if warehouse not in orders:
                    orders[warehouse] = Makeup_Order(warehouse, for_warehouse)
                orders[warehouse].add_part(p, qty=take)
                qty_short -= take
                inv.adj_qty(w, p.id, -take)

    # second, order the parts from a vendor
    if qty_short > 0:
        vendor = part.best_vendor()
        if not vendor:
            return
        if vendor not in orders:
            orders[vendor] = Makeup_Order(vendor, for_warehouse)
        orders[vendor].add_part(part, qty_short)

@permission_required(perms.VIEW)
def order_check_stock(request, pk):
    def shortage_key(x):
        qty = x['warehouses'][0]['qty_remaining']
        if qty < 0:
            return qty
        return x['part'].id

    crumb = breadcrumb(reverse('epic:order_check_stock', kwargs={'pk': pk}))
    order = get_object_or_404(Order, pk=pk)
    if order.status != Order.STATUS_OPEN or \
       not order.assembly_line_items().exists():
        raise Http404	# order not open or has no line-items for assemblies
    open_orders = get_open_order_summary(last_order=order)

    inv = get_stock()

    my_summary_items = []
    for summary in open_orders:
        if summary['order'].id == order.id:
            my_summary_items = summary['items']
        for item in summary['items']:
            inv.apply_order_line_item(item)

    comp_status = []
    order_warehouse = Warehouse.by_name(order.vendor.name)
    max_lead_time = 0
    warehouses = [ order_warehouse.id ]
    max_assy = None
    for line_item in my_summary_items:
        assy_lead_time = line_item.part.lead_time
        if max_assy is None:
            max_assy = line_item.part
        for assy_item in line_item.part.assembly_items():
            if assy_lead_time + assy_item.comp.lead_time > max_lead_time:
                max_lead_time = assy_lead_time + assy_item.comp.lead_time
                max_assy = line_item.part
                max_comp = assy_item.comp
            part = assy_item.comp.best_part()
            if any(sts['part'] == part for sts in comp_status):
                continue	# we already checked this part
            comp_status.append({
                'part': part,
                'warehouses': [ ]
            })
            for w in inv.warehouse:
                for p in part.equivalent_parts():
                    if inv.get_qty(w, p.id) != 0:
                        try:
                            warehouses.index(w)
                        except:
                            warehouses.append(w)

    min_assy_arrival_date = date.today() + timedelta(days=7 * max_lead_time)

    needed_by = (order.expected_arrival_date
                 - timedelta(days=7 * max_assy.lead_time))
    tomorrow = date.today() + timedelta(days = 1)
    if needed_by < tomorrow:
        needed_by = tomorrow
    available_time = order.expected_arrival_date - date.today()
    available_time = math.ceil(available_time.days / 7)

    shortages = {}
    makeup_orders = {}
    for sts in comp_status:
        part = sts['part']
        for w in warehouses:
            total_qty = 0
            qty_breakdown = []
            for p in part.equivalent_parts():
                qty = inv.get_qty(w, p.id)
                total_qty += qty
                if qty != 0:
                    qty_breakdown.append({ 'part': p, 'qty' : qty })
            if total_qty < 0 and w == order_warehouse.id:
                shortages[part.id] = -total_qty
            warehouse_sts = { 'qty_remaining': total_qty }
            if len(qty_breakdown) > 1:
                warehouse_sts['qty_breakdown'] = qty_breakdown

            sts['warehouses'].append(warehouse_sts)
        if part.id in shortages:
            add_to_makeup_orders(makeup_orders, order_warehouse,
                                 part, shortages[part.id], inv)
    makeup_order_list = []
    for warehouse, makeup_order in makeup_orders.items():
        makeup_order.finalize()
        makeup_order_list.append(makeup_order)
    # list inter-warehouse shipments first:
    makeup_order_list.sort(key=lambda x: isinstance(x.src, Vendor))

    warehouse_names = []
    for w in warehouses:
        warehouse_names.append(get_object_or_404(Warehouse, pk=w).name)
    comp_status.sort(key=shortage_key)

    return render(request, 'epic/order_check_stock.html',
                  {
                      'breadcrumb': crumb,
                      'order': order,
                      'shortage_count': len(shortages),
                      'open_orders': open_orders,
                      'comp_status': comp_status,
                      'warehouse_names': warehouse_names,
                      'makeup_order_list': makeup_order_list,
                      'needed_by': needed_by,
                      'max_lead_time': max_lead_time,
                      'available_time': available_time,
                      'min_assy_arrival_date': min_assy_arrival_date,
                      'max_comp': max_comp,
                      'max_assy': max_assy
                  })

@permission_required(perms.EDIT)
def order_add_shipment(request, pk):
    return ship_edit(request, None, order_id=pk)

class Ship_List_View(generic.ListView):
    model = Shipment
    paginate_by = 50

    def get_queryset(self):
        return super(Ship_List_View, self).get_queryset().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(Ship_List_View, self).get_context_data(**kwargs)
        context['breadcrumb'] = breadcrumb(reverse('epic:ship_list'))
        context['list_pager'] = html_list_pager(context['page_obj'])
        return context

class Ship_Detail_View(generic.DetailView):
    model = Shipment

    def get_context_data(self, **kwargs):
        ship = self.object
        pk = ship.id
        line_items = Line_Item.objects.filter(txtn_id=pk)

        context = super(Ship_Detail_View, self).get_context_data(**kwargs)
        context['breadcrumb'] = breadcrumb(reverse('epic:ship_detail',
                                                   kwargs={'pk': pk}))
        context['page_nav'] = html_page_nav('epic:ship_detail', Shipment, pk)
        context['shipment'] = ship
        context['line_items'] = line_items
        return context

class OrderChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.choice_label()

class Ship_Edit_Form(ModelForm):
    ordr = OrderChoiceField(
        required=False, queryset=Order.objects.all(),
        widget=Order_Autocomplete.widget()
    )

    def __init__(self, fixed, *args, **kwargs):
        super(Ship_Edit_Form, self).__init__(*args, **kwargs)
        self.fixed = fixed
        self.helper = crispy_form_helper()
        self.has_assemblies = False
        self.fields['ts'].label = 'Ship Date'
        self.fields['from_warehouse'].label = 'Ship-From Warehouse'
        self.fields['warehouse'].label = 'Ship-To Warehouse'

        if self.fixed:
            if 'order' in fixed:
                self.fields['ordr'].widget.attrs['readonly'] = 'True'
            else:
                del self.fields['ordr']
            if 'from_warehouse' in fixed:
                self.fields['from_warehouse'].widget.attrs['readonly'] = 'True'
            else:
                del self.fields['from_warehouse']

    def clean(self):
        cleaned_data = super(Ship_Edit_Form, self).clean()

        if 'order' in self.fixed:
            cleaned_data['ordr'] = get_object_or_404(Order,
                                                     pk=self.fixed['order'])
        if 'from_warehouse' in self.fixed:
            cleaned_data['from_warehouse'] \
                = get_object_or_404(Warehouse, pk=self.fixed['from_warehouse'])

        dst_warehouse = cleaned_data.get('warehouse')

        order = cleaned_data.get('ordr')
        from_warehouse = cleaned_data.get('from_warehouse')

        if from_warehouse is not None:
            if order is not None:
                raise forms.ValidationError(
                    { 'ordr': ['Order # and Ship-From Warehouse '
                               'cannot both be non-empty.' ] })
            if from_warehouse == dst_warehouse:
                raise forms.ValidationError(
                    { 'warehouse': ['Must be different from '
                                    'Ship-From Warehouse.' ] })
        else:
            if order is None:
                raise forms.ValidationError(
                    { 'ordr': ['One of Order # or Ship-From Warehouse '
                               'must be specified.' ] })

    class Meta:
        model = Shipment
        fields = [ 'ts', 'ordr', 'from_warehouse', 'warehouse',
                   'tracking', 'cost_freight', 'cost_other', 'cost_discount',
                   'notes' ]
        widgets = {
            'ts': DateTimePicker(options={'format': 'YYYY-MM-DD'})
        }

@permission_required(perms.VIEW)
def ship_list(request):
    return Ship_List_View.as_view()(request)

@permission_required(perms.VIEW)
def ship_detail(request, pk):
    return Ship_Detail_View.as_view()(request, pk=pk)

@transaction.atomic
@permission_required(perms.EDIT)
def ship_edit(request, pk, order_id=None, from_warehouse_id=None,
              ship_initial=None, items_initial=None):
    def prev_url(pk):
        if pk is None:
            if 'order' in fixed:
                return reverse('epic:order_detail',
                               kwargs={'pk': fixed['order']})
            elif 'from_warehouse' in fixed:
                return reverse('epic:warehouse_detail',
                               kwargs={'pk': fixed['from_warehouse']})
            else:
                return reverse('epic:ship_list')
        return reverse('epic:ship_detail', kwargs={'pk': pk})

    # See http://bit.ly/1wfFNKa:
    if ship_initial is None:
        ship_initial = {}
    if items_initial is None:
        items_initial = []

    if order_id is not None:
        fixed = { 'order': order_id }
    elif from_warehouse_id is not None:
        fixed = { 'from_warehouse': from_warehouse_id }
    else:
        fixed = {}

    order = None
    if pk is None:
        ship = None
        warehouse = None
        if order_id is not None:
            my_url = reverse('epic:order_add_shipment',
                             kwargs={'pk': order_id})
        elif from_warehouse_id is not None:
            my_url = reverse('epic:warehouse_add_shipment',
                             kwargs={'pk': from_warehouse_id })
        else:
            my_url = reverse('epic:ship_add')

        if 'order' in fixed:
            order = get_object_or_404(Order, pk=fixed['order'])
            if len(items_initial) == 0:
                # pre-populated with order-items that remain to be shipped:
                for item in Line_Item.objects.filter(txtn_id=fixed['order']) \
                                             .order_by('index'):
                    qty = item.qty_remaining_to_ship()
                    if qty > 0:
                        part_cost = item.line_cost / item.qty
                        lc = Decimal('%.2f' % (qty * part_cost))
                        items_initial.append({ 'qty': qty,
                                               'part': item.part.id,
                                               'line_cost': lc })
        elif 'from_warehouse' in fixed:
            warehouse = int(fixed['from_warehouse'])
            if len(items_initial) == 0:
                # pre-populate with in-stock items of the warehouse:
                inv = get_stock()
                for p in inv.warehouse.get(warehouse, []):
                    qty = inv.warehouse[warehouse][p].qty
                    if qty > 0:
                        items_initial.append({ 'qty': qty, 'part': p })
    else:
        ship = get_object_or_404(Shipment, pk=pk)
        order = ship.ordr		# may be None
        warehouse = ship.from_warehouse	# may be None
        my_url = reverse('epic:ship_edit', kwargs={'pk': pk})

    num_extra = len(items_initial) + 3

    Line_Item_Formset = inlineformset_factory(Shipment, Line_Item,
                                              form=Line_Item_Edit_Form,
                                              formset=Line_Item_Edit_Formset,
                                              fields=[ 'part', 'qty',
                                                       'line_cost'],
                                              extra=num_extra)

    if request.method == 'POST' and 'preset' not in request.POST:
        if 'cancel' in request.POST:
            return HttpResponseRedirect(prev_url(pk))

        ship_form = Ship_Edit_Form(fixed, request.POST, instance=ship)
        item_form = Line_Item_Formset(request.POST, instance=ship)

        if ship_form.is_valid() and item_form.is_valid():
            pk = item_form.save_with_transaction(request, Line_Item_Formset,
                                                 ship_form, item_form)
            if 'save-and-done' in request.POST:
                return HttpResponseRedirect(prev_url(pk))
            return HttpResponseRedirect(reverse('epic:ship_edit',
                                                kwargs={'pk': pk}))
    else:
        if ship is None and len(ship_initial) == 0:
            ship_initial['ts'] = datetime.today()
            if order is not None:
                ship_initial['ordr'] = order.id
                ship_initial['warehouse'] = order.warehouse_id
            if warehouse is not None:
                ship_initial['from_warehouse'] = warehouse
        ship_form = Ship_Edit_Form(fixed, instance=ship, initial=ship_initial)
        item_form = Line_Item_Formset(instance=ship, initial=items_initial)

    vendor_id = None if order is None else order.vendor.id
    item_form.initialize_virtual_fields(vendor_id)

    crumb = breadcrumb(my_url)
    return render(request, 'epic/shipment_edit.html',
                  {
                      'breadcrumb': crumb,
                      'pk': pk,
                      'ship_form': ship_form,
                      'item_form': item_form,
                  })

@permission_required(perms.VIEW)
def ship_add(request):
    from_warehouse_id = None
    ship_initial = {}
    items_initial = []
    if request.method == 'POST' and 'preset' in request.POST:
        ship_initial, items_initial = get_initial_from_post(request,
                                                            'item_set',
                                                            Shipment,
                                                            Line_Item)
        from_warehouse_id = ship_initial.get('from_warehouse')
    return ship_edit(request, None, from_warehouse_id=from_warehouse_id,
                     ship_initial=ship_initial, items_initial=items_initial)

@permission_required(perms.EDIT)
def ship_delete(request, pk):
    ship = get_object_or_404(Shipment, pk=pk)
    my_url = reverse('epic:ship_delete', kwargs={'pk': pk})
    parent_url = get_parent_url(my_url)

    # Shipments are easy: nothing else refers to them so we can always delete
    # them.
    ship.delete()
    return HttpResponseRedirect(get_parent_url(parent_url))

@permission_required(perms.VIEW)
def search_results(request):
    def find_parts(q):
        # EP<number> or <number> results in direct part id lookup:
        m = re.match(r'(?:EP)?(\d+)$', q, re.I)
        if m:
            qs = Part.objects.filter(id=int(m.group(1)))
            if qs.exists():
                return qs
        qs  = Part.objects.filter(mfg_pn__icontains=q)
        qs |= Part.objects.filter(mfg__icontains=q)
        qs |= Part.objects.filter(descr__icontains=q)
        qs |= Part.objects.filter(vendor_part__vendor__name__icontains=q)
        qs |= Part.objects.filter(vendor_part__vendor_pn__icontains=q)
        qs |= Part.objects.filter(val__icontains=q)
        return qs.distinct().order_by('id')

    def find_txtns(q):
        m = re.match(r'(\d+)$', q, re.I)
        qs = Transaction.objects.none()
        if m:
            qs = Transaction.objects.filter(pk=int(m.group(1)))
            if len(qs) == 1:
                return qs
            for txtn in Transaction.objects.all():
                if re.match('\d*%s\d*' % q, str(txtn.id)):
                    qs |= Transaction.objects.filter(pk=txtn.pk)
            if len(qs) > 0:
                return qs
        qs |= Transaction.objects.filter(warehouse__name__icontains=q)
        qs |= Transaction.objects.filter(notes__icontains=q)
        qs |= Transaction.objects.filter(order__vendor__name__icontains=q)
        qs |= Transaction.objects.filter(shipment__tracking__icontains=q)
        return qs.distinct().order_by('-ts')

    parts = Part.objects.none()
    txtns = Transaction.objects.none()
    queries = [ ]
    if request.method == 'GET' and ('q' in request.GET):
        q = request.GET['q'].strip()
        queries.append('q=' + q)
        if q != '':
            parts = find_parts(q)
            txtns = find_txtns(q)

    if len(parts) == 1 and len(txtns) == 0:
        return HttpResponseRedirect(reverse('epic:part_detail',
                                            kwargs={'pk': parts[0].pk}))
    if len(txtns) == 1 and len(parts) == 0:
        txtn = txtns[0]
        if hasattr(txtn, 'order'):
            url = reverse('epic:order_detail', kwargs={'pk': txtn.pk})
        elif hasattr(txtn, 'shipment'):
            url = reverse('epic:ship_detail', kwargs={'pk': txtn.pk})
        elif hasattr(txtn, 'inventory'):
            url = reverse('epic:warehouse_inventory_detail',
                           kwargs={'warehouse': txtn.warehouse.id,
                                   'pk': txtn.pk})
        return HttpResponseRedirect(url)

    paginator = Paginator(parts, 10)
    ppg = request.GET.get('ppg')
    try:
        parts = paginator.page(ppg)
    except PageNotAnInteger:
        parts = paginator.page(1)
    except EmptyPage:
        parts = paginator.page(paginator.num_pages)

    paginator = Paginator(txtns, 10)
    tpg = request.GET.get('tpg')
    try:
        txtns = paginator.page(tpg)
    except PageNotAnInteger:
        txtns = paginator.page(1)
    except EmptyPage:
        txtns = paginator.page(paginator.num_pages)

    my_url = reverse('epic:search_results')
    crumb = breadcrumb(my_url)
    return render(request, 'epic/search_results.html',
                  {
                      'q':		q,
                      'breadcrumb':	breadcrumb,
                      'parts':		parts,
                      'parts_pager':	html_list_pager(parts,
                                                        queries=queries,
                                                        key='ppg'),
                      'txtns':		txtns,
                      'txtns_pager':	html_list_pager(txtns,
                                                        queries=queries,
                                                        key='tpg')
                  })

@permission_required(perms.VIEW)
def epic_index(request):
    open_order_summaries = get_open_order_summary()
    inv = get_stock()
    orders_with_shortages = []
    for summary in open_order_summaries:
        # update current stock:
        for line_item in summary['items']:
            inv.apply_order_line_item(line_item)

        try:
            warehouse = Warehouse.by_name(summary['order'].vendor)
        except:
            continue

        w = warehouse.id

        has_shortages = 0
        for line_item in summary['items']:
            for assy_item in line_item.part.assembly_items():
                part = assy_item.comp.best_part()
                qty = 0
                for p in part.equivalent_parts():
                    qty += inv.get_qty(w, p.id)
                if qty < 0:
                    orders_with_shortages.append(
                        summary['order'].transaction_ptr)
                    has_shortages = True
                    break
            if has_shortages:
                break

    orders_with_shortages.sort(key=operator.attrgetter('ts'), reverse=True)

    now = timezone.now()
    ts_limit = now - timedelta(days=30)

    activity = []

    recent = Transaction.objects.filter(ts__gte=ts_limit) \
                                .order_by('-ts')[:20]
    for txtn in recent:
        try:
            orders_with_shortages.index(txtn)
        except:
            activity.append(txtn)

    past_due = Order.objects \
                    .filter(status=Order.STATUS_OPEN) \
                    .filter(expected_arrival_date__lte=now) \
                    .order_by('-ts')
    for txtn in past_due:
        try:
            activity.index(txtn)
        except:
            activity.append(txtn)

    breadcrumb = '<ol class="breadcrumb">' \
                 '%s: %s</ol>' % (EPIC_App_Config.name.upper(),
                                  EPIC_App_Config.verbose_name)
    return render(request, 'epic/epic_index.html',
                  {
                      'breadcrumb': breadcrumb,
                      'orders_with_shortages': orders_with_shortages,
                      'activity': activity
                  })

class Datasheet_List_View(generic.ListView):
    model = Datasheet
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(Datasheet_List_View, self).get_context_data(**kwargs)

        context['breadcrumb'] = breadcrumb(reverse('epic:datasheet_list'))
        context['list_pager'] = html_list_pager(context['page_obj'])
        return context

class Datasheet_Detail_View(generic.DetailView):
    model = Datasheet
    fields = [ 'name', 'ds_file', 'notes' ]

    def get_context_data(self, **kwargs):
        context = super(Datasheet_Detail_View, self).get_context_data(**kwargs)
        context['breadcrumb'] = breadcrumb(
            reverse('epic:datasheet_detail', kwargs={'pk': self.object.pk}))
        context['page_nav'] = html_page_nav('epic:datasheet_detail', Datasheet,
                                            self.object.pk)
        context['fields'] = get_model_fields(self.object, self.fields)
        context['parts'] = ', '.join([p.html_link() for p in
                                      self.object.part_set.all()])
        return context

@permission_required(perms.VIEW)
def datasheet_detail(request, pk):
    return Datasheet_Detail_View.as_view()(request, pk=pk)

class Datasheet_Edit_Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super(Datasheet_Edit_Form, self).__init__(*args, **kwargs)
        self.helper = crispy_form_helper()

    def clean_ds_file(self):
        md5 = hashlib.md5()
        ds_file = self.cleaned_data.get('ds_file')
        try:
            # These exist only for freshly uploaded (not previously existing)
            # values of ds_file:
            content_type = ds_file.content_type
            size = ds_file._size
        except AttributeError:
            content_type = None
            size = 0
        if content_type is not None and content_type != 'application/pdf':
            raise ValidationError('File `%(name)s\' is not a PDF file',
                                  params={'name': ds_file.name},
                                  code='invalid')
        limit = getattr(settings, 'EPIC_DATASHEET_MAX_SIZE', 20*1024*1024)
        if size > limit:
            raise ValidationError('File size of %(size).1f MiB exceeds '
                                  'limit of %(limit).1f MiB',
                                  params={'size': ds_file._size / MiB,
                                          'limit': limit / MiB})
        for chunk in ds_file.chunks():
            md5.update(chunk)
        md5sum = md5.hexdigest()
        existing_ds = Datasheet.objects.filter(md5sum=md5sum)
        if existing_ds and existing_ds[0] != self.instance:
            raise ValidationError('Datasheet `%(ds)s\' already has the same '
                                  'contents as file `%(name)s\'.',
                                  params={'name': ds_file.name,
                                          'ds': existing_ds[0].name},
                                  code='invalid')
        return ds_file

    class Meta:
        model = Datasheet
        fields = [ 'name', 'ds_file', 'notes' ]

@permission_required(perms.VIEW)
def datasheet_list(request):
    return Datasheet_List_View.as_view()(request)


class Part_Datasheet_Edit_Formset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(Part_Datasheet_Edit_Formset, self).__init__(*args, **kwargs)
        self.helper = crispy_inline_form_helper()

    def add_fields(self, form, index):
        super(Part_Datasheet_Edit_Formset, self).add_fields(form, index)

        ndict = OrderedDict()
        # first, copy all hidden fields:
        for f in form.fields:
            if form.fields[f].widget.is_hidden:
                ndict[f] = form.fields[f]
        # second, load our autocomplete field for Part selection
        ndict['id'] = PartChoiceField(
            queryset=Part.objects.all(),
            widget=Part_Autocomplete.widget(),
            label='Part #')
        # render delete last
        if DELETION_FIELD_NAME in form.fields:
            ndict[DELETION_FIELD_NAME] = form.fields[DELETION_FIELD_NAME]

        form.fields = ndict

    def clean(self):
        super(Part_Datasheet_Edit_Formset, self).clean()

        for form in self:
            if 'id' in form.cleaned_data:
                part = form.cleaned_data['id']
                if part and part.datasheet:
                    if part.datasheet != self.instance:
                        errors = form._errors.setdefault('id', ErrorList())
                        errors.append('This part is already associated with '
                                      'datasheet %s.' % part.datasheet)

    def save(self):
        """This formset is not for creating/deleting, only changing FKs."""
        for form in self:
            part = form.cleaned_data.get('id')
            if not part:
                continue
            if form.cleaned_data.get(DELETION_FIELD_NAME):
                part.datasheet = None
            else:
                part.datasheet = self.instance
            part.save()


@permission_required(perms.EDIT)
def datasheet_edit(request, pk, parts_list=None):
    def prev_url(pk):
        if pk is None:
            return reverse('epic:datasheet_list')
        return reverse('epic:datasheet_detail', kwargs={'pk': pk})

    if pk is None:
        datasheet = None
        my_url = reverse('epic:datasheet_add')
        Part_Inline_Form_Set = inlineformset_factory(
            Datasheet, Part,
            fields=('id',),
            formset=Part_Datasheet_Edit_Formset, extra=3, can_delete=False)
    else:
        datasheet = get_object_or_404(Datasheet, pk=pk)
        my_url = reverse('epic:datasheet_edit', kwargs={'pk': pk})
        Part_Inline_Form_Set = inlineformset_factory(
            Datasheet, Part,
            fields=('id',),
            formset=Part_Datasheet_Edit_Formset,
            extra=3, can_delete=True)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(prev_url(pk))

        datasheet_form = Datasheet_Edit_Form(request.POST, request.FILES,
                                             instance=datasheet)
        part_formset = Part_Inline_Form_Set(request.POST, instance=datasheet)
        if datasheet_form.is_valid() and part_formset.is_valid():
            datasheet = datasheet_form.save()
            # Datasheet may be new
            part_formset = Part_Inline_Form_Set(request.POST,
                                                instance=datasheet)
            part_formset.is_valid()
            part_formset.save()
            return HttpResponseRedirect(prev_url(datasheet.pk))
    else:
        datasheet_form = Datasheet_Edit_Form(instance=datasheet)
        initial = []
        if parts_list:
            for p in parts_list:
                initial.append ({'id': p})
        part_formset = Part_Inline_Form_Set(instance=datasheet,
                                            initial=initial)

    return render(request, 'epic/datasheet_edit.html',
                  {
                      'pk': pk,
                      'datasheet_form': datasheet_form,
                      'breadcrumb': breadcrumb(my_url),
                      'part_formset': part_formset,
                  })

@permission_required(perms.EDIT)
def datasheet_add(request):
    return datasheet_edit(request, None)

@permission_required(perms.EDIT)
def datasheet_add_part(request, pk):
    return datasheet_edit(request, None, parts_list=[pk])

@permission_required(perms.EDIT)
def datasheet_delete(request, pk):
    datasheet = get_object_or_404(Datasheet, pk=pk)
    my_url = reverse('epic:datasheet_delete', kwargs={'pk': pk})
    parent_url = get_parent_url(my_url)

    # Check if the datasheet is being referenced:
    #  1) By any Part
    # If so, refuse to delete, as that could throw everything off balance.
    parts  = Part.objects.filter(datasheet_id=datasheet.id).order_by('-id')
    if parts.exists():
        messages = [ 'Sorry, datasheet %s cannot be deleted because '
                     '%d part%s refer%s to it.'
                     % (datasheet.html_link(),
                        len(parts), '' if len(parts) == 1 else 's',
                        's' if len(parts) == 1 else '') ]
        messages.append(here_are_all_or_some(
            'part', '', 's',
            [p.html_link() for p in datasheet.part_set.all()]))
        return render(request, 'epic/delete_error.html',
                      {
                          'breadcrumb': breadcrumb(my_url),
                          'parent_url': parent_url,
                          'messages': messages
                      })
    datasheet.delete()
    return HttpResponseRedirect(get_parent_url(parent_url))
