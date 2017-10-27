# pylint: disable=missing-docstring
COLLECTIONS_SAMPLE = [{
    'contributor': 1,
    'created': '2016-04-07T08:03:38.314293Z',
    'data': [13, 14],
    'description': 'Test colllection',
    'descriptor': {},
    'descriptor_schema': None,
    'id': 21,
    'modified': '2016-04-07T08:03:38.314330Z',
    'name': 'TestCollection',
    'permissions': {
        'group': [],
        'public': [],
        'user': ['add', 'download', 'edit', 'share', 'view']
    },
    'settings': {},
    'slug': 'TestCollection'
}]

PROCESS_SAMPLE = [{
    'category': 'upload:',
    'contributor': 1,
    'created': '2016-04-20T10:37:15.058595Z',
    'description': 'Upload NGS reads in FASTQ format.\n',
    'id': 99,
    'input_schema': [{
        'description': 'NGS reads in FASTQ format. Supported extensions: .fastq.gz '
                       '(preferred), .fq.* or .fastq.*\n',
        'label': 'NGS reads (FASTQ)',
        'name': 'src',
        'required': True,
        'type': 'basic:file:',
        'validate_regex': '(\\.(fastq|fq)(|\\.gz|\\.bz2|\\.tgz|\\.tar'
                          '\\.gz|\\.tar\\.bz2|\\.zip|\\.rar|\\.7z))|(\\.bz2)$'
    }],
    'modified': '2016-04-20T10:37:15.058616Z',
    'name': 'Upload NGS reads',
    'output_schema': [{
        'label': 'Reads file',
        'name': 'fastq',
        'type': 'basic:file:'
    }, {
        'label': 'Number of reads',
        'name': 'number',
        'type': 'basic:integer:'
    }, {
        'label': 'Number of bases',
        'name': 'bases',
        'type': 'basic:string:'
    }, {
        'label': 'Quality control with FastQC',
        'name': 'fastqc_url',
        'type': 'basic:url:view:'
    }, {
        'label': 'Download FastQC archive',
        'name': 'fastqc_archive',
        'type': 'basic:file:'
    }],
    'permissions': {
        'group': [],
        'public': [],
        'user': ['share', 'view']
    },
    'persistence': 'RAW',
    'run': {
        'bash': 're-import "{{ src.file_temp|default:src.file }}" "{{ src.file }}" "fastq|fq|bz2" "fastq" 0.5 "extract"\n\n#detect and if old Illumina encoding is found transform to new format\nfastqFormatDetect.pl ${NAME}.fastq &> encoding.txt\nif [[ $(grep \'Solexa/Illumina1.3+/Illumina1.5+\' "encoding.txt") ]]\nthen\n  sed -i -e \'4~4y/@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghi/!"#$%&\'\\\'\'()*+,-.\\/0123456789:;<=>?@ABCDEFGHIJ/\' "${NAME}.fastq"\nfi\n\ngzip -c ${NAME}.fastq > ${NAME}.fastq.gz\nre-save-file fastq ${NAME}.fastq.gz\n\necho "Postprocessing FastQC..."\nmkdir "fastqc" && fastqc "${NAME}.fastq" --extract --outdir="fastqc" 2> stderr.txt\nre-checkrc "Failed while processing with FastQC."\nif [[ $(grep --text "Failed to process file" stderr.txt) != "" ]]\nthen\n  re-error "Failed while processing with FastQC."\nfi\nre-progress 0.9\n\nBASES=$(awk \'/^Sequence length/ {print $3}\' fastqc/*_fastqc/fastqc_data.txt)\nNUMBER=`sed -ne \'s/^Total Sequences\\s*\\([0-9\\.]\\+\\)\\s*$/\\1/pi\' fastqc/*_fastqc/fastqc_data.txt | head -n 1`\nFASTQC_URL="{\\"name\\":\\"View\\",\\"url\\":\\"fastqc/${NAME}_fastqc/fastqc_report.html\\",\\"refs\\":[\\"fastqc/${NAME}_fastqc\\"]}"\nmv "fastqc/${NAME}_fastqc.zip" .\n\nre-save-file fastqc_archive ${NAME}_fastqc.zip\nre-save number $NUMBER\nre-save bases "\\"$BASES\\""\nre-save fastqc_url $FASTQC_URL\n',  # noqa pylint: disable=line-too-long
        'runtime': 'polyglot'
    },
    'slug': 'import-upload-reads-fastq',
    'type': 'data:reads:fastq:single:',
    'version': 16777233
}, {
    'category': 'upload:',
    'contributor': 1,
    'created': '2016-04-20T10:37:15.058595Z',
    'description': 'Upload NGS reads in FASTQ format.\n',
    'id': 99,
    'input_schema': [{
        'description': 'NGS reads in FASTQ format. Supported extensions: .fastq.gz (preferred), '
                       '.fq.* or .fastq.*\n',
        'label': 'NGS reads (FASTQ)',
        'name': 'src',
        'required': True,
        'type': 'basic:file:',
        'validate_regex': '(\\.(fastq|fq)(|\\.gz|\\.bz2|\\.tgz|\\.tar'
                          '\\.gz|\\.tar\\.bz2|\\.zip|\\.rar|\\.7z))|(\\.bz2)$'
    }],
    'modified': '2016-04-20T10:37:15.058616Z',
    'name': 'Upload NGS reads',
    'output_schema': [{
        'label': 'Reads file',
        'name': 'fastq',
        'type': 'basic:file:'
    }, {
        'label': 'Number of reads',
        'name': 'number',
        'type': 'basic:integer:'
    }, {
        'label': 'Number of bases',
        'name': 'bases',
        'type': 'basic:string:'
    }, {
        'label': 'Quality control with FastQC',
        'name': 'fastqc_url',
        'type': 'basic:url:view:'
    }, {
        'label': 'Download FastQC archive',
        'name': 'fastqc_archive',
        'type': 'basic:file:'
    }],
    'permissions': {
        'group': [],
        'public': [],
        'user': ['share', 'view']
    },
    'persistence': 'RAW',
    'run': {
        'bash': 're-import "{{ src.file_temp|default:src.file }}" "{{ src.file }}" "fastq|fq|bz2" "fastq" 0.5 "extract"\n\n#detect and if old Illumina encoding is found transform to new format\nfastqFormatDetect.pl ${NAME}.fastq &> encoding.txt\nif [[ $(grep \'Solexa/Illumina1.3+/Illumina1.5+\' "encoding.txt") ]]\nthen\n  sed -i -e \'4~4y/@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghi/!"#$%&\'\\\'\'()*+,-.\\/0123456789:;<=>?@ABCDEFGHIJ/\' "${NAME}.fastq"\nfi\n\ngzip -c ${NAME}.fastq > ${NAME}.fastq.gz\nre-save-file fastq ${NAME}.fastq.gz\n\necho "Postprocessing FastQC..."\nmkdir "fastqc" && fastqc "${NAME}.fastq" --extract --outdir="fastqc" 2> stderr.txt\nre-checkrc "Failed while processing with FastQC."\nif [[ $(grep --text "Failed to process file" stderr.txt) != "" ]]\nthen\n  re-error "Failed while processing with FastQC."\nfi\nre-progress 0.9\n\nBASES=$(awk \'/^Sequence length/ {print $3}\' fastqc/*_fastqc/fastqc_data.txt)\nNUMBER=`sed -ne \'s/^Total Sequences\\s*\\([0-9\\.]\\+\\)\\s*$/\\1/pi\' fastqc/*_fastqc/fastqc_data.txt | head -n 1`\nFASTQC_URL="{\\"name\\":\\"View\\",\\"url\\":\\"fastqc/${NAME}_fastqc/fastqc_report.html\\",\\"refs\\":[\\"fastqc/${NAME}_fastqc\\"]}"\nmv "fastqc/${NAME}_fastqc.zip" .\n\nre-save-file fastqc_archive ${NAME}_fastqc.zip\nre-save number $NUMBER\nre-save bases "\\"$BASES\\""\nre-save fastqc_url $FASTQC_URL\n',  # noqa pylint: disable=line-too-long
        'runtime': 'polyglot'
    },
    'slug': 'import-upload-reads-fastq',
    'type': 'data:reads:fastq:single:',
    'version': 16777234
}, {
    'category': 'analyses:variants:',
    'contributor': 1,
    'created': '2016-04-07T07:40:01.593209Z',
    'description': 'Filtering and annotation of Variant Calling data -'
                   ' Chemical mutagenesis in Dictyostelium discoideum\n',
    'id': 1,
    'input_schema': [{
        'label': 'Variants file (VCF)',
        'name': 'variants',
        'required': True,
        'type': 'data:variants:vcf:'
    }, {
        'choices': [{
            'label': 'SNV',
            'value': 'snv'
        }, {
            'label': 'INDEL',
            'value': 'indel'
        }, {
            'label': 'SNV_CHR2',
            'value': 'snv_chr2'
        }, {
            'label': 'INDEL_CHR2',
            'value': 'indel_chr2'
        }],
        'default': 'snv',
        'description': 'Choice of the analysis type. Use "SNV" or "INDEL" options for the analysis of VCF files prepared by using GATK UnifiedGenotyper -glm option "SNP" or "INDEL", respectively. Choose options SNV_CHR2 or INDEL_CHR2 if duplication of CHR2 was considered as diploidy when running GATK analysis (-ploidy 2 -L chr2:2263132-3015703).\n',  # noqa pylint: disable=line-too-long
        'label': 'Analysis type',
        'name': 'analysis_type',
        'type': 'basic:string:'
    }, {
        'label': 'Parental Strain Prefix',
        'name': 'parental_strain',
        'placeholder': 'AX4',
        'type': 'basic:string:'
    }, {
        'label': 'Mutant Strain Prefix',
        'name': 'mutant_strain',
        'placeholder': 'mutant',
        'type': 'basic:string:'
    }, {
        'default': 5,
        'label': 'Read Depth Cutoff',
        'name': 'read_depth',
        'type': 'basic:integer:'
    }],
    'modified': '2016-04-07T07:40:01.593226Z',
    'name': 'Variant filtering (Chemical Mutagenesis)',
    'output_schema': [{
        'description': 'Summarize the input parameters and results.\n',
        'label': 'Summary',
        'name': 'summary',
        'type': 'basic:file:'
    }, {
        'description': 'A genome VCF file of variants that passed the filters.\n',
        'label': 'Variants',
        'name': 'vcf',
        'type': 'basic:file:'
    }, {
        'description': 'A data frame of variants that passed the filters.\n',
        'label': 'Variants filtered',
        'name': 'variants_filtered',
        'type': 'basic:file:'
    }, {
        'description': 'A data frame of variants that contain more than two alternative alleles. '
                       'These vairants are likely to be false positives.\n',
        'label': 'Variants filtered (multiple alt. alleles)',
        'name': 'variants_filtered_alt',
        'type': 'basic:file:'
    }, {
        'description': 'Genes that are mutated at least once.\n',
        'label': 'Gene list (all)',
        'name': 'gene_list_all',
        'type': 'basic:file:'
    }, {
        'description': 'Genes that are mutated at least twice.\n',
        'label': 'Gene list (top)',
        'name': 'gene_list_top',
        'type': 'basic:file:'
    }, {
        'description': 'List mutations in individual chromosomes.\n',
        'label': 'Mutations (by chr)',
        'name': 'mut_chr',
        'type': 'basic:file:'
    }, {
        'description': 'List mutations in individual strains.\n',
        'label': 'Mutations (by strain)',
        'name': 'mut_strain',
        'type': 'basic:file:'
    }, {
        'description': 'List mutants that carry mutations in individual genes.\n',
        'label': 'Strain (by gene)',
        'name': 'strain_by_gene',
        'type': 'basic:file:'
    }],
    'permissions': {
        'group': [],
        'public': [],
        'user': ['share', 'view']
    },
    'persistence': 'CAC',
    'run': {
        'bash': 'NAME=`basename \'{{ variants.vcf.file }}\' .vcf`\nre-progress 0.05\n\ncp {{variants.vcf.file}} .\n\nRscript -e \'source("R/{{analysis_type}}.R")\' -e \'{{analysis_type}}(input_file = "\'${NAME}.vcf\'", ref_file = "reference_files/", parental_strain = "{{parental_strain}}", mutant_strain = "{{mutant_strain}}", read_depth = \'{{read_depth}}\')\'\nre-checkrc "VCF file filtering failed"\nre-progress 0.9\n\nif [ -f ${NAME}.vcf_{{read_depth}}/summary.txt ];\nthen\n  re-save-file summary ${NAME}.vcf_{{read_depth}}/summary.txt\nfi\n\nif [ -f ${NAME}.vcf_{{read_depth}}/variants.vcf ];\nthen\n  bgzip -c "${NAME}.vcf_{{read_depth}}/variants.vcf" > "${NAME}.vcf_{{read_depth}}/variants.vcf.bgz"\n  tabix -p vcf "${NAME}.vcf_{{read_depth}}/variants.vcf.bgz"\n  re-save-file vcf ${NAME}.vcf_{{read_depth}}/variants.vcf ${NAME}.vcf_{{read_depth}}/variants.vcf.bgz ${NAME}.vcf_{{read_depth}}/variants.vcf.bgz.tbi\nfi\n\nif [ -f ${NAME}.vcf_{{read_depth}}/variant_filtered.txt ];\nthen\n  re-save-file variants_filtered ${NAME}.vcf_{{read_depth}}/variant_filtered.txt\nfi\n\nif [ -f ${NAME}.vcf_{{read_depth}}/variant_mult_alt.txt ];\nthen\n  re-save-file variants_filtered_alt ${NAME}.vcf_{{read_depth}}/variant_mult_alt.txt\nfi\n\nif [ -f ${NAME}.vcf_{{read_depth}}/gene_list_all.txt ];\nthen\n  re-save-file gene_list_all ${NAME}.vcf_{{read_depth}}/gene_list_all.txt\nfi\n\nif [ -f ${NAME}.vcf_{{read_depth}}/gene_list_top.txt ];\nthen\n  re-save-file gene_list_top ${NAME}.vcf_{{read_depth}}/gene_list_top.txt\nfi\n\nif [ -f ${NAME}.vcf_{{read_depth}}/mutations_by_chr.txt ];\nthen\n  re-save-file mut_chr ${NAME}.vcf_{{read_depth}}/mutations_by_chr.txt\nfi\n\nif [ -f ${NAME}.vcf_{{read_depth}}/mutations_by_strain.txt ];\nthen\n  re-save-file mut_strain ${NAME}.vcf_{{read_depth}}/mutations_by_strain.txt\nfi\n\nif [ -f ${NAME}.vcf_{{read_depth}}/strain_by_gene.txt ];\nthen\n  re-save-file strain_by_gene ${NAME}.vcf_{{read_depth}}/strain_by_gene.txt\nfi\n',  # noqa pylint: disable=line-too-long
        'runtime': 'polyglot'
    },
    'slug': 'vc_filtering_chem_mutagenesis',
    'type': 'data:variants:vcf:filtering:',
    'version': 16777216
}, {
    'category': 'analyses:variants:',
    'contributor': 1,
    'created': '2016-04-07T07:40:01.608498Z',
    'description': 'GATK varint calling. Note: Usage of Genome Analysis '
                   'Toolkit requires a licence.\n',
    'id': 2,
    'input_schema': [{
        'label': 'Reference genome',
        'name': 'genome',
        'required': True,
        'type': 'data:genome:fasta:'
    }, {
        'label': 'Mapped reads',
        'name': 'mapping',
        'required': True,
        'type': 'data:alignment:bam:'
    }, {
        'default': True,
        'label': 'Do variant base recalibration and indel realignment',
        'name': 'br_and_ind_ra',
        'type': 'basic:boolean:'
    }, {
        'default': False,
        'description': 'Writes a file containing metrics about the statistical distribution of '
                       'insert size (excluding duplicates) and generates a Histogram plot.\n',
        'label': 'Collect insert size metrics',
        'name': 'collectinsertsizemetrics',
        'type': 'basic:boolean:'
    }, {
        'label': 'Known sites',
        'name': 'known_sites',
        'required': False,
        'type': 'data:variants:vcf:'
    }, {
        'label': 'Known indels',
        'name': 'known_indels',
        'required': False,
        'type': 'list:data:variants:vcf:'
    }, {
        'group': [{
            'default': 'x',
            'label': 'Read group identifier',
            'name': 'ID',
            'required': True,
            'type': 'basic:string:'
        }, {
            'default': 'x',
            'description': 'Sample. Use pool name where a pool is being sequenced.\n',
            'label': 'Sample',
            'name': 'SM',
            'required': True,
            'type': 'basic:string:'
        }, {
            'choices': [{
                'label': 'Capillary',
                'value': 'Capillary'
            }, {
                'label': 'Ls454',
                'value': 'Ls454'
            }, {
                'label': 'Illumina',
                'value': 'Illumina'
            }, {
                'label': 'SOLiD',
                'value': 'SOLiD'
            }, {
                'label': 'Helicos',
                'value': 'Helicos'
            }, {
                'label': 'IonTorrent',
                'value': 'IonTorrent'
            }, {
                'label': 'Pacbio',
                'value': 'Pacbio'
            }],
            'default': 'Illumina',
            'description': 'Platform/technology used to produce the reads.\n',
            'label': 'Platform/technology',
            'name': 'PL',
            'required': True,
            'type': 'basic:string:'
        }, {
            'default': 'x',
            'label': 'Library',
            'name': 'LB',
            'required': True,
            'type': 'basic:string:'
        }, {
            'default': 'x',
            'description': 'Platform unit (e.g. flowcell-barcode.lane for Illumina or slide for '
                           'SOLiD). Unique identifier.\n',
            'label': 'Platform unit',
            'name': 'P',
            'required': True,
            'type': 'basic:string:'
        }, {
            'default': 'x',
            'description': 'Name of sequencing center producing the read.\n',
            'label': 'Sequencing center',
            'name': 'CN',
            'required': True,
            'type': 'basic:string:'
        }, {
            'description': 'Date the run was produced.\n',
            'label': 'Date',
            'name': 'DT',
            'required': True,
            'type': 'basic:date:'
        }],
        'label': 'Reads information',
        'name': 'reads_info'
    }, {
        'group': [{
            'default': 10,
            'description': 'The minimum confidence threshold (phred-scaled) at which the program '
                           'should emit sites that appear to be possibly variant.\n',
            'label': 'Emission confidence threshold',
            'name': 'stand_emit_conf',
            'required': True,
            'type': 'basic:integer:'
        }, {
            'default': 30,
            'description': 'the minimum confidence threshold (phred-scaled) at which the program should emit variant sites as called. If a site\'s associated genotype has a confidence score lower than the calling threshold, the program will emit the site as filtered and will annotate it as LowQual. This threshold separates high confidence calls from low confidence calls.\n',  # noqa pylint: disable=line-too-long
            'label': 'Calling confidence threshold',
            'name': 'stand_call_conf',
            'required': True,
            'type': 'basic:integer:'
        }],
        'label': 'Parameters of HaplotypeCaller',
        'name': 'Varc_param'
    }],
    'modified': '2016-04-07T07:40:01.608515Z',
    'name': 'Variant calling (GATK)',
    'output_schema': [{
        'label': 'Called variants file',
        'name': 'vcf',
        'type': 'basic:file:'
    }, {
        'label': 'Insert size metrics',
        'name': 'ism',
        'type': 'basic:file:'
    }],
    'permissions': {
        'group': [],
        'public': [],
        'user': ['share', 'view']
    },
    'persistence': 'CAC',
    'run': {
        'bash': 'echo "uncompressing genome, indexing"\nGENOME_NAME=`basename \'{{ genome.fasta.file }}\' .fasta.gz`\ngzip -cd {{ genome.fasta.file }} > "${GENOME_NAME}.fasta"\nsamtools faidx "${GENOME_NAME}.fasta"\npicard CreateSequenceDictionary R="${GENOME_NAME}.fasta" O="${GENOME_NAME}.dict"\necho "{\\"proc.progress\\":0.05,\\"proc.rc\\":$?}"\n\necho "bam files processing"\nBAM_FILE=`basename \'{{ mapping.bam.file }}\' .bam`\n\necho "sorting, marking duplicates, indexing"\npicard MarkDuplicates I="{{ mapping.bam.file }}" O="${BAM_FILE}_inds.bam" METRICS_FILE=junk.txt VALIDATION_STRINGENCY=LENIENT\necho "{\\"proc.progress\\":0.1,\\"proc.rc\\":$?}"\npicard AddOrReplaceReadGroups I="${BAM_FILE}_inds.bam" O="${BAM_FILE}_indh.bam" RGID={{reads_info.ID}} RGLB={{reads_info.LB}} RGPL={{reads_info.PL}} RGPU={{reads_info.PU}} RGSM={{reads_info.SM}} RGCN={{reads_info.CN}} RGDT={{reads_info.DT}}\necho "{\\"proc.progress\\":0.15,\\"proc.rc\\":$?}"\nsamtools index "${BAM_FILE}_indh.bam"\necho "{\\"proc.progress\\":0.2,\\"proc.rc\\":$?}"\n\n{% if collectinsertsizemetrics %}\n  picard CollectInsertSizeMetrics I="${BAM_FILE}_indh.bam" O="${BAM_FILE}".CollectInsertSizeMetrics H="${BAM_FILE}".CollectIsertSizeMetrics.pdf VALIDATION_STRINGENCY=LENIENT\n  echo "{\\"proc.progress\\":0.25,\\"proc.rc\\":$?,\\"ism\\":{\\"file\\":\\"${BAM_FILE}.CollectIsertSizeMetrics.pdf\\"}}"\n{% endif %}\n\n{% if br_and_ind_ra %}\n  echo "indel realignment"\n  gatk -T RealignerTargetCreator -I "${BAM_FILE}_indh.bam" -R "${GENOME_NAME}.fasta" -o indel_interval.bed {% if known_indels %} -known {% for indelx in known_indels %}{{ indelx.vcf.file }} {% endfor %}{% endif %}\n  echo "{\\"proc.progress\\":0.3,\\"proc.rc\\":$?}"\n  gatk -T IndelRealigner -I "${BAM_FILE}_indh.bam" -R "${GENOME_NAME}.fasta" -o "${BAM_FILE}_noncal.bam" -targetIntervals indel_interval.bed -compress 0\n  echo "{\\"proc.progress\\":0.35,\\"proc.rc\\":$?}"\n\n  echo "Base recalibration"\n  gatk -T BaseRecalibrator -I "${BAM_FILE}_noncal.bam"  -R "${GENOME_NAME}.fasta" -o recal_data.table -knownSites \'{{ known_sites.vcf.file }}\'\n  echo "{\\"proc.progress\\":0.4,\\"proc.rc\\":$?}"\n  gatk -T PrintReads -I "${BAM_FILE}_noncal.bam" -R "${GENOME_NAME}.fasta" -o "${BAM_FILE}_final.bam" -BQSR recal_data.table\n  echo "{\\"proc.progress\\":0.45,\\"proc.rc\\":$?}"\n{% else %}\n  mv "${BAM_FILE}_indh.bam" "${BAM_FILE}_final.bam"\n{% endif %}\n\nsamtools index "${BAM_FILE}_final.bam"\n\necho "variant calling"\ngatk -T UnifiedGenotyper -I "${BAM_FILE}_final.bam" -R "${GENOME_NAME}.fasta" -o "${BAM_FILE}_GATKvariants.vcf" {% if known_sites %} --dbsnp {{ known_sites.vcf.file }} {% endif %} -stand_call_conf {{ Varc_param.stand_call_conf }} -stand_emit_conf {{ Varc_param.stand_emit_conf }} -rf ReassignOneMappingQuality -RMQF 255 -RMQT 60\necho "{\\"proc.progress\\":0.8,\\"proc.rc\\":$?}"\n\n#echo "hard filtering"\n#gatk -V "${BAM_FILE}_haplotype.vcf" -o "${BAM_FILE}_filtered.vcf" -T VariantFiltration -R "${GENOME_NAME}.fasta" --filterName GATKstandard --filterExpression "QUAL < 30 || QD < 5.0"\n#vcftools --vcf "${BAM_FILE}_filtered.vcr"\n#mv "${BAM_FILE}_filtered.vcr" "${BAM_FILE}_GATKvariants.vcf"\n\nbgzip -c "${BAM_FILE}_GATKvariants.vcf" > "${BAM_FILE}_GATKvariants.vcf.bgz"\necho "{\\"proc.progress\\":0.9,\\"proc.rc\\":$?}"\ntabix -p vcf "${BAM_FILE}_GATKvariants.vcf.bgz"\necho "{\\"proc.progress\\":0.95,\\"proc.rc\\":$?}"\n\necho "{\\"proc.progress\\":1,\\"vcf\\":{\\"file\\": \\"${BAM_FILE}_GATKvariants.vcf\\", \\"refs\\":[\\"${BAM_FILE}_GATKvariants.vcf.bgz\\",\\"${BAM_FILE}_GATKvariants.vcf.bgz.tbi\\"] }}"\n',  # noqa pylint: disable=line-too-long
        'runtime': 'polyglot'
    },
    'slug': 'vc-gatk',
    'type': 'data:variants:vcf:gatk:',
    'version': 16777226
}, ]

