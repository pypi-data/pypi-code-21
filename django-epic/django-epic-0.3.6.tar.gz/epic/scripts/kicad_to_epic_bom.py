#!/usr/bin/env python
#
#   Copyright (c) 2014-2017 eGauge Systems LLC
#	4730 Walnut St, Suite 110
#	Boulder, CO 80301
#	voice: 720-545-9767
#	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
'''This is a KiCad Eeschema plugin that uses EPIC parts information to:

	1) generate a BOM as a text file
	2) create an EPIC assembly ("PCB") consisting of the BOM components

The EPIC assembly created by this tool will have it's manufacturer set
to django.conf.EPIC_MANUFACTURER and the manufacturer's part-number
will be set to 'bom:' with the name of the schematic appended.  If an
assembly with that part-number already exists, it will be update
UNLESS the BOM was edited manually inside EPIC.  In the latter case,
you can force overwriting the manually edited BOM pass passing this
script the --force-overwrite command-line option.

'''

from __future__ import print_function

import argparse
import io
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

# Please replace 'epic-sample' with the name of your Django project:
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'epic-sample.epic-sample.settings')

import django
django.setup()

from django.conf import settings as cfg
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from epic.models import Part, format_part_number, Assembly_Item, strchoice, \
    Vendor

from os import path

MY_TOOL_NAME = 'kicad-to-epic-bom'

manufacturer = cfg.EPIC_MANUFACTURER

class Component:
    def __init__(self, part_id=None, refdes=None, value=None, footprint=None,
                 mfg=None, mfg_pn=None):
        self.part_id = part_id
        self.part = None
        self.refdes = refdes
        self.value = value
        self.footprint = footprint
        self.mfg = mfg
        self.mfg_pn = mfg_pn

    def __str__(self):
        res = 'Component('
        sep = ''
        for f in dir(self):
            if f[0] == '_':
                continue
            val = self.__dict__[f]
            if val != None:
                res += '%s%s=%s' % (sep, f, val)
                sep = ','
        res += ')'
        return res

def quote(str):
    str = str.replace('"', '\"')
    # Replace comma by colon.  DigiKey doesn't
    # handle commas correctly even if they're inside double quotes...
    str = str.replace(',', ':')
    return '"' + str + '"'

@transaction.atomic
def save_assembly(assembly_part, bom):
    created = assembly_part.id is None

    assembly_part.last_bom_mod_type = Part.LAST_MOD_TYPE_TOOL
    assembly_part.last_bom_mod_name = MY_TOOL_NAME
    assembly_part.save()

    Assembly_Item.objects.filter(assy_id=assembly_part.id).delete()

    for components in bom:
        comp = components[0]
        refdes = ','.join(c.refdes for c in components)
        item = Assembly_Item(assy_id=assembly_part.id,
                             comp_id=comp.part_id,
                             qty=len(components),
                             refdes=refdes)
        item.save()
    print('%s: %s part %s (%s %s) with %d components' \
          % (MY_TOOL_NAME, 'created' if created else 'updated',
             format_part_number(assembly_part.id),
             assembly_part.mfg, assembly_part.mfg_pn, len(bom)),
          file=sys.stderr)

def update_comp(comp):
    footprint_field_index = part_number = None
    has_changed = False
    for index, line in enumerate(comp):
        m = re.match(r'F\s+(\d+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+'
                     '\s+\S+(\s+(\S+))?$', line)
        if m:
            if m.group(1) == '2':
                footprint_field_index = index
            elif m.lastindex >= 3 and m.group(4) == '"EP"':
                try:
                    part_str = m.group(2)[1:-1]
                    part_number = int(part_str)
                except ValueError:
                    print('%s: warning: invalid EPIC part number %s' %
                          (MY_TOOL_NAME, part_str), file=sys.stderr)
    if footprint_field_index is not None and part_number is not None:
        try:
            part = Part.objects.get(pk=part_number)
        except ObjectDoesNotExist:
            print('%s: error: Part %s does not exist' %
                  (MY_TOOL_NAME, format_part_number(part_number)),
                  file=sys.stderr)
            return False
        if part.footprint is None or part.footprint == '':
            if part.mounting != Part.MOUNTING_CHASSIS \
               and part.mounting != Part.MOUNTING_FREE:
                print('%s: warning: EPIC part %s has no footprint defined' %
                      (MY_TOOL_NAME, format_part_number(part.id)),
                      file=sys.stderr)
        else:
            old = comp[footprint_field_index]
            m = re.match(r'F\s+2\s+"([^"]*)"+\s+(.*)', old)
            if m:
                old_footprint = m.group(1)
                rest = m.group(2)
                new_footprint = part.footprint
                new = 'F 2 \"%s\" %s\n' % (new_footprint, rest)
                comp[footprint_field_index] = new
                if old_footprint != new_footprint:
                    print('%s: warning: footprint changed from %s to %s.'
                          % (MY_TOOL_NAME, old_footprint, new_footprint))
                    has_changed = True
                else:
                    has_changed = False
    return has_changed

