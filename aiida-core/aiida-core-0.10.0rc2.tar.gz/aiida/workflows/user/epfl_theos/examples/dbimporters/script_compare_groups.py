#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-

from aiida.workflows.user.epfl_theos.dbimporters.utils \
    import composition_string, group_similar_structures,\
    get_source_id, get_source_db_name, get_is_structure_duplicate_results,\
    get_filter_duplicate_structures_results
from aiida.orm import DataFactory
import collections

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Andrius Merkys, Nicolas Mounet."


ParameterData = DataFactory('parameter')

def parse_cmdline():
    """
    Parse the command line.

    :return: a tuple with the parsed parameters.
    """
    import sys
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(
        description='Compare two groups of AiiDA structures. Produces '
                    'two-column output of similar structures PKs, where '
                    'first column contains PK from the first, second -- '
                    'from the second group. If the structure is unique '
                    'to any of the group, PK is given only for that '
                    'group. WARNING: for low dimensional structures with '
                    'a lot of vacuum, stol has to be reduced.')

    parser.add_argument('-a','--all',default=False,action='store_true',
                        help='Compare all structures from both groups '
                             'together, according to composition. If '
                             'False, each structure from the '
                             'first group will be compared to all '
                             'structures with the same composition from '
                             'the second group, and we output only those '
                             'unique to the first group (default=False)')    
    parser.add_argument('-1',default=False,action='store_true',
                        help='Suppress from the output the structures '
                             'unique to GROUPNAME1 (only with -a option)'
                             ' (default=False)')
    parser.add_argument('-2',default=False,action='store_true',
                        help='Suppress from the output the structures '
                             'unique to GROUPNAME2 (only with -a option)'
                             ' (default=False)')
    parser.add_argument('-3',default=False,action='store_true',
                        help='Suppress from the output the common '
                             'structures (only with -a option) (default=False)')
    parser.add_argument('-c','--create_groups',default=False,action='store_true',
                        help='Create new group(s) of structures, grouped '
                             'according to which group they belong (only '
                             'from first group, only from second group, '
                             'or common to both) (default=False)')
    parser.add_argument('-s','--store',default=False,action='store_true',
                        help='Store the filter duplicate inline calculations'
                        ' launched, and their output (default=False)')
    parser.add_argument('--ltol',type=float,default=0.2,
                        help='Fractional length tolerance (default = 0.2)')
    parser.add_argument('--stol',type=float, default=0.3,
                        help='Site tolerance. Defined as fraction of the '
                             'the average free length per atom = '
                             '(V/Nsites) ** (1/3) (default = 0.3). '
                             'WARNING: for low dimensional structures '
                             'with a lot of vacuum (i.e. large V), stol '
                             'has to be reduced.')
    parser.add_argument('--atol',type=float, default=5.0,
                        help='Angle tolerance in degrees (default = 5)')
    parser.add_argument('GROUPNAME1', type=str,
                        help='The name of the first group of structures')
    parser.add_argument('GROUPNAME2', type=str,
                        help='The name of the second group of structures')

    # Parse and return the values
    return vars(parser.parse_args(sys.argv[1:]))


