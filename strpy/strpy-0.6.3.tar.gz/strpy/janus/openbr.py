import os
import tempfile
import numpy as np
from scipy import sparse
from strpy.bobo.util import tempcsv, temppdf,  islist, tolist, Stopwatch, lower_bound, quietprint
import strpy.bobo.metrics
from strpy.janus.dataset.cs2 import CS2
from itertools import product

def writebinary(M, mtxfile=None):
    """Write a numpy array to a binary file, consistent with openbr"""
    """First 4 bytes indicate the number of rows, second 4 bytes indicate the number of columns. The rest of the bytes are 32-bit floating data elements in row-major order."""
    mtxfile = tempfile.mktemp() + '.mtx' if mtxfile is None else mtxfile
    (row,col) = M.shape
    with open(mtxfile, 'wb') as f:
        f.write(np.array( [row], dtype=np.uint32).view(np.uint8).tostring())
        f.write(np.array( [col], dtype=np.uint32).view(np.uint8).tostring())
        f.write(M.view(np.uint8).tostring())  # see also ndarray.tofile
        return mtxfile

def readbinary(mtxfile):
    """Read a numpy array from a binary file, consistent with openbr"""    
    """First 4 bytes indicate the number of rows, second 4 bytes indicate the number of columns. The rest of the bytes are 32-bit floating data elements in row-major order."""
    with open(mtxfile, 'rb') as f:
        rows = int(np.fromfile(f, dtype=np.uint32, count=1, sep=''));  f.seek(4)
        cols = int(np.fromfile(f, dtype=np.uint32, count=1, sep='')); f.seek(8)
        mtx = np.reshape(np.fromfile(f, dtype=np.float32, count=-1, sep=''), (rows,cols) )
        return mtx

def readbee(mtxfile):
    """https://github.com/biometrics/janus/blob/master/src/janus_io.cpp"""
    with open(mtxfile, 'rb') as f:
        f.readline()
        f.readline()
        f.readline()
        header = f.readline().split(' ')
        rows = int(header[1])
        cols = int(header[2])
        if header[0] == 'MB':
            mtx = np.reshape(np.fromfile(f, dtype=np.uint8, count=-1, sep=''), (rows,cols) )
        else:
            mtx = np.reshape(np.fromfile(f, dtype=np.float32, count=-1, sep=''), (rows,cols) )
    return mtx
    
def writebee(mtx, mtxfile=None):
    """https://github.com/biometrics/janus/blob/master/src/janus_io.cpp"""
    mtxfile = tempfile.mktemp() + '.mtx' if mtxfile is None else mtxfile
    with open(mtxfile, 'wb') as f:
        f.write('S2\n')  # ?
        f.write('target_sigset\n')  # target sigset?
        f.write('query_sigset\n')  # query sigset?
        f.write('M%s %d %d %s\n' % ('F' if mtx.dtype=='float32' else 'B', mtx.shape[0], mtx.shape[1], np.array( [0x12345678], dtype=np.uint32).view(np.uint8).tostring()))  # endian?
        f.write(mtx.view(np.uint8).tostring())  # see also ndarray.tofile
    return mtxfile


def brMaskMatrix(is_same, ProbeTemplateID=None, GalleryTemplateID=None, returnTemplateID=False):
    """Generate OpenBR Mask Matrix for given probe and gallery IDs with ground truth same/different"""
    """If IDs are not provided, mask matrix is asssumed to be diagonal with zeros on off diagonal"""
    ProbeTemplateID = ProbeTemplateID if ProbeTemplateID is not None else range(0,len(is_same))  # zero indexed
    GalleryTemplateID = GalleryTemplateID if GalleryTemplateID is not None else range(0,len(is_same))  # zero indexed

    M = len(set(ProbeTemplateID))
    N = len(set(GalleryTemplateID))
    mtx = np.zeros( (M, N), dtype=np.uint8)
    I = []; J = [];
    for (v,i,j) in zip(is_same, ProbeTemplateID, GalleryTemplateID):
        # Maintain template ID order 
        if i in I:
            p = np.argwhere(i == np.array(I))  # template ID to row index
        else:
            I.append(i)  # append template ID to row index list
            p = len(I) - 1

        if j in J:
            q = np.argwhere(j == np.array(J))
        else:
            J.append(j)
            q = len(J) - 1

        if mtx[p,q] != 0:
            raise ValueError('[janus.metrics.brMaskMatrix]: double entry at (%d,%d)' % (p,q))
        mtx[p,q] = np.uint8(128*v + 127)  # same=255, different=127, invalid=0

    if returnTemplateID:
        return (mtx, I, J) # matrix and template ID of rows (I) and columns (J)
    else:
        return mtx
    

