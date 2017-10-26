import pandas as pd

def tsv_to_df(tsv_path, logger):
    data_dict = dict()
    with open(tsv_path, 'r') as f_open:
        i = 0
        for line in f_open:
            line = line.strip('\n')
            line_split = line.split('\t')
            data_dict[i] = line_split
            i += 1
    df = pd.DataFrame.from_dict(data_dict, orient='index')
    return df


def run(task_uuid, metric_path, bam, input_state, engine, logger):
    df = tsv_to_df(metric_path, logger)
    df.columns = ['NAME', 'LENGTH', 'ALIGNED_READS', 'UNALIGNED_READS']
    df['task_uuid'] = task_uuid
    df['bam'] = bam
    df['input_state'] = input_state
    table_name = 'samtools_idxstats'
    df.to_sql(table_name, engine, if_exists='append')
    return
