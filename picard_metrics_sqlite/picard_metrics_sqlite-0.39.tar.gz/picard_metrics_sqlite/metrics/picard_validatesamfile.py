import sys
from collections import defaultdict

import pandas as pd

def run(task_uuid, stats_path, bam, input_state, engine, logger):
    val_error_dict = defaultdict(dict)
    with open(stats_path, 'r') as f_open:
        for line in f_open:
            if line.startswith('ERROR:'):
                validation_type = 'ERROR'
                line_split = line.strip().split(',')
                if len(line_split) == 4:
                    line_error = line_split[2:]
                    line_error = ', '.join(line_error)
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 3:
                    line_error = line_split[2]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 2:
                    line_error = line_split[1]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 1:
                    line_error = line_split[0]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                else:
                    logger.debug('validation_type=ERROR')
                    logger.debug('line: %s' % line)
                    logger.debug('Need to handle this comma amount: %s' % len(line_split))
                    sys.exit(1)
            elif line.startswith('WARNING:'):
                validation_type = 'WARNING'
                line_split = line.strip().split(',')
                if len(line_split) == 4:
                    line_error = line_split[2:]
                    line_error = ', '.join(line_error)
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 3:
                    line_error = line_split[2]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 2:
                    line_error = line_split[1].strip()
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                elif len(line_split) == 1:
                    line_error = line_split[0]
                    if line_error in val_error_dict[validation_type].keys():
                        val_error_dict[validation_type][line_error] += 1
                    else:
                        val_error_dict[validation_type][line_error] = 1
                else:
                    logger.debug('validation_type=WARNING')
                    logger.debug('line: %s' % line)
                    logger.debug('Need to handle this comma amount: %s' % len(line_split))
                    sys.exit(1)
            elif line.startswith('No errors found'):
                validation_type = 'PASS'
                line_error = line.strip()
                val_error_dict[validation_type][line_error] = 1
            else:
                logger.info('unknown picard validation line')
                logger.info('line=%s' % line)
                sys.exit(1)

    validation_type = 'ERROR'
    for akey in sorted(val_error_dict[validation_type].keys()):
        store_dict = dict()
        store_dict['value'] = akey
        store_dict['count'] = val_error_dict[validation_type][akey]
        store_dict['task_uuid'] = [rn_uuid]  # a non scalar
        store_dict['bam'] = bam
        store_dict['severity'] = validation_type
        store_dict['input_state'] = input_state
        df = pd.DataFrame(store_dict)
        table_name = 'picard_ValidateSamFile'
        df.to_sql(table_name, engine, if_exists='append')
    validation_type = 'WARNING'
    for akey in sorted(val_error_dict[validation_type].keys()):
        store_dict = dict()
        store_dict['value'] = akey
        store_dict['count'] = val_error_dict[validation_type][akey]
        store_dict['task_uuid'] = [task_uuid]  # a non scalar
        store_dict['bam'] = bam
        store_dict['severity'] = validation_type
        store_dict['input_state'] = input_state
        df = pd.DataFrame(store_dict)
        table_name = 'picard_ValidateSamFile'
        df.to_sql(table_name, engine, if_exists='append')
    validation_type = 'PASS'
    for akey in sorted(val_error_dict[validation_type].keys()):
        store_dict = dict()
        store_dict['value'] = akey
        store_dict['count'] = val_error_dict[validation_type][akey]
        store_dict['task_uuid'] = [task_uuid]  # a non scalar
        store_dict['bam'] = bam
        store_dict['severity'] = validation_type
        store_dict['input_state'] = input_state
        df = pd.DataFrame(store_dict)
        table_name = 'picard_ValidateSamFile'
        df.to_sql(table_name, engine, if_exists='append')
    return
