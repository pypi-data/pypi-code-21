import pandas as pd

def samtools_stats_to_dict(metric_path, task_uuid):
    data_dict = dict()
    data_dict['task_uuid'] = [task_uuid]
    values_to_store = ['raw total sequences:', 'filtered sequences:', 'sequences:',
                       'is sorted:', '1st fragments:', 'last fragments:', 'reads mapped:',
                       'reads mapped and paired:', 'reads unmapped:',
                       'reads properly paired:', 'reads paired:', 'reads duplicated:',
                       'reads MQ0:', 'reads QC failed:', 'non-primary alignments:',
                       'total length:', 'bases mapped:', 'bases mapped (cigar):',
                       'bases trimmed:', 'bases duplicated:', 'mismatches:', 'error rate:',
                       'average length:', 'maximum length:', 'average quality:',
                       'insert size average:', 'insert size standard deviation:',
                       'inward oriented pairs:', 'outward oriented pairs:',
                       'pairs with other orientation:', 'pairs on different chromosomes:']
    with open(metric_path, 'r') as f_open:
        for line in f_open:
            line = line.strip('\n')
            if line.startswith('SN\t'):
                line_split = line.split('\t')
                line_key = line_split[1]
                for value_to_store in values_to_store:
                    if value_to_store == line_key:
                        line_value = line_split[2].strip()
                        dict_key = value_to_store.strip(':')
                        if dict_key == 'bases mapped (cigar)':
                            dict_key = 'bases mapped CIGAR'
                        data_dict[dict_key] = line_value
    return data_dict


def run(task_uuid, metric_path, bam, input_state, engine, logger):
    data_dict = samtools_stats_to_dict(metric_path, task_uuid)
    df = pd.DataFrame(data_dict)
    df['bam'] = bam
    df['input_state'] = input_state
    table_name = 'samtools_stats'
    df.to_sql(table_name, engine, if_exists='append')
    return
