# -*- coding: utf-8 -*-

from .models import *
from .bayespy_constants import (
    DIST_GAUSSIAN_ARD, DIST_GAMMA, DIST_GAUSSIAN, DET_ADD)
import bayespy.plot as bpplt
from .utils import *

bn1 = BayesianNetwork.objects.first()
mu, tau, ui1 = bn1.nodes.all()
#
bn3 = BayesianNetwork.objects.get(name="bn3")
x1, x2 = bn3.nodes.get(name="x1"), bn3.nodes.get(name="x2")
z = bn3.nodes.get(name="z")

# # nodes_eos = []
nodes = bn3.nodes.all()
# # Initialize the dict {name: {django_model:, engine_object:}}
nodes_dict = {n.name: {"dm": n, "eo": None}
              for n in nodes}
# # Root nodes have no problem getting their engine object
root_nodes = {n.name:
                {
                    "dm": n,
                    "eo": n.get_engine_object(reconstruct=True)
                }
              for n in nodes if not n.parents()}
# # Child nodes are "intermediate" nodes and "final" ones - "leafs" in
# # trees
child_nodes = [n for n in nodes if n.parents()]

nodes_dict.update(root_nodes)

BayesianNetwork.update_eos_struct(nodes_dict, z)

bn4 = BayesianNetwork.objects.get(name="bn4")
# bn4.perform_inference(recalculate=True, save=True)
alpha = bn4.nodes.get(name="alpha")
Z = bn4.nodes.get(name="Z")
mu = bn4.nodes.get(name="mu")
Lambda = bn4.nodes.get(name="Lambda")
Y = bn4.nodes.get(name="Y")

y = Y.get_data()
Y_eo = bn4.get_engine_object()["Y"]
alpha_eo = bn4.get_engine_object()["alpha"]
Z_eo = bn4.get_engine_object()["alpha"]
mu_eo = bn4.get_engine_object()["mu"]
Lambda_eo = bn4.get_engine_object()["Lambda"]
# Q = bp.inference.VB(Y_eo, alpha_eo, Z_eo, mu_eo, Lambda_eo)
# Y_eo.observe(y)
# Q.update(repeat=1000)
# ##
# Z_new = bp.nodes.Categorical(alpha_eo)
# Z_new.initialize_from_random()
# Y_new = bp.nodes.Mixture(Z_new, bp.nodes.Gaussian, mu_eo, Lambda_eo)
# Y_new.observe([30.2, 29.8])
# Q_0 = bp.inference.VB(Z_new, Y_new, Y_eo, alpha_eo, Z_eo, mu_eo, Lambda_eo)
# Q_0.update(Z_new)
# print(Z_new.get_moments())

#print(bn4.assign_clusters_labels())
# print(bn4.assign_cluster([20, 22]))
# print(bn4.assign_cluster([30, 32]))

def plot():
    bpplt.pyplot.plot(y[:,0], y[:,1], 'rx')
    bpplt.gaussian_mixture_2d(Y_eo, alpha=alpha_eo, scale=2)
    bpplt.pyplot.show()

bn7 = BayesianNetwork.objects.get(name="Clustering (Example)")
# bn7.perform_inference(recalculate=True, save=True)
alpha1 = bn7.nodes.get(name="alpha")
Z1 = bn7.nodes.get(name="Z")
mu1 = bn7.nodes.get(name="mu")
Lambda1 = bn7.nodes.get(name="Lambda")
Y1 = bn7.nodes.get(name="Y")

# Inferred?
y1 = Y.get_data()
Y_eo1 = bn7.get_engine_object()["Y"]
alpha_eo1 = bn7.get_engine_object()["alpha"]
Z_eo1 = bn7.get_engine_object()["alpha"]
mu_eo1 = bn7.get_engine_object()["mu"]
Lambda_eo1 = bn7.get_engine_object()["Lambda"]

x = [1, 0]
y = [0, 1]
S1 = [[1, 0], [0, 1]]
print(mahalanobis_distance(x, y, S1))
