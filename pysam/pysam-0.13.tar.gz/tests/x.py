import subprocess
import pysam

args =["samtools", "view", "-u", "-F", "0x200", "pysam_data/ex1.bam", "chr1"]

proc = subprocess.Popen(args, stdout=subprocess.PIPE)

fd_child = proc.stdout.fileno()
print fd_child

with pysam.AlignmentFile(fd_child, "rb") as sam:
    for rec in sam:
        print rec

proc.communicate()
