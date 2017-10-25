import os

from .metrics_util import picard_select_tsv_to_df


def picard_AlignmentSummaryMetrics_to_df(stats_path, logger):
    select = 'CATEGORY'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_BaseDistributionByCycle_to_df(stats_path, logger):
    select = 'READ_END'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_CollectQualityYieldMetrics_to_df(stats_path, logger):
    select = 'TOTAL_READS'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_GcBiasDetailMetrics_to_df(stats_path, logger):
    select = 'ACCUMULATION_LEVEL'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_GcBiasSummaryMetrics_to_df(stats_path, logger):
    select = 'ACCUMULATION_LEVEL'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_InsertSizeMetrics_metrics_to_df(stats_path, logger):
    select = 'MEDIAN_INSERT_SIZE'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_InsertSizeMetrics_histogram_to_df(stats_path, logger):
    select = 'insert_size'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    if df is not None:
        keep_column_list = ['insert_size', 'All_Reads.fr_count', 'All_Reads.rf_count', 'All_Reads.tandem_count']
        drop_column_list = [ column for column in df.columns if column not in keep_column_list]
        needed_column_list = [ column for column in keep_column_list if column not in df.columns ]
        #drop readgroup specific columns as the bam is already one readgroup
        logger.info('pre drop df=\n%s' % df)
        df.drop(drop_column_list, axis=1, inplace=True)
        logger.info('post drop df=\n%s' % df)
        #add columns that could be present in other files
        for needed_column in needed_column_list:
            df[needed_column] = None
    return df

def picard_MeanQualityByCycle_to_df(stats_path, logger):
    select = 'CYCLE'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_QualityScoreDistribution_to_df(stats_path, logger):
    select = 'QUALITY'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_SequencingArtifactMetrics_BaitBiasDetailMetrics_to_df(stats_path, logger):
    select = 'SAMPLE_ALIAS'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_SequencingArtifactMetrics_BaitBiasSummaryMetrics_to_df(stats_path, logger):
    select = 'SAMPLE_ALIAS'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_SequencingArtifactMetrics_PreAdapterDetailMetrics_to_df(stats_path, logger):
    select = 'SAMPLE_ALIAS'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df

def picard_SequencingArtifactMetrics_PreAdapterSummaryMetrics_to_df(stats_path, logger):
    select = 'SAMPLE_ALIAS'
    df = picard_select_tsv_to_df(stats_path, select, logger)
    return df


def run(bam, engine, input_state, logger, task_uuid,
        alignment_summary_metrics, bait_bias_detail_metrics,
        bait_bias_summary_metrics, base_distribution_by_cycle_metrics,
        gc_bias_detail_metrics, gc_bias_summary_metrics,
        insert_size_metrics, pre_adapter_detail_metrics,
        pre_adapter_summary_metrics, quality_by_cycle_metrics,
        quality_distribution_metrics, quality_yield_metrics):

    df_list = list()
    table_name_list = list()

    table_name = 'picard_AlignmentSummaryMetrics'
    stats_path = alignment_summary_metrics
    df = picard_AlignmentSummaryMetrics_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_BaseDistributionByCycleMetrics'
    stats_path = base_distribution_by_cycle_metrics
    df = picard_BaseDistributionByCycle_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_CollectQualityYieldMetrics'
    stats_path = quality_yield_metrics
    df = picard_CollectQualityYieldMetrics_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_GcBiasDetailMetrics'
    stats_path = gc_bias_detail_metrics
    df = picard_GcBiasDetailMetrics_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_GcBiasSummaryMetrics'
    stats_path = gc_bias_summary_metrics
    df = picard_GcBiasSummaryMetrics_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_InsertSizeMetrics'
    stats_path = insert_size_metrics
    df = picard_InsertSizeMetrics_metrics_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_InsertSizeMetrics_histogram'
    df = picard_InsertSizeMetrics_histogram_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_MeanQualityByCycle'
    stats_path = quality_by_cycle_metrics
    df = picard_MeanQualityByCycle_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_QualityScoreDistribution'
    stats_path = quality_distribution_metrics
    df = picard_QualityScoreDistribution_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_SequencingArtifactMetrics.BaitBiasDetailMetrics'
    stats_path = bait_bias_detail_metrics
    df = picard_SequencingArtifactMetrics_BaitBiasDetailMetrics_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_SequencingArtifactMetrics.BaitBiasSummaryMetrics'
    stats_path = bait_bias_summary_metrics
    df = picard_SequencingArtifactMetrics_BaitBiasSummaryMetrics_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_SequencingArtifactMetrics.PreAdapterDetailMetrics'
    stats_path = pre_adapter_detail_metrics
    df = picard_SequencingArtifactMetrics_PreAdapterDetailMetrics_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)

    table_name = 'picard_SequencingArtifactMetrics.PreAdapterSummaryMetrics'
    stats_path = pre_adapter_summary_metrics
    df = picard_SequencingArtifactMetrics_PreAdapterSummaryMetrics_to_df(stats_path, logger)
    if df is not None:
        df_list.append(df)
        table_name_list.append(table_name)
            
    for i, df in enumerate(df_list):
        logger.info('df_list enumerate i=%s:' % i)
        df['task_uuid'] = task_uuid
        df['bam'] = bam
        df['input_state'] = input_state
        table_name = table_name_list[i]
        df.to_sql(table_name, engine, if_exists='append')
    return
