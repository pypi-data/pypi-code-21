#!/usr/bin/env python
#-*- coding: utf-8 -*-

import argparse, sys
import numpy as np
import scipy.sparse
import scipy.stats
import multiprocessing

from hicexplorer import HiCMatrix
from hicexplorer.utilities import _fdr

import parserCommon

w_width = None
p_width = None

orig_matrix = None

pvalue = True

def parse_argumentss(args=None):
    """
    parse arguments
    """

    parent_parser = parserCommon.getParentArgParse()
    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Applies a transformation to a Hi-C matrix.')

    parser.add_argument('--originalMat',
                        help='File name containing the original hic matrix',
                        type=argparse.FileType('r'))

    parser.add_argument('--outFileName', '-o',
                        help='File name to save the resulting matrix ',
                        type=parserCommon.writableFile,
                        required=True)

    parser.add_argument(
                        '--chromosome',
                        help='Chromosome name to compute the values ',
                        required=True,
                        default=None)

    parser.add_argument('--numberOfProcessors',  '-p',
                        help='Number of processors to use ',
                        type=int,
                        default=1)

    parser.add_argument('--type',
                        help='output type. The options are "obs/exp" or "p-value".',
                        choices=['obs/exp', 'p-value'],
                        required=True)

    return parser.parse_args(args)


def compute_local_background_for_pixel(matrix, expected_matrix, row, col, correction_factors):
    """
    Given a corrected Hi-C matrix and a 'expected values' matrix this function returns
    either the obs/exp ratio or the p-value after considering the local background using
    the shapes proposed by Rao et al (lower_left, donut, horizontal and vertical). It chooses
    the shape that results in the lower ratio (or least significant p-value)
    :param matrix: scipy sparse csr corrected Hi-C matrix
    :param expected_matrix: scipy sparse csr expected values matrix
    :param row: row position of pixel to evaluate
    :param col: col position of pixel to evaluate
    :param correction_factors: Correction factors used to correct the Hi-C matrix

    :return:
    """

    global p_width, w_width
    lambda_ = [expected_matrix[row, col]]
    for what in ['lower_left', 'donut', 'horizontal', 'vertical']:
        counts = get_matrix_section_mean(matrix, row, col, w_width, p_width, what)

        exp = get_matrix_section_mean(expected_matrix, row, col, w_width, p_width, what)

        if np.isnan(counts):
            # close to the matrix borders and close to the diagonal
            # the value of the counts is nan.
            lambda_.append(np.nan)
            return np.nan
        if counts == 0 and exp > 0:
            counts = exp

        lambda_.append((float(counts)/exp) * expected_matrix[row, col])

    # get the highest of the computed lambdas
    lambda_ = max(lambda_)

    if ARGS.type == 'p-value':

        pixel_value = np.rint(matrix[row, col] * correction_factors[row] * correction_factors[col])
        value = -1 * scipy.stats.poisson.logsf(pixel_value,
                                               lambda_ * correction_factors[row] * correction_factors[col])
    else:
        value = float(matrix[row, col]) / lambda_

    return value
        
    
