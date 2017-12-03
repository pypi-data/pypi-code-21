
import os
from pdfrw import PdfReader, PdfWriter

def strip_pages_pdf(indir, infile, outdir=None, outfile=None, numpages=1, keep=False):
    '''
    Deletes the first pages from a PDF. Omit outfile name to replace. Default is one page.
    If option keep is specified, keeps first pages of PDF, dropping rest.
    '''
    if outfile is None:
        outfile = infile
        
    if outdir is None:
        outdir = indir

    output = PdfWriter()
    inpath = os.path.join(indir,infile)
    outpath = os.path.join(outdir,outfile)
    
    for i, page in enumerate(PdfReader(inpath).pages):
        if not keep:
            if i > (numpages - 1):
                output.addpage(page)
        if keep:
            if i <= (numpages - 1):
                output.addpage(page)

    output.write(outpath)