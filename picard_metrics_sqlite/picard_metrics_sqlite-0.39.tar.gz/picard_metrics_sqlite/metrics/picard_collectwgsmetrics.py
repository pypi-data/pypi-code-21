import os

from .metrics_util import picard_select_tsv_to_df

def picard_CollectWgsMetrics_to_df(metric_path, logger):
    select = 'GENOME_TERRITORY'
    df = picard_select_tsv_to_df(metric_path, select, logger)
    return df

def picard_CollectWgsMetrics_histogram_to_df(metric_path, logger):
    select = 'coverage'
    df = picard_select_tsv_to_df(metric_path, select, logger)
    return df

def run(task_uuid, metric_path, bam, input_state, engine, logger, metric_name):
    table_name = 'picard_' + metric_name
    df = picard_CollectWgsMetrics_to_df(metric_path, logger)
    df['bam'] = bam
    df['input_state'] = input_state
    df['task_uuid'] = task_uuid
    df.to_sql(table_name, engine, if_exists='append')

    table_name += '_histogram'
    df = picard_CollectWgsMetrics_histogram_to_df(metric_path, logger)
    df['bam'] = bam
    df['input_state'] = input_state
    df['task_uuid'] = task_uuid
    df.to_sql(table_name, engine, if_exists='append')
    return