def update_schematic(dirname, filename):
    '''Update schematic file FILENAME residing in directory DIRNAME with
    footprints from the EPIC database.

    '''
    schem_path = os.path.join(dirname, filename)
    has_changes = False
    with tempfile.NamedTemporaryFile(dir=dirname) as out:
        with io.open(schem_path, 'r', encoding='utf-8') as schem_file:
            inside_comp = False
            for line in schem_file:
                if line.rstrip() == '$Comp':
                    inside_comp = True
                    curr_comp = [line]
                elif line.rstrip() == '$EndComp':
                    inside_comp = False
                    curr_comp.append(line)
                    has_changes |= update_comp(curr_comp)
                    for comp_line in curr_comp:
                        out.write(comp_line.encode('utf-8'))
                elif inside_comp:
                    curr_comp.append(line)
                else:
                    out.write(line.encode('utf-8'))
        if has_changes:
            os.rename(schem_path, schem_path + '~')
            os.link(os.path.join(dirname, out.name), schem_path)
            print('%s: %s updated.  Use kicad to update net list and PCB'
                  % (MY_TOOL_NAME, schem_path))

def bom_append(bom, component):
    if component.part_id not in bom:
        bom[component.part_id] = []
    bom[component.part_id].append(component)

def bom_sort(bom):
    bom_list = []
    for part_id in bom:
        bom_list.append(bom[part_id])
    bom_list.sort(key=lambda x: x[0].part_id)
    return bom_list

def output_csv(outfile, bom_list, with_vendor_pn=False, preferred_vendors=None):
    for components in bom_list:
        qty = len(components)
        refdes = ','.join(c.refdes for c in components)
        c = components[0]

        substitutes = ''
        if c.part:
            sep = ''
            for sub in c.part.equivalent_parts():
                if sub == c.part:
                    continue
                substitutes += sep
                substitutes += '%s (%s %s)' % (format_part_number(sub.id),
                                               sub.mfg, sub.mfg_pn)
                sep = ', '


        row = '%s,%s,%s,%s,%s,%s,%s,%s' % \
              (qty, c.value, c.footprint, format_part_number(c.part_id),
               c.mfg, quote(c.mfg_pn), quote(substitutes), quote(refdes))

        if with_vendor_pn:
            vp = c.part.best_vendor_part(preferred_vendors)
            if vp is None:
                vendor = 'n/a'
                vendor_pn = 'n/a'
            else:
                vendor = vp.vendor
                vendor_pn = vp.vendor_pn
            row += ',%s,%s' % (vendor, vendor_pn)
        print(row, file=outfile)

