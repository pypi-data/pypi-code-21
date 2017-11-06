#!/usr/bin/env python

"""A class for handling HiC modeling."""

import os
import sys

import numpy
import mlpy

from hic_binning import dynamically_bin_cis_array
import libraries._modeling as _modeling

class ThreeDModel(object):
    """
    This class handles the creation of 3D models based on HiC data, including learning parameters,
    exporting coordinates into JSON format.
    """

    def __init__(self, hic, chrom, start=None, stop=None, binsize=10000, method='poisson', max_iterations=1000,
                 silent=False):
        """Create a 3D model using the specified algorithmic approach."""
        self.silent = silent
        if chrom not in hic.chr2int:
            if not self.silent:
                print >> sys.stderr, ("Chromosome name not found in HiC project.\n"),
            return None
        self.method = method
        if method not in ['poisson']:
            if not self.silent:
                print >> sys.stderr, ("Method name not recognized.\n"),
            return None
        chrint = hic.chr2int[chrom]
        start_fend = hic.fends['chr_indices'][chrint]
        stop_fend = hic.fends['chr_indices'][chrint]
        if start is None:
            while start_fend < stop_fend and hic.filter[start_fend] == 0:
                start_fend += 1
            start = hic.fends['fends']['mid'][start_fend]
        if stop is None:
            while stop_fend > start_fend and hic.filter[stop_fend - 1] == 0:
                stop_fend -= 1
        self.start = start
        self.stop = stop
        self.chrom = chrom
        self.binsize = binsize
        if method == 'poisson':
            self._learn_poisson_model(hic, max_iterations)
        return None

    def _learn_poisson_model(self, hic, max_iterations=1000):
        data, mapping = hic.cis_heatmap(self.chrom, start=self.start, stop=self.stop, binsize=self.binsize,
                                               datatype='fend', arraytype='upper', returnmapping=True)
        self.positions = (mapping[:, 0] + mapping[:, 1]) / 2
        binned_data = numpy.copy(data)
        dynamically_bin_cis_array(data, mapping, binned_data, mapping, minobservations=10)
        distances = numpy.zeros((mapping.shape[0], mapping.shape[0]), dtype=numpy.float32)
        indices = numpy.triu_indices(mapping.shape[0], 1)
        """
        distances[indices] = (binned_data[:, 0] / binned_data[:, 1]) ** -2.0
        distances[indices[1], indices[0]] = distances[indices]
        if not self.silent:
            print >> sys.stderr, ('Finding initial coordinate states...'),
        #coords = self.PCA(distances, 3)
        U, s, Vt = svd(distances, full_matrices=False)
        order = numpy.argsort(s)[::-1]
        U = U[:, order]
        s = s[order]
        Vt = Vt[:, order]
        PCAs = ((s**0.5) * Vt.T)[:3, :]
        coords = PCAs.dot(distances).T
        print coords.shape
        """
        distances[indices] = numpy.log(binned_data[:, 0] / binned_data[:, 1])
        distances[indices[1], indices[0]] = distances[indices]
        distances[numpy.arange(distances.shape[0]), numpy.arange(distances.shape[0])] = numpy.amax(distances[indices])
        distances -= numpy.mean(distances, axis=1).reshape(-1, 1)
        distances /= numpy.sqrt(numpy.sum(distances**2, axis=1)).reshape(-1, 1)
        pca_fast = mlpy.PCAFast(k=3)
        pca_fast.learn(distances)
        coords = pca_fast.transform(distances).astype(numpy.float32)
        if not self.silent:
            print >> sys.stderr, ('Done\nLearning coordinates...'),
        del binned_data
        distances = distances[indices]
        nonzero_indices = numpy.where(data[:, 0] > 0)[0].astype(numpy.int32)
        nonzero_indices0 = indices[0][nonzero_indices].astype(numpy.int32)
        nonzero_indices1 = indices[1][nonzero_indices].astype(numpy.int32)
        nonzero_counts = data[nonzero_indices, 0].astype(numpy.int32)
        nonzero_weights = data[nonzero_indices, 1].astype(numpy.float32)
        zero_indices = numpy.where(data[:, 0] == 0)[0].astype(numpy.int32)
        zero_indices0 = indices[0][zero_indices].astype(numpy.int32)
        zero_indices1 = indices[1][zero_indices].astype(numpy.int32)
        zero_weights = data[zero_indices, 1].astype(numpy.float32)
        del indices
        alpha = -3.0
        beta = 0.1
        new_coords = numpy.copy(coords)
        coord_grads = numpy.zeros(coords.shape, dtype=numpy.float64)
        param_grads = numpy.zeros(2, dtype=numpy.float64)
        _modeling.find_distances(coords, distances)
        nonzero_log_distances = numpy.log(distances[nonzero_indices]).astype(numpy.float32)
        start_cost = _modeling.find_poisson_cost(zero_indices,
                                                 zero_weights,
                                                 nonzero_indices,
                                                 nonzero_weights,
                                                 nonzero_counts,
                                                 nonzero_log_distances,
                                                 distances,
                                                 alpha,
                                                 beta)
        print start_cost
        cost = start_cost
        previous_cost = start_cost
        change = 0.0
        if max_iterations > 0:
            cont = True
        else:
            cont = False
        iteration = 0
        learningstep = 0.5
        while cont:
            """
            param_grads.fill(0.0)
            zero_log_distances = numpy.log(distances[zero_indices]).astype(numpy.float32)
            _modeling.calculate_poisson_param_gradients(zero_indices,
                                                        zero_weights,
                                                        zero_log_distances,
                                                        nonzero_indices,
                                                        nonzero_weights,
                                                        nonzero_counts,
                                                        nonzero_log_distances,
                                                        distances,
                                                        param_grads,
                                                        alpha,
                                                        beta)
            gradient_norm = numpy.sum(param_grads ** 2.0)
            # find best step size
            armijo = numpy.inf
            t = 1.0
            while armijo > 0.0:
                # if using multiple cores, pass gradients to root
                new_alpha = alpha - t * param_grads[0] / distances.shape[0]
                new_beta = beta - t * param_grads[1] / distances.shape[0]
                print param_grads, new_alpha, new_beta
                cost = _modeling.find_poisson_cost(zero_indices,
                                                   zero_weights,
                                                   nonzero_indices,
                                                   nonzero_weights,
                                                   nonzero_counts,
                                                   nonzero_log_distances,
                                                   distances,
                                                   new_alpha,
                                                   new_beta)
                armijo = cost - previous_cost + t * gradient_norm
                if not self.silent:
                    print >> sys.stderr, ("\r%s iteration:%ia cost:%f change:%f armijo: %f %s") %\
                                         ('Learning coordinates...', iteration, previous_cost,
                                          change, armijo, ' ' * 20),
                t *= learningstep
            previous_cost = cost
            alpha = new_alpha
            beta = new_beta
            if not self.silent:
                print >> sys.stderr, ("\r%s iteration:%ia cost:%f %s") %\
                                     ('Learning coordinates...', iteration, cost, ' ' * 40),
            """
            coord_grads.fill(0.0)
            _modeling.calculate_poisson_coord_gradients(zero_indices,
                                                        zero_indices0,
                                                        zero_indices1,
                                                        zero_weights,
                                                        nonzero_indices,
                                                        nonzero_indices0,
                                                        nonzero_indices1,
                                                        nonzero_weights,
                                                        nonzero_counts,
                                                        distances,
                                                        coords,
                                                        coord_grads,
                                                        alpha,
                                                        beta)
            gradient_norm = numpy.sum(coord_grads ** 2.0)
            print numpy.amin(numpy.abs(coord_grads)), numpy.amax(numpy.abs(coord_grads))
            # find best step size
            armijo = numpy.inf
            t = 1.0
            while armijo > 0.0:
                # if using multiple cores, pass gradients to root
                new_coords = (coords - t * coord_grads).astype(numpy.float32)
                print numpy.sum(numpy.abs(new_coords - coords))
                _modeling.find_distances(new_coords, distances)
                nonzero_log_distances = numpy.log(distances[nonzero_indices]).astype(numpy.float32)
                cost = _modeling.find_poisson_cost(zero_indices,
                                                   zero_weights,
                                                   nonzero_indices,
                                                   nonzero_weights,
                                                   nonzero_counts,
                                                   nonzero_log_distances,
                                                   distances,
                                                   alpha,
                                                   beta)
                armijo = cost - previous_cost + t * gradient_norm
                if not self.silent:
                    print >> sys.stderr, ("\r%s iteration:%ib cost:%f change:%f armijo: %f %s") %\
                                         ('Learning coodrinates...', iteration, previous_cost,
                                          change, armijo, ' ' * 20),
                t *= learningstep
                armijo = -numpy.inf
            previous_cost = cost
            coords = new_coords
            if not self.silent:
                print >> sys.stderr, ("\r%s iteration:%ib cost:%f %s") %\
                                     ('Learning cooordinates...', iteration, cost, ' ' * 40),
            iteration += 1
            if iteration >= max_iterations:
                cont = False
        self.coords = coords
        self.alpha = alpha
        self.beta = beta
        self.coords /= numpy.mean(distances) / 100.0
        self.coords -= numpy.mean(self.coords, axis=0).reshape(1, -1)
        if not self.silent:
            print >> sys.stderr, ("\r%s\tLearning coordinates... Final cost: %f\n") % (" " * 80, cost),
        return None

    def PCA(self, data, k):
        assert len(data.shape) == 2, "Data must be 2D"
        m, n = data.shape
        means = numpy.mean(data, axis=0)
        scatter_matrix = numpy.sum((data.reshape(m, 1, n) - means.reshape(1, 1, n)) *
                                   (data.reshape(m, n, 1) - means.reshape(1, n, 1)), axis=0)
        eig_val, eig_vec = numpy.linalg.eig(scatter_matrix)
        order = numpy.argsort(eig_val)[::-1]
        eig_vec = eig_vec[:, order[:k]]
        new_data = eig_vec.T.dot(data)
        return new_data.astype(numpy.float32).T

    def export_json(self, fname):
        output = open(fname, 'w')
        print >> output, "var DNA = {"
        print >> output, "\tnum_points:%i," % self.positions.shape[0]
        print >> output, "\tpositions:["
        for i in range(self.coords.shape[0]):
            if i < self.coords.shape[0] - 1:
                print >> output, "\t\t%i," % self.positions[i]
            else:
                print >> output, "\t\t%i" % self.positions[i]
        print >> output, "\t\t],\n\tcoordinates:["
        for i in range(self.coords.shape[0]):
            if i < self.coords.shape[0] - 1:
                print >> output, "\t\tnew THREE.Vector3(%f, %f, %f)," % (self.coords[i, 0],
                                 self.coords[i, 1], self.coords[i, 2])
            else:
                print >> output, "\t\tnew THREE.Vector3(%f, %f, %f)" % (self.coords[i, 0],
                                 self.coords[i, 1], self.coords[i, 2])
        print >> output, "\t]\n};"
        output.close()
        return None
