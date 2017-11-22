#!/usr/bin/env python

from timeit import timeit


SETUP = """\
from benchmarking import (cluster_points_proposal,
                          cluster_points_original,
                          cluster_points_original_defaultdict)
from numpy.random import random

fragment = random(({points}, {dim}))
mu = random(({centers}, {dim}))

{gc_enable}
"""

POINTS = 10000
CENTERS = 10
DIM = 100

SIZE_RATIO = 100


def validate_algorithm(points, centers, dim):
    exec SETUP.format(
        points=points,
        centers=centers,
        dim=dim,
        gc_enable="")

    assert cluster_points_original(fragment, mu) == cluster_points_proposal(fragment, mu)


def perform_method(method, points, centers, dim, gc_enable=False, n_calls=1):
    return timeit(
        "\n".join(["cluster_points_%s(fragment, mu)" % method] * n_calls),
        setup=SETUP.format(
            points=points,
            centers=centers,
            dim=dim,
            gc_enable="gc.enable()\n" if gc_enable else ""),
        number=20
    )


if __name__ == "__main__":

    print "Checking algorithms . . ."
    validate_algorithm(POINTS, CENTERS, DIM)
    print " -> Done !"

    print
    print "Basic comparison: original vs proposal"
    print "######################################"

    original = perform_method("original", POINTS, CENTERS, DIM)
    proposal = perform_method("proposal", POINTS, CENTERS, DIM)

    print "Original: %f" % original
    print "Proposal: %f" % proposal

    print
    print "Defaultdict impact:"
    print "###################"

    original = perform_method("original", POINTS, CENTERS, DIM)
    o_ddict = perform_method("original_defaultdict", POINTS, CENTERS, DIM)

    print "Original (w/regular dict): %f" % original
    print "Original (w/ defaultdict): %f" % o_ddict

    print
    print "Impact of memory pressure (more executions, smaller fragment, gc enabled)"
    print "#########################################################################"

    original = perform_method("original", POINTS * SIZE_RATIO, CENTERS, DIM,
                              gc_enable=True)
    proposal = perform_method("proposal", POINTS, CENTERS, DIM,
                              gc_enable=True, n_calls=SIZE_RATIO)

    print "Original: %f" % original
    print "Proposal: %f" % proposal