def main():
    parser = argparse.ArgumentParser(description =
                                     'Create Bill-of-Materials (BOM) from '
                                     'eeschema XML file.  The BOM is stored '
                                     'as a comma-separated-values (CSV) file '
                                     'and as an EPIC BOM (assembly) part. '
                                     'Also, update the '
                                     'schematic files with the footprint info '
                                     'in the EPIC database.  The original '
                                     'schematic files are backed up in files '
                                     'with a tilde (~) appended to the '
                                     'original filename.')
    parser.add_argument('input-file', nargs=1, help='Name of XML file '
                        'generated by KiCad\'s \"Generate BOM\" command.')
    parser.add_argument('output-file', nargs=1, help='Name of output file '
                        'that will contain the bill-of-materials (BOM) in '
                        'a comma-separated-values (CSV) file.')
    parser.add_argument('-f', '--force-overwrite', action='store_true',
                        help='Force overwriting of existing EPIC BOM '
                        '(assembly) part even if the part appears to '
                        'have been modified manually.')
    parser.add_argument('-V', '--with-vendor-pn', action='store_true',
                        help='Include Vendor and Vendor part-number in the '
                        'CSV output.')
    parser.add_argument ('-p', '--prefer-vendor', nargs='+', default=[],
                         help='Prefer the specified vendor(s), even if those '
                         'do not have the lowest cost for a given part. '
                         'Non-preferred vendors are used only for parts that '
                         'could be ordered otherwise.')
    parser.add_argument('-n', '--no-update-footprints', action='store_true',
                        help='By default, this program will update the '
                        'schematic files with the footprint information '
                        'found in the parts database.  This option can be '
                        'specified to skip this step.')
    args = parser.parse_args()

    preferred_vendors = None
    for vendor_name in args.prefer_vendor:
        vendors = Vendor.objects.filter(name__istartswith=vendor_name)
        if len(vendors) < 1:
            print('%s: vendor `%s\' cannot be found' %
                  (MY_TOOL_NAME, vendor_name), file=sys.stderr)
            sys.exit(1)
        elif len(vendors) > 1:
            print('%s: vendor name `%s\' not unique, matches: %s' %
                  (MY_TOOL_NAME, vendor_name,
                   ', '.join(['`%s\'' % v.name for v in vendors])),
                  file=sys.stderr)
            sys.exit(1)
        if preferred_vendors is None:
            preferred_vendors = []
        preferred_vendors.append(vendors[0])

    output_filename = args.__dict__['output-file'][0]
    input_filename = args.__dict__['input-file'][0]

    xml = ET.parse(input_filename)

    schematic_name = 'unknown'
    revision = ''
    design = xml.find('design')
    sources = []
    source_path = path.dirname(input_filename)
    if design is not None:
        source = design.find('source')
        if source is not None:
            schematic_name = path.splitext(path.basename(source.text))[0]
            source_path = path.dirname(source.text)
        sheet = design.find('sheet')
        for sheet in design.iter('sheet'):
            title_block = sheet.find('title_block')
            if title_block is not None:
                if revision == '':
                    rev = title_block.find('rev')
                    if rev is not None:
                        revision = '-rev' + rev.text.lstrip().rstrip()
                sources.append(title_block.find('source').text)

    if not args.no_update_footprints:
        for schematic in sources:
            update_schematic(source_path, schematic)

    assembly_name = 'bom:' + schematic_name + revision
    qs = Part.objects.filter(mfg=manufacturer).filter(mfg_pn=assembly_name)
    if qs.exists():
        assembly_part = qs[0]
        if assembly_part.last_bom_mod_type != Part.LAST_MOD_TYPE_TOOL \
           or assembly_part.last_bom_mod_name != MY_TOOL_NAME:
            print('%s: part %s %s was last modified by %s %s' %
                  (MY_TOOL_NAME, manufacturer, assembly_name,
                   strchoice(Part.LAST_MOD_CHOICES,
                             assembly_part.last_bom_mod_type),
                   assembly_part.last_bom_mod_name), file=sys.stderr)
            if args.force_overwrite:
                print('%s: overwriting existing part due to --force-overwrite'
                      % MY_TOOL_NAME, file=sys.stderr)
            else:
                print('%s: refusing to overwrite part %s; '
                      'use --force-overwrite if desired' \
                      % (MY_TOOL_NAME, format_part_number(assembly_part.id)),
                      file=sys.stderr)
                sys.exit(1)
    else:
        assembly_part = Part(descr='BOM for %s' % schematic_name,
                             mfg=manufacturer, mfg_pn=assembly_name,
                             mounting=Part.MOUNTING_CHASSIS,
                             target_price=1000,
                             overage=1, spq=1, lead_time=4,
                             status=Part.STATUS_PREVIEW)

    bom = {}    # regular bom
    dnp = {}    # do-not-place bom
    for comp in xml.find('components'):
        part_id = None
        do_not_place = False
        fields = comp.find('fields')
        if fields is not None:
            for field in fields:
                if field.attrib['name'] == 'EP':
                    part_id = int(field.text)
                elif field.attrib['name'] == 'Installation' and \
                     field.text == 'DNP':
                    do_not_place = True
        c = Component(part_id, refdes=comp.attrib.get('ref'),
                      value=comp.findtext('value', default='n/a'))
        if do_not_place:
            print('%s: info: refdes %s marked as do-not-place '
                  '(Installation=DNP)' % (MY_TOOL_NAME, c.refdes),
                  file=sys.stderr)

        if part_id is None:
            print('%s: warning: skipping refdes %s due to missing '
                  'EPIC Part Number (EP field)' % (MY_TOOL_NAME, c.refdes),
                  file=sys.stderr)
            continue
        else:
            try:
                c.part = Part.objects.get(pk=part_id)
                if c.value != c.part.val:
                    print('%s: warning: %s has value %s but part %s has '
                          'value %s' % (MY_TOOL_NAME, c.refdes, c.value,
                                        format_part_number(part_id),
                                        c.part.val),
                          file=sys.stderr)
                c.footprint = c.part.footprint
                c.mfg = c.part.mfg
                c.mfg_pn = c.part.mfg_pn
            except ObjectDoesNotExist:
                print('%s: warning: part %s not found in database' %
                      (MY_TOOL_NAME, format_part_number(part_id)),
                      file=sys.stderr)
                continue
        if do_not_place:
            bom_append(dnp, c)
        else:
            bom_append(bom, c)

    bom_list = bom_sort(bom)
    dnp_list = bom_sort(dnp)

    out = io.open(output_filename, 'w', encoding='utf-8')
    hdr = (u'Qty,Value,Footprint,%s PN,Mfg,Mfg PN,Approved Substitutes,Refdes' %
           manufacturer)
    if args.with_vendor_pn:
        hdr += u',Vendor,Vendor PN'
    print(hdr, file=out)

    output_csv(out, bom_list, args.with_vendor_pn, preferred_vendors)

    if len(dnp_list) > 0:
        print('\nDO NOT PLACE parts:', file=out)
        output_csv(out, dnp_list, args.with_vendor_pn, preferred_vendors)

    save_assembly(assembly_part, bom_list)

if __name__ == '__main__':
    main()
