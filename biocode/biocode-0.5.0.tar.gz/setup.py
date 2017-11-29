
from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst', 'md')
except ImportError:
    raise Exception("Error: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(name='biocode',
      author='Joshua Orvis',
      author_email='jorvis@gmail.com',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
      ],
      description='Bioinformatics code libraries and scripts',
      include_package_data=True,
      install_requires=['pypandoc', 'igraph', 'jinja2', 'matplotlib'],
      keywords='bioinformatics scripts modules gff3 fasta fastq bam sam',
      license='MIT',
      long=read_md('biocode/README.md'),
      packages=['biocode'],
      scripts=['bin/filter_fastq_by_N_content.py', 'bin/convert_fastq_to_fasta.py', 'bin/validate_fasta.py', 'bin/filter_fasta_by_header_regex.py', 'bin/add_gff3_locus_tags.py', 'bin/split_molecules_on_gaps.py', 'bin/convert_gff3_to_gene_association_format.py', 'bin/extract_fasta_regions.py', 'bin/hmmlib_to_sqlite3.py', 'bin/convert_scipio_gff_to_gff3.py', 'bin/report_coverage_gaps.py', 'bin/remove_masked_gene_models.py', 'bin/remove_duplicate_sequences.py', 'bin/create_taxonomy_db.py', 'bin/merge_predicted_gff3.py', 'bin/report_or_replace_nonstandard_residues.py', 'bin/convert_aat_btab_to_gff3.py', 'bin/make_go_slim.py', 'bin/validate_feature_boundaries_on_molecules.py', 'bin/report_basic_gff_model_agreement.py', 'bin/make_cufflinks_ids_unique.py', 'bin/split_fasta_into_even_files.py', 'bin/remove_duplicate_features.py', 'bin/filter_gff3_by_id_list.py', 'bin/randomly_subsample_fastq.py', 'bin/convert_blast_btab_to_gff3.py', 'bin/write_fasta_from_gff.py', 'bin/replace_gff_type_column_value.py', 'bin/convert_genbank_to_gff3.py', 'bin/get_mpilup_from_id_list.py', 'bin/uniprot_sprot_to_sqlite3.py', 'bin/add_polypeptide_to_gff3_gene_models.py', 'bin/split_interleaved_sequence_file.py', 'bin/uniref_to_sqlite3.py', 'bin/compare_gene_structures.py', 'bin/convert_augustus_to_gff3.py', 'bin/reorient_sequences_by_id.py', 'bin/convert_gff3_to_gbk.py', 'bin/reverse_misordered_cds_coords.py', 'bin/convert_prodigal_to_gff3.py', 'bin/interleave_fastq.py', 'bin/tigrfam_info_to_sqlite3.py', 'bin/mark_partial_genes.py', 'bin/convert_pasa_gff_to_models.py', 'bin/eggnog_to_sqlite3.py', 'bin/filter_uniref_by_repid.py', 'bin/merge_masked_fasta_files.py', 'bin/convert_glimmerHMM_gff_to_gff3.py', 'bin/update_selected_column9_values.py', 'bin/interleave_fasta.py', 'bin/make_go_slim_index.py', 'bin/convert_cufflinks_gtf_to_gff3.py', 'bin/check_gff_for_internal_stops.py', 'bin/replace_homopolymeric_repeats_with_Ns.py', 'bin/extend_genes_to_stops.py', 'bin/append_to_fastq_read_header.py', 'bin/convert_metagenemark_gff_to_gff3.py', 'bin/report_gff3_statistics.py', 'bin/convert_fasta_contigs_to_gff3.py', 'bin/fasta_size_distribution_plot.py', 'bin/merge_bam_files.py', 'bin/correct_gff3_CDS_phase_column.py', 'bin/biothings_coordinate_comparisons.py', 'bin/prepend_to_fasta_header.py', 'bin/split_isoforms_into_individual_genes.py', 'bin/report_gff_intron_and_intergenic_stats.py', 'bin/merge_fasta_files_and_uniquify_ids.py', 'bin/subsample_fasta.py', 'bin/convert_cegma_gff_to_gff3.py', 'bin/detect_inverted_repeats.py', 'bin/create_taxonomic_profile_from_blast.py', 'bin/reformat_fasta_residue_lengths.py', 'bin/select_training_and_evaluation_transcripts.py', 'bin/append_to_fasta_header.py', 'bin/calculate_query_coverage_by_blast.py', 'bin/validate_uniref_member_characterization.py', 'bin/convert_gff3_to_ncbi_tbl.py', 'bin/filter_fasta_by_type.py', 'bin/remove_orphaned_features.py', 'bin/create_rsem_html_table.py', 'bin/filter_uniref_by_taxonomy.py', 'bin/set_source_column.py', 'bin/fasta_base_content.py', 'bin/check_for_embedded_fasta_headers.py', 'bin/fastq_simple_stats.py', 'bin/append_to_column_9_value.py'],
      url='http://github.com/jorvis/biocode',
      version='0.5.0',
      zip_safe=False)
    