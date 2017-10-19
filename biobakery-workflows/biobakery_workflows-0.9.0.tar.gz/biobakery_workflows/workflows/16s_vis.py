#!/usr/bin/env python

"""
bioBakery Workflows: 16S workflow for visualization

Copyright (c) 2017 Harvard School of Public Health

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

# import the workflow class from anadama2
from anadama2 import Workflow

# import the document templates from biobakery_workflows
from biobakery_workflows import document_templates, utilities

# import the files for descriptions and paths
from biobakery_workflows import files

# create a workflow instance, providing the version number and description
# remove the input folder option as it will be replaced with multiple input files
workflow = Workflow(version="0.1", remove_options=["input"],
                    description="A workflow for 16S visualization")

# list the required and optional files for the workflow
# these are expected to be included in the input folder
input_files={"required":["otu_table_closed_reference","otu_table_open_reference","read_count_table","eestats2","msa_nonchimera","msa_closed_reference"]}

# create a custom description for the input argument listing all expected input files
input_desc="A folder containing the final products from the 16s data workflow.\n\nThe input folder should include the following:\n\n"
input_desc+=files.SixteenS.list_file_path_description("",input_files)

# add the custom arguments to the workflow                          
workflow.add_argument("input",desc=input_desc,required=True)

# add the custom arguments to the workflow
workflow.add_argument("project-name",desc="the name of the project",required=True)
workflow.add_argument("input-metadata",desc="the metadata file (samples as columns or rows)")
workflow.add_argument("input-picard",desc="the folder of picard quality score files")
workflow.add_argument("input-picard-extension",desc="the extensions for the picard quality score files", default="quality_by_cycle_metrics")
workflow.add_argument("metadata-categorical",desc="the categorical features", action="append", default=[])
workflow.add_argument("metadata-continuous",desc="the continuous features", action="append", default=[])
workflow.add_argument("metadata-exclude",desc="the features to exclude", action="append", default=[])
workflow.add_argument("exclude-workflow-info",desc="do not include data processing task info in report", action="store_true")
workflow.add_argument("format",desc="the format for the report", default="pdf", choices=["pdf","html"])

# get the arguments from the command line
args = workflow.parse_args()

# get the paths for the required files and check they are found
otu_table=files.SixteenS.path("otu_table_closed_reference",args.input, error_if_not_found=True)
otu_open_table=files.SixteenS.path("otu_table_open_reference",args.input, error_if_not_found=True)
read_count_table=files.SixteenS.path("read_count_table",args.input, error_if_not_found=True)
eestats_table=files.SixteenS.path("eestats2",args.input, error_if_not_found=True)
centroid_fasta = files.SixteenS.path("msa_nonchimera",args.input, error_if_not_found=True)
centroid_closed_fasta = files.SixteenS.path("msa_closed_reference", args.input, error_if_not_found=True)

# read and label the metadata
metadata=None
metadata_labels=None
if args.input_metadata:
    metadata=utilities.read_metadata(args.input_metadata, otu_table, ignore_features=args.metadata_exclude, otu_table=True)
    metadata_labels, metadata=utilities.label_metadata(metadata, categorical=args.metadata_categorical, continuous=args.metadata_continuous)

templates=[document_templates.get_template("16S")]

# add the template for the data processing information
log_file=None
if not args.exclude_workflow_info:
    templates+=[document_templates.get_template("workflow_info")]
    log_file=files.Workflow.path("log", args.input, error_if_not_found=True)

# add the document to the workflow
doc_task=workflow.add_document(
    templates=templates,
    depends=[otu_table, read_count_table, otu_open_table, eestats_table, centroid_fasta, centroid_closed_fasta], 
    targets=workflow.name_output_files("16S_report."+args.format),
    vars={"title":"16S Report",
          "project":args.project_name,
          "otu_table":otu_table,
          "read_count_table":read_count_table,
          "eestats_table":eestats_table,
          "format":args.format,
          "log":log_file,
          "metadata":metadata,
          "metadata_labels":metadata_labels,
          "picard":args.input_picard,
          "picard_ext":args.input_picard_extension},
    table_of_contents=True)

# add an archive of the document and figures, removing the log file
# the archive will have the same name and location as the output folder
workflow.add_archive(
    depends=[args.output,doc_task],
    targets=args.output+".zip",
    remove_log=True)

# start the workflow
workflow.go()