if __name__ == '__main__':
    options = parse_cmdline()
    
    g1 = Group.get(name=options['GROUPNAME1'])
    g2 = Group.get(name=options['GROUPNAME2'])
    group1 = list(g1.nodes)
    group2 = list(g2.nodes)

    if options['create_groups']:
        # new groups
        if not options['all'] or not options['1']:
            group_only1, _ = Group.get_or_create(
                name='{}_not_in_grouppk_{}'.format(options['GROUPNAME1'],g2.pk))
                #name='{}_not_in_cod'.format(options['GROUPNAME1']))
        if options['all'] and not options['2']:
            group_only2, _ = Group.get_or_create(
                name='{}_not_in_grouppk_{}'.format(options['GROUPNAME2'],g1.pk))
        if options['all'] and not options['3']:
            group_common, _ = Group.get_or_create(
                name='structures_common_to_grouppks_{}_{}'.format(g1.pk,g2.pk))
        
    group1_uuids = list(models.DbNode.objects.filter(dbgroups=g1.dbgroup
            ).values_list('uuid',flat=True))
    group2_uuids = list(models.DbNode.objects.filter(dbgroups=g2.dbgroup
            ).values_list('uuid',flat=True))
    inline_params = ParameterData(dict={'ltol': options['ltol'],
                                        'stol': options['stol'],
                                        'angle_tol': options['atol']})

    if options['all']:
        # Here we use composition strings to group ALL the 
        # structures; this will filter duplicates again inside each
        # group - one then might end up with the warning 'one of the 
        # groups contain duplicates, please remove them before comparison'
        # even if duplicate filtering was already applied to each group...
        # (because the result of duplicate filtering depends on the 
        # reference structure chosen)
        structures = group1 + group2
        structure_string_id = collections.defaultdict(list)
        for ind, structure in enumerate(structures):
            string_id = composition_string(structure)
            # structure.set_extra('composition_string_id',string_id)
            structure_string_id[string_id].append(ind)
        
        for string_id, structure_indices in structure_string_id.iteritems():
            print "*"*50
            print "COMPOSITION: {}".format(string_id)
            input_structures_dict = dict([("structure_{}".format(i), structures[ind])
                                              for i,ind in enumerate(structure_indices)])
            result_dict = get_filter_duplicate_structures_results(parameters=inline_params,
                                                                  store=options['store'],
                                                                  **input_structures_dict)
            
            for ref_uuid,uuids in result_dict['output_parameters'].get_dict().iteritems():
                similar_structures = [load_node(uuid) for uuid in uuids]
                the_structure = similar_structures[0]
                ids = [get_source_id(s) for s in similar_structures]
                strings = ["ICSD:{}".format(the_id)
                            if get_source_db_name(s) == 'Icsd'
                            else "COD:{}".format(the_id) 
                            if get_source_db_name(s) == 'Crystallography Open Database'
                            else "Other:{}".format(the_id)
                            for the_id,s in zip(ids,similar_structures)]
                if len(uuids) == 1:
                    if (ref_uuid in group1_uuids) and not options['1']:
                        #print "{}\t".format(structures[index].pk)
                        print "{}\t{}\t-".format(the_structure.get_formula(separator=" "),strings[0])
                        if options['create_groups']:
                            group_only1.add_nodes([the_structure])
                            print "Structure {} added to group {}".format(the_structure.pk,group_only1.name)
                   
                    if (ref_uuid in group2_uuids) and not options['2']:
                        #print "\t{}".format(structures[index].pk)
                        print "{}\t-\t{}".format(the_structure.get_formula(separator=" "),strings[0])
                        if options['create_groups']:
                            group_only2.add_nodes([the_structure])
                            print "Structure {} added to group {}".format(the_structure.pk,group_only2.name)
               
                elif len(uuids) > 2:
                    print 'WARNING: one of the groups contain duplicates, ' \
                          'please remove them before comparison'
                
                elif len(uuids) == 2 and not options['3']:
                    #print "{}\t{}".format(*[structures[structure_indices[i]].pk for i in similar_group])
                    print "{}\t{}\t{}".format(the_structure.get_formula(separator=" "),strings[0],strings[1])
                    if options['create_groups']:
                        group_common.add_nodes([the_structure])
                        print "Structure {} added to group {}".format(the_structure.pk,group_common.name)
    
    else:
        # build first a dictionary to get all structures of a given
        # composition in group2
        print "*"*50
        print "BUILDING composition dictionary ..."
        structure_string_id = collections.defaultdict(list)
        for ind, s in enumerate(group2):
            string_id = composition_string(s)
            structure_string_id[string_id].append(ind)
        
        for structure_ref in group1:
            composition = composition_string(structure_ref)
            print "*"*50
            print "COMPOSITION: {}, STRUCTURE: {}".format(composition,structure_ref.pk)
            structure_indices = structure_string_id[composition] # 0 is for the reference structure from the first group
            input_structures_dict = dict([("structure_{}".format(i), group2[ind])
                                              for i,ind in enumerate(structure_indices)])
            print "Comparing structure to {} structure{} from second group".format(
                        len(input_structures_dict),'' if len(input_structures_dict)<=1 else 's')
            result_dict = get_is_structure_duplicate_results(parameters=inline_params,
                                                             structure_ref=structure_ref,
                                                             store=options['store'],
                                                             **input_structures_dict)
            
            uuids = [v for k,v in result_dict['output_parameters'].get_dict(
                ).iteritems() if k != 'is_duplicate'][0]
            similar_structures = [load_node(uuid) for uuid in uuids]
            ids = [get_source_id(s) for s in similar_structures]
            strings = ["ICSD:{}".format(the_id)
                       if get_source_db_name(s) == 'Icsd'
                       else "COD:{}".format(the_id) 
                       if get_source_db_name(s) == 'Crystallography Open Database'
                       else "Other:{}".format(the_id)
                       for the_id,s in zip(ids,similar_structures)]
            print "{}\t{}".format(structure_ref.get_formula(separator=" "),"\t".join(strings))
                
            if (options['create_groups'] and
                not result_dict['output_parameters'].get_dict()['is_duplicate']):
                group_only1.add_nodes([structure_ref])
                print "Structure {} added to group {}".format(structure_ref.pk,group_only1.name)
                    
