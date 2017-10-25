import pandas as pd

def get_data_dict(stats_path, logger):
    data_dict = dict()
    read_header = False
    
    with open(stats_path, 'r') as f_open:
        for line in f_open:
            if line.startswith("## HISTOGRAM"):
                break
            if line.startswith('#') or len(line) < 5:
                continue
            if not read_header:
                value_key_list = line.strip('\n').split('\t')
                logger.info('picard_markduplicates_to_dict() header value_key_list=\n\t%s' % value_key_list)
                logger.info('len(value_key_list=%s' % len(value_key_list))
                read_header = True
            else:
                data_list = line.strip('\n').split('\t')
                logger.info('picard_markduplicates_do_dict() data_list=\n\t%s' % data_list)
                logger.info('len(data_list)=%s' % len(data_list))
                for value_pos, value_key in enumerate(value_key_list):
                    data_dict[value_key] = data_list[value_pos]
    return data_dict

def run(task_uuid, stats_path, bam, input_state, engine, logger, metric_name):
    data_dict = get_data_dict(stats_path, logger)
    data_dict['task_uuid'] = [task_uuid]
    data_dict['bam'] = bam
    data_dict['input_state'] = input_state
    df = pd.DataFrame(data_dict)
    table_name = 'picard_' + metric_name
    df.to_sql(table_name, engine, if_exists='append')
    return