def get_matrix_section_mean(matrix, row, col, w_width, p_width, what='lower_left'):
    """
    computes sub matrices based on Rao et al. 2014
    :param matrix: Hi-C matrix
    :param i: row idx
    :param j: col idx
    :param what: string, type of matrix. Options are
            lower_left, donut, horizontal, vertical
    :return: mean value of counts found in the given
    matrix section

    >>> w_width = 5
    >>> p_width =2
    >>> matrix = np.zeros((13,13))
    >>> matrix[1:12, 1:12] = 1
    >>> matrix[4:9,4:9] = 5
    >>> matrix[6,6] = 10
    >>> #print matrix
    >>> get_matrix_section_mean(scipy.sparse.csr_matrix(matrix), 6, 6, w_width, p_width, 'donut')
    1.0
    >>> matrix = np.zeros((13,13))
    >>> matrix[1:12, 1:12] = 1
    >>> matrix[7:12,1:6] = 3
    >>> matrix[4:9,4:9] = 5
    >>> matrix[6,6] = 10
    >>> # print matrix
    >>> get_matrix_section_mean(scipy.sparse.csr_matrix(matrix), 6, 6, w_width, p_width, 'lower_left')
    3.0
    >>> get_matrix_section_mean(scipy.sparse.csr_matrix(matrix), 6, 6, w_width, p_width, 'horizontal')
    1.3333333333333333
    >>> get_matrix_section_mean(scipy.sparse.csr_matrix(matrix), 6, 6, w_width, p_width, 'vertical')
    1.3333333333333333

    """


    M = matrix.shape[0]
    # check that the area to check is not too close to the borders or
    # to the diagonal
    if row-w_width < 0 or col-w_width < 0 or \
        row+w_width + 1 > M or col+w_width + 1 > M or \
        row+w_width+1 > col - w_width:

        return np.nan

    if what == 'lower_left':
        values = np.concatenate([matrix[row+1:row+w_width+1,
                                  col-w_width:col-p_width].data,
                                 matrix[row+p_width+1:row+w_width+1,
                                  col-p_width:col-1].data])

    elif what == 'donut':
        # donut values are computed by first selecting a sub-matrix and
        # then subtracting the regions that are not interesting?

        donut_matrix = matrix[row-w_width:row+w_width+1,
                              col-w_width:col+w_width+1].todense()

        # remove the donut center:
        donut_matrix[w_width-p_width:w_width+p_width+1,
                     w_width-p_width:w_width+p_width+1] = 0
        # remove horizontal and vertical parts
        donut_matrix[w_width,:] = 0
        donut_matrix[:, w_width] = 0

        values = donut_matrix[np.nonzero(donut_matrix)]

    elif what == 'vertical':
        values = np.concatenate([matrix[row-w_width:row-p_width,
                                  col-1:col+1+1].data,
                                 matrix[row+p_width+1:row+w_width+1,
                                  col-1:col+1+1].data])

    elif what == 'horizontal':
        values = np.concatenate([matrix[row-1:row+1+1,
                                  col-w_width:col-p_width].data,
                                 matrix[row-1:row+1+1,
                                  col+p_width+1:col+w_width+1].data])

    return values.sum()

def get_ratio_wrapper(args):
    return get_ratio_worker(*args)
    
def get_ratio_worker(triu_ma, csr_matrix, expected_ma, bin_size,
                     correction_factors, idx_array):

    print "Processing from {} to {}".format(min(idx_array), max(idx_array))
    #    for idx, pixel_value in enumerate(triu_ma.-wdata):
    transf_ma = np.zeros(len(idx_array))

    for idx in idx_array:
        # compute lower_left value
        row = triu_ma.row[idx]
        col = triu_ma.col[idx]

        transf_ma[idx-min(idx_array)] = compute_local_background_for_pixel(csr_matrix,
                                                                           expected_ma, row, col, correction_factors)

        """
        lower_left_mean = get_matrix_section_mean(csr_matrix, expected_ma, row, col,
                                                  bin_size, correction_factors, what='lower_left')
        donut_mean  = get_matrix_section_mean(csr_matrix, expected_ma, row, col,
                                              bin_size,  correction_factors, what='donut')
        horizontal_mean  = get_matrix_section_mean(csr_matrix, expected_ma, row, col,
                                                   bin_size, correction_factors, what='horizontal')
        vertical_mean  = get_matrix_section_mean(csr_matrix, expected_ma, row, col,
                                                 bin_size,  correction_factors, what='vertical')
                                                 


        transf_ma[idx-min(idx_array)] = float(pixel_value) / max(lower_left_mean, donut_mean,
                                                   horizontal_mean, vertical_mean)
        """
        if idx % 100 == 0:
            sys.stderr.write(".") #  print a . to show progress

    return transf_ma

