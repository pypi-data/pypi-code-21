

def convert_file(in_filename, out_filename, in_format, out_format):
    from Bio import AlignIO
    
    with open(in_filename, "rU") as input_handle:
        with open(out_filename, "w") as output_handle:
            alignments = AlignIO.parse(input_handle,in_format)
            AlignIO.write(alignments, output_handle, out_format)
