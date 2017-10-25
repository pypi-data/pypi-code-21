#!/usr/bin/env python

import argparse
import logging
import os
import sys

import sqlalchemy

from .metrics import picard_collectalignmentsummarymetrics
from .metrics import picard_collecthsmetrics
from .metrics import picard_collectmultiplemetrics
from .metrics import picard_collectoxogmetrics
from .metrics import picard_collectrnaseqmetrics
from .metrics import picard_collectwgsmetrics
from .metrics import picard_markduplicates
from .metrics import picard_validatesamfile

def get_param(args, param_name):
    if vars(args)[param_name] == None:
        return None
    else:
        return vars(args)[param_name]
    return

def setup_logging(tool_name, args, task_uuid):
    logging.basicConfig(
        filename=os.path.join(task_uuid + '_' + tool_name + '.log'),
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

def main():
    parser = argparse.ArgumentParser('picard docker tool')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    # Required flags.
    parser.add_argument('--input_state',
                        required = True
    )
    parser.add_argument('--metric_name',
                        required = True,
                        help = 'picard tool'
    )
    parser.add_argument('--metric_path',
                        required = False
    )
    parser.add_argument('--task_uuid',
                        required = True,
                        help = 'uuid string',
    )

    # Tool flags
    parser.add_argument('--bam',
                        required = False
    )
    parser.add_argument('--bam_library',
                        required = False
    )
    parser.add_argument('--exome_kit',
                        required = False
    )
    parser.add_argument('--fasta',
                        required = False
    )
    parser.add_argument('--ref_flat',
                        required = False
    )
    parser.add_argument('--ribosomal_intervals',
                        required = False
    )
    parser.add_argument('--vcf',
                        required = False
    )

    #cmm
    parser.add_argument('--alignment_summary_metrics',
                        required = False
    )
    parser.add_argument('--bait_bias_detail_metrics',
                        required = False
    )
    parser.add_argument('--bait_bias_summary_metrics',
                        required = False
    )
    parser.add_argument('--base_distribution_by_cycle_metrics',
                        required = False
    )
    parser.add_argument('--gc_bias_detail_metrics',
                        required = False
    )
    parser.add_argument('--gc_bias_summary_metrics',
                        required = False
    )
    parser.add_argument('--insert_size_metrics',
                        required = False
    )
    parser.add_argument('--pre_adapter_detail_metrics',
                        required = False
    )
    parser.add_argument('--pre_adapter_summary_metrics',
                        required = False
    )
    parser.add_argument('--quality_by_cycle_metrics',
                        required = False
    )
    parser.add_argument('--quality_distribution_metrics',
                        required = False
    )
    parser.add_argument('--quality_yield_metrics',
                        required = False
    )
    
    # setup required parameters
    args = parser.parse_args()
    input_state = args.input_state
    metric_name = args.metric_name
    metric_path = args.metric_path
    task_uuid = args.task_uuid

    logger = setup_logging('picard_' + metric_name, args, task_uuid)

    sqlite_name = task_uuid + '.db'
    engine_path = 'sqlite:///' + sqlite_name
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    if metric_name == 'CollectAlignmentSummaryMetrics':
        bam = get_param(args, 'bam')
        picard_collectalignmentsummarymetrics.run(task_uuid, metric_path, bam, input_state, engine, logger, metric_name)
    elif metric_name == 'CollectHsMetrics':
        bam = get_param(args, 'bam')
        bam_library = get_param(args, 'bam_library')
        input_state = get_param(args, 'input_state')
        exome_kit = get_param(args, 'exome_kit')
        picard_collecthsmetrics.run(task_uuid, metric_path, bam, bam_library, exome_kit, input_state, engine, logger, metric_name)
    elif metric_name == 'CollectMultipleMetrics':
        bam = get_param(args, 'bam')
        input_state = get_param(args, 'input_state')
        alignment_summary_metrics = get_param(args, 'alignment_summary_metrics')
        bait_bias_detail_metrics = get_param(args, 'bait_bias_detail_metrics')
        bait_bias_summary_metrics = get_param(args, 'bait_bias_summary_metrics')
        base_distribution_by_cycle_metrics = get_param(args, 'base_distribution_by_cycle_metrics')
        gc_bias_detail_metrics = get_param(args, 'gc_bias_detail_metrics')
        gc_bias_summary_metrics = get_param(args, 'gc_bias_summary_metrics')
        insert_size_metrics = get_param(args, 'insert_size_metrics')
        pre_adapter_detail_metrics = get_param(args, 'pre_adapter_detail_metrics')
        pre_adapter_summary_metrics = get_param(args, 'pre_adapter_summary_metrics')
        quality_by_cycle_metrics = get_param(args, 'quality_by_cycle_metrics')
        quality_distribution_metrics = get_param(args, 'quality_distribution_metrics')
        quality_yield_metrics = get_param(args, 'quality_yield_metrics')
        picard_collectmultiplemetrics.run(bam, engine, input_state, logger, task_uuid,
                                          alignment_summary_metrics, bait_bias_detail_metrics,
                                          bait_bias_summary_metrics, base_distribution_by_cycle_metrics,
                                          gc_bias_detail_metrics, gc_bias_summary_metrics,
                                          insert_size_metrics, pre_adapter_detail_metrics,
                                          pre_adapter_summary_metrics, quality_by_cycle_metrics,
                                          quality_distribution_metrics, quality_yield_metrics
        )
    elif metric_name == 'CollectOxoGMetrics':
        bam = get_param(args, 'bam')
        input_state = get_param(args, 'input_state')
        picard_collectoxogmetrics.run(task_uuid, metric_path, bam, input_state, engine, logger, metric_name)
    elif metric_name == 'CollectRnaSeqMetrics':
        bam = get_param(args, 'bam')
        input_state = get_param(args, 'input_state')
        picard_collectrnaseqmetrics.run(task_uuid, metric_path, bam, input_state, engine, logger, metric_name)
    elif metric_name == 'CollectWgsMetrics':
        bam = get_param(args, 'bam')
        input_state = get_param(args, 'input_state')
        picard_collectwgsmetrics.run(task_uuid, metric_path, bam, input_state, engine, logger, metric_name)
    elif metric_name == 'MarkDuplicates':
        bam = get_param(args, 'bam')
        input_state = get_param(args, 'input_state')
        picard_markduplicates.run(task_uuid, metric_path, bam, input_state, engine, logger, metric_name)
    # elif metric_name == 'MarkDuplicatesWithMateCigar':
    #     bam = get_param(args, 'bam')
    #     input_state = get_param(args, 'input_state')
    #     picard_markduplicateswithmatecigar.run(task_uuid, bam, input_state, engine, logger)
    # elif metric_name == 'FixMateInformation':
    #     bam = get_param(args, 'bam')
    #     input_state = get_param(args, 'input_state')
    #     picard_fixmateinformation.run(task_uuid, bam, input_state, engine, logger)
    elif metric_name == 'ValidateSamFile':
        bam = get_param(args, 'bam')
        input_state = get_param(args, 'input_state')
        picard_validatesamfile.run(task_uuid, metric_path, bam, input_state, engine, logger)
    else:
        sys.exit('No recognized tool was selected')
        
    return

if __name__ == '__main__':
    main()