def main(args):

    hicma = HiCMatrix.hiCMatrix(args.matrix)

    hicma.keepOnlyTheseChr(args.chromosome)

    if hicma.correction_factors is None:
        exit("matrix {} does not have correction factors. Iterative corrected matrix required.".format(args.matrix))

    # check that the matrix has bins of same size
    # otherwise try to adjust the bins to
    # to match a regular binning
    chrom, start, end, extra = zip(*hicma.cut_intervals)

    median = int(np.median(np.diff(start)))
    diff = np.array(end) - np.array(start)
    # check if the bin size is homogeneous
    if len(np.flatnonzero(diff != median)) > (len(diff) * 0.01):
        # set the start position of a bin to the closest multiple
        # of the median
        def snap_nearest_multiple(start_x, m):
            resi = [-1*(start_x % m), -start_x % m]
            return start_x + resi[np.argmin(np.abs(resi))]
        start = [snap_nearest_multiple(x, median) for x in start]
        end = [snap_nearest_multiple(x, median) for x in end]
        cut_intervals = zip(chrom, start, end, extra)
        sys.stderr.write('[getCountsByDistance] Bin size is not '
                         'homogeneous, setting \n'
                         'the bin distance to the median: {}\n'.format(median))

    # TODO make generic for all chromosomes
    # get counts by distance for chrX
    counts_by_distance = hicma.getCountsByDistance(per_chr=True)[args.chromosome]

    # construct expected matrix
    diagonals_array = []
    M = hicma.matrix.shape[0]
    for k in np.sort(counts_by_distance.keys()):
        diagonals_array.append(np.repeat(counts_by_distance[k].mean(), M))

    diagonals_array = np.vstack(diagonals_array)
    # the expected value matrix is not sparse but
    # the constructor is useful to add the diagonals
    # each containing the diagonal mean in each position.
    # In other words, the following line is a hack to
    # to convert rows in a matrix to diagonals.
    exp_mat = scipy.sparse.dia_matrix((diagonals_array, np.arange(0, len(diagonals_array))), shape=(M,M))

    # make the matrix symmetric
    exp_mat = exp_mat + scipy.sparse.triu(exp_mat, 1).T
    exp_mat = exp_mat.tocsr()
    import copy
    exp_mat_obj = copy.copy(hicma)
    exp_mat_obj.setMatrixValues(exp_mat)
    exp_mat_obj.maskBins(hicma.nan_bins)

    hicma.maskBins(hicma.nan_bins)

    # use only upper part of the matrix
    # and convert to coo
    triu_ma = scipy.sparse.triu(hicma.matrix, format='coo')

    global bin_size, w_width, p_width

    bin_size = hicma.getBinSize()
    #kb_20_in_bins = max(1, 20000/bin_size)
    #w_width = int(kb_20_in_bins * 8)
    #p_width =  max(1, int(kb_20_in_bins * 4))
    # for 25 kb
    w_width = 3
    p_width =  1

    #w_width = 5
    #p_width =  2

    #import ipdb;ipdb.set_trace()
    #compute_local_background_for_pixel(hicma.matrix, exp_mat, 463, 474, bin_size, hicma.correction_factors, what='lower_left')

    # matrix to hold the results (initially just an array)
    transf_ma = np.zeros(len(triu_ma.data))
#    import ipdb;ipb.set_trace()
    # this loop is to process o>nly pixels with data
    num_processors = args.numberOfProcessors
    pool = multiprocessing.Pool(num_processors)
    func = get_ratio_wrapper
    TASKS = []
    for idx_array in np.array_split(np.arange(len(triu_ma.data)), num_processors):
        TASKS.append((triu_ma, hicma.matrix, exp_mat_obj.matrix, bin_size, 
                      hicma.correction_factors, idx_array))

    if num_processors > 1:
        res = pool.map_async(func, TASKS).get(9999999)
    else:
        res = map(func, TASKS)
#    import ipdb;ipdb.set_trace()
    transf_ma = np.concatenate(res)
    # set the new values back into the original matrix
    if args.type == 'p-value':
        sys.stderr.write("computing FDR\n")
        #triu_ma.data = -np.log(_fdr(np.exp(-transf_ma)))
        transf_ma = np.exp(-transf_ma) * len(transf_ma)
        transf_ma[transf_ma > 1] = 1
        triu_ma.data = -np.log(transf_ma)

    else:
            triu_ma.data = transf_ma
    # fill the lower triangle
    triu_ma = triu_ma + scipy.sparse.triu(triu_ma, 1).T
    triu_ma = triu_ma.tocsr()
    triu_ma.eliminate_zeros()

    hicma.setMatrixValues(triu_ma)
    hicma.restoreMaskedBins()

    hicma.save(args.outFileName)

if __name__ == "__main__":
    ARGS = parse_argumentss()
    main(ARGS)