def brSimilarityMatrix(similarity_score, ProbeTemplateID=None, GalleryTemplateID=None, returnTemplateID=False):
    """Generate OpenBR Similarity Matrix for given probe and gallery IDs with similarity score"""
    """If IDs are not provided, matrix is asssumed to be diagonal with zeros on off diagonal"""
    ProbeTemplateID = ProbeTemplateID if ProbeTemplateID is not None else range(0,len(similarity_score))  # zero indexed
    GalleryTemplateID = GalleryTemplateID if GalleryTemplateID is not None else range(0,len(similarity_score))  # zero indexed

    M = len(set(ProbeTemplateID))
    N = len(set(GalleryTemplateID))
    mtx = np.zeros( (M, N), dtype=np.float32)
    I = []; J = []; 
    for (v,i,j) in zip(similarity_score, ProbeTemplateID, GalleryTemplateID):
        # Maintain template ID order: map templateID (i,j) to matrix index (p,q) 
        if i in I:
            p = np.argwhere(i == np.array(I))  # template ID to row index
        else:
            I.append(i);  # append template ID to row index list
            p = len(I) - 1  # matrix row index

        if j in J:
            q = np.argwhere(j == np.array(J))
        else:
            J.append(j);
            q = len(J) - 1 # matrix column index

        if mtx[p,q] != 0:
            raise ValueError('[janus.metrics.brSimilarityMatrix]: double entry at (%d,%d)' % (p,q))
        mtx[p,q] = np.float32(v)  # same=255, different=127, invalid=0

    if returnTemplateID:
        return (mtx, I, J) # matrix and template ID of rows (I) and columns (J)
    else:
        return mtx


def openbr_eval(y=None, yhat=None, similaritymtx=None, maskmtx=None, csvfile=None, ProbeTemplateID=None, GalleryTemplateID=None):
    #br -eval $MATRIX/protocolA.mtx $MATRIX/protocolA.mask $RESULTS/protocolA.csv
    #br -eval $MATRIX/protocolB.mtx $MATRIX/protocolB.mask $RESULTS/protocolB.csv
    if similaritymtx is None and yhat is not None:
        similaritymtx = brSimilarityMatrix(yhat, ProbeTemplateID, GalleryTemplateID)
    if maskmtx is None and y is not None:
        maskmtx = brMaskMatrix(y, ProbeTemplateID, GalleryTemplateID)

    simfile = writebee(similaritymtx, mtxfile='%s.mtx' % tempfile.mktemp())  # must have .mtx extension
    maskfile = writebee(maskmtx, mtxfile='%s.mask' % tempfile.mktemp())  # must have .mask extension
    if csvfile is None:
        csvfile = tempcsv()
    cmd = 'br -platform offscreen -eval %s %s %s' % (simfile, maskfile, csvfile)
    print '[janus.metrics.openbr]: executing "%s" ' % cmd
    os.system(cmd)
    return csvfile


def openbr_plot(csvfiles=None, pdffile=None):
    if isinstance(csvfiles,str):
        csvfiles=[csvfiles]

    files = ' '.join(csvfiles)
    cmd = 'br -platform offscreen -plot %s %s' % (files, pdffile)
    print '[janus.metrics.openbr]: executing "%s" ' % cmd
    os.system(cmd)
    return pdffile


def openbr(y=None, yhat=None, similaritymtx=None, maskmtx=None, pdffile=None, ProbeTemplateID=None, GalleryTemplateID=None, csvfile=None):
    # plot results in openBR
    #br -plot $RESULTS/protocolA.csv $RESULTS/protocolB.csv $RESULTS/resultsAB.pdf

    csvfile = openbr_eval(y=y, yhat=yhat, similaritymtx=similaritymtx, maskmtx=maskmtx, ProbeTemplateID=ProbeTemplateID, GalleryTemplateID=GalleryTemplateID, csvfile=csvfile)

    cmd = 'br -platform offscreen -plot %s %s' % (csvfile, pdffile)
    print '[janus.metrics.openbr]: executing "%s" ' % cmd
    os.system(cmd)
    return pdffile


def importbr(mtxfile, maskfile):
    mtx = readbee(mtxfile)
    yhat = mtx.flatten()
    mask = readbee(maskfile)
    y = mask.flatten()
    k = np.where(y >= 127)
    y = np.float32(y[k] > 127)  # {0,1}
    #bobo.metrics.plot_roc(y_true=y, y_pred=yhat[k], logx=True)
    return (y, yhat[k])