DATA_SAMPLE = [{
    'process': 26,
    'contributor': 1,
    'process_output_schema': [{
        'type': 'basic:file:',
        'name': 'fastq',
        'label': 'Reads file'
    }, {
        'type': 'basic:integer:',
        'name': 'number',
        'label': 'Number of reads'
    }, {
        'type': 'basic:string:',
        'name': 'bases',
        'label': 'Number of bases'
    }, {
        'type': 'basic:url:view:',
        'name': 'fastqc_url',
        'label': 'Quality control with FastQC'
    }, {
        'type': 'basic:file:',
        'name': 'fastqc_archive',
        'label': 'Download FastQC archive'
    }],
    'id': 13,
    'process_type': 'data:reads:fastq:single:',
    'process_error': [],
    'process_progress': 0,
    'input': {
        'src': {
            'file': '20151231-shep21-0hr-twist-RZ2638_S4_R1_001.fastq',
            'file_temp': '/home/jure/devel/genialis-base/upload/'
                         '3b1a12c7-5725-4386-b1c3-98209330cdc6'
        }
    },
    'process_info': [],
    'status': 'PR',
    'process_rc': None,
    'started': '2016-04-18T07:31:03.329782Z',
    'process_name': 'Upload NGS reads',
    'process_warning': [],
    'finished': None,
    'slug': '54861ac8-48fd-4ec9-8dab-07b159442e20',
    'permissions': {
        'group': [],
        'user': ['download',
                 'edit',
                 'share',
                 'view'],
        'public': []
    },
    'name': 'Name1',
    'descriptor_schema': None,
    'created': '2016-04-18T09:31:03.273940Z',
    'checksum': None,
    'modified': '2016-04-18T09:31:03.321548Z',
    'descriptor': {},
    'process_input_schema': [{
        'validate_regex': '(\\.(fastq|fq)(|\\.gz|\\.bz2|\\.tgz|\\.tar'
                          '\\.gz|\\.tar\\.bz2|\\.zip|\\.rar|\\.7z))|(\\.bz2)$',
        'description': 'NGS reads in FASTQ format. Supported extensions: .fastq.gz (preferred), '
                       '.fq.* or .fastq.*\n',
        'required': True,
        'label': 'NGS reads (FASTQ)',
        'type': 'basic:file:',
        'name': 'src'
    }],
    "output": {
        "fastq": {
            "file": "example.fastq.gz"
        },
        "bases": "75"
    }
}, {
    'process': 26,
    'contributor': 1,
    'process_output_schema': [{
        'type': 'basic:file:',
        'name': 'fastq',
        'label': 'Reads file'
    }, {
        'type': 'basic:integer:',
        'name': 'number',
        'label': 'Number of reads'
    }, {
        'type': 'basic:string:',
        'name': 'bases',
        'label': 'Number of bases'
    }, {
        'type': 'basic:url:view:',
        'name': 'fastqc_url',
        'label': 'Quality control with FastQC'
    }, {
        'type': 'basic:file:',
        'name': 'fastqc_archive',
        'label': 'Download FastQC archive'
    }],
    'id': 14,
    'process_type': 'data:reads:fastq:single:',
    'process_error': [],
    'process_progress': 100,
    'input': {
        'src': {
            'file': '20151231-shep21-0hr-twist-RZ2638_S4_R1_001.fastq',
            'file_temp': '/home/jure/devel/genialis-base/upload/'
                         'bce3fd27-692f-46f6-ba09-bb14c0c7ce9f'
        }
    },
    'process_info': [],
    'status': 'ER',
    'process_rc': 1,
    'started': '2016-04-18T07:31:09.712650Z',
    'process_name': 'Upload NGS reads',
    'process_warning': [],
    'finished': '2016-04-18T07:31:09.723797Z',
    'slug': '8a3f7685-9942-45d5-9dff-e0c8654ba39b',
    'permissions': {
        'group': [],
        'user': ['download',
                 'edit',
                 'share',
                 'view'],
        'public': []
    },
    'name': 'Name2',
    'descriptor_schema': None,
    'created': '2016-04-18T09:31:09.645791Z',
    'checksum': None,
    'modified': '2016-04-18T09:31:09.702595Z',
    'descriptor': {},
    'process_input_schema': [{
        'validate_regex': '(\\.(fastq|fq)(|\\.gz|\\.bz2|\\.tgz|\\.tar'
                          '\\.gz|\\.tar\\.bz2|\\.zip|\\.rar|\\.7z))|(\\.bz2)$',
        'description': 'NGS reads in FASTQ format. Supported extensions: .fastq.gz (preferred), '
                       '.fq.* or .fastq.*\n',
        'required': True,
        'label': 'NGS reads (FASTQ)',
        'type': 'basic:file:',
        'name': 'src'
    }],
    'output': {}
}]
