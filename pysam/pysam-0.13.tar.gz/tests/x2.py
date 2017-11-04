import subprocess
import threading
import errno
from pysam import VariantFile

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
            print('Wrote {} headers + {} records'.format(len(infile.header.records), i))

    writer = threading.Thread(target=_writer_thread, args=(infile, outfile))
    writer.daemon = True
    writer.start()
    return writer

proc = subprocess.Popen('head -n3000', stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

in_vars  = VariantFile('cbcf_data/example_vcf40.vcf')
out_vars = VariantFile(proc.stdin, 'w', header=in_vars.header)
writer   = writer_thread(in_vars, out_vars)

with VariantFile(proc.stdout) as new_invars:
    i = 0
    for i, record in enumerate(new_invars, 1):
        pass
    print('Read {} headers + {} records'.format(len(new_invars.header.records), i))
