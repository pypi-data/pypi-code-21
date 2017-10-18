#!/usr/bin/env python
import argparse
import os
import gzip


def get_argument_parser():
    p = argparse.ArgumentParser(description=
        'Remove annotation from FASTQ headers. '
        'This might be necessary for some analysis tools, '
        'which can not cope with non-standard header formats. '
        'The extracted annotation is written to a file with the '
        'name <filename>_annotation.txt.' )
    p.add_argument('files', nargs='+', metavar='FASTQ',
        help="One or more fastq files from which the annotation is to be extracted.")
    return p


def main():
    p = get_argument_parser()
    args = p.parse_args()
    for fq_file in args.files:
        clean_file(fq_file)
    

def splitext(path):
    prefix, extension = os.path.splitext(path)
    extensions = [extension]
    while extension:
        prefix, extension = os.path.splitext(prefix)
        if extension:
            extensions.insert(0, extension)
    return prefix, "".join(extensions)


def clean_file(in_path):
    """Remove annotation from a single FASTQ file."""
    # assume fastq files, not gzfastq
    prefix, extension = splitext(in_path)
    out_path_clean = prefix + "_noheader" + extension
    out_path_annotation = prefix + "_annotation.txt"

    print("Reading FASTQ file {}".format(in_path))
    print("Writing output files:")
    print("  - {}".format(out_path_clean))
    print("  - {}".format(out_path_annotation))

    with gzip.open(in_path, "rb") if in_path.endswith(".gz") else open(in_path, "rb") as in_file, \
         gzip.open(out_path_clean, "wb") if out_path_clean.endswith(".gz") else open(out_path_clean, "wb") as out_file_clean, \
         gzip.open(out_path_annotation, "wb") if out_path_annotation.endswith(".gz") else open(out_path_annotation, "wb") as out_file_annotation:

        for line in in_file:
            if line.startswith(b"@instrument"):
                casava_1, casava_2, ddrage = line.split(b" ", maxsplit=2)
                out_file_annotation.write(ddrage)
                out_file_clean.write(b" ".join((casava_1, casava_2)))
                out_file_clean.write(b"\n")
            else:
                out_file_clean.write(line)

if __name__ == '__main__':
    main()
