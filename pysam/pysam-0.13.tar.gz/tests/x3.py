import subprocess
import threading
import errno
from pysam import AlignmentFile

def writer_thread(infile, outfile):
    def _writer_thread(infile, outfile):
        try:
            i = 0
            for i, record in enumerate(infile, 1):
                outfile.write(record)
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise
        finally:
            outfile.close()
            print('writer: Wrote {} records'.format(i))

    writer = threading.Thread(target=_writer_thread, args=(infile, outfile))
    writer.daemon = True
    writer.start()
    return writer

proc = subprocess.Popen('head -n200',
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        shell=True)

in_vars  = AlignmentFile('pysam_data/ex1.bam')
out_vars = AlignmentFile(proc.stdin, 'wh', header=in_vars.header)
writer   = writer_thread(in_vars, out_vars)

with AlignmentFile(proc.stdout) as new_invars:
    i = 0
    for i, record in enumerate(new_invars, 1):
        pass
    print('finally: Read {} records'.format(i))
