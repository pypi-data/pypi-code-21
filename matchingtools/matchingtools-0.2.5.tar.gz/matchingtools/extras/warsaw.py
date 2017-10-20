"""
This module defines a basis of operators for the Standar Model
effective lagrangian up to dimension 6. 


The basis is the one in arXiv:1412.8480v2_.

.. _arXiv:1412.8480v2: https://arxiv.org/abs/1412.8480v2.
"""

from fractions import Fraction

from matchingtools.core import (
    tensor_op, flavor_tensor_op, D, Op, OpSum, i_op, number_op)

from matchingtools.extras.SM import (
    phi, phic, lL, lLc, eR, eRc, qL, qLc, uR, uRc, dR, dRc, bFS, wFS, gFS,
    ye, yec, yd, ydc, yu, yuc, V, Vc, mu2phi, lambdaphi)

from matchingtools.extras.SU2 import epsSU2, sigmaSU2, epsSU2triplets

from matchingtools.extras.SU3 import epsSU3, TSU3, fSU3

from matchingtools.extras.Lorentz import (
    epsUp, epsUpDot, epsDown, epsDownDot, sigma4, sigma4bar,
    eps4, sigmaTensor)

# -- Standard Model dimension 4 operators --

Qkinphi = tensor_op("Qkinphi")
r"""
Higgs kinetic term
:math:`Q_{kin,\phi} = (D_\mu \phi)^\dagger D^\mu \phi`.
"""

Qphi4 = tensor_op("Qphi4")
r"""
Higgs quartic coupling
:math:`Q_{\phi 4} = (\phi^\dagger\phi)^2`.
"""

Qphi2 = tensor_op("Qphi2")
r"""
Higgs quadratic coupling
:math:`Q_{\phi 2} = \phi^\dagger\phi`.
"""

Qye = flavor_tensor_op("Qye")
r"""
Lepton Yukawa coupling
:math:`(Q_{y^e})_{ij} = \bar{l}_{Li}\phi e_{Rj}`.
"""

Qyec = flavor_tensor_op("Qyec")
r"""
Conjugate lepton Yukawa coupling
:math:`(Q_{y^e})^*_{ij} = \bar{e}_{Rj}\phi^\dagger l_{Li}`.
"""

Qyd = flavor_tensor_op("Qyd")
r"""
Down quark Yukawa coupling
:math:`(Q_{y^d})_{ij} = \bar{q}_{Li}\phi d_{Rj}`.
"""

Qydc = flavor_tensor_op("Qydc")
r"""
Conjugate down quark Yukawa coupling
:math:`(Q_{y^d})^*_{ij} = \bar{d}_{Rj}\phi^\dagger q_{Li}`.
"""

Qyu = flavor_tensor_op("Qyu")
r"""
Up quark Yukawa coupling
:math:`(Q_{y^u})_{ij} = \bar{q}_{Li}\tilde{\phi} u_{Rj}`.
"""

Qyuc = flavor_tensor_op("Qyuc")
r"""
Conjugate up quark Yukawa coupling
:math:`(Q_{y^d})^*_{ij} = 
\bar{d}_{Rj}\tilde{\phi}^\dagger q_{Li}`.
"""

# -- Standard Model dimension 5 operators --

Q5 = flavor_tensor_op("Q5")
r"""
Weinberg operator
:math:`Q_5 = 
\overline{l^c}_L\tilde{\phi}^*\tilde{\phi}^\dagger l_L`.
"""

Q5c = flavor_tensor_op("Q5c")
r"""
Conjugate Weinberg operator
:math:`Q_5 = 
\bar{l}_L\tilde{\phi}\tilde{\phi}^T l^c_L`.
"""

# -- Standard Model dimension 6 four-fermion operators --

# *** LLLL ***

Qll = flavor_tensor_op("Qll")
r"""
LLLL type four-fermion operator
:math:`(Q_{ll})_{ijkl}=
(\bar{l}_{Li}\gamma_\mu l_{Lj})
(\bar{l}_{Lk}\gamma^\mu l_{Ll})`.
"""

Q1qq = flavor_tensor_op("Q1qq")
r"""
LLLL type four-fermion operator
:math:`(Q^{(1)}_{qq})_{ijkl}=
(\bar{q}_{Li}\gamma_\mu q_{Lj})
(\bar{q}_{Lk}\gamma^\mu q_{Ll})`.
"""

Q3qq = flavor_tensor_op("Q3qq")
r"""
LLLL type four-fermion operator 
:math:`(Q^{(3)}_{qq})_{ijkl}=
(\bar{q}_{Li}\sigma_a \gamma_\mu q_{Lj})
(\bar{q}_{Lk}\sigma_a \gamma^\mu q_{Ll})`.
"""

Q1lq = flavor_tensor_op("Q1lq")
r"""
LLLL type four-fermion operator
:math:`(Q^{(1)}_{lq})_{ijkl}=
(\bar{l}_{Li}\gamma_\mu l_{Lj})
(\bar{q}_{Lk}\gamma^\mu q_{Ll})`.
"""

Q3lq = flavor_tensor_op("Q3lq")
r"""
LLLL type four-fermion operator
:math:`(Q^{(3)}_{lq})_{ijkl}=
(\bar{l}_{Li}\sigma_a \gamma_\mu l_{Lj})
(\bar{q}_{Lk}\sigma_a \gamma^\mu q_{Ll})`.
"""

# *** RRRR ***

Qee = flavor_tensor_op("Qee")
r"""
RRRR type four-fermion operator
:math:`(Q_{ee})_{ijkl}=
(\bar{e}_{Ri}\gamma_\mu e_{Rj})
(\bar{e}_{Rk}\gamma^\mu e_{Rl})`.
"""

Quu = flavor_tensor_op("Quu")
r"""
RRRR type four-fermion operator
:math:`(Q_{uu})_{ijkl}=
(\bar{u}_{Ri}\gamma_\mu u_{Rj})
(\bar{u}_{Rk}\gamma^\mu u_{Rl})`.
"""

Qdd = flavor_tensor_op("Qdd")
r"""
RRRR type four-fermion operator
:math:`(Q_{dd})_{ijkl}=
(\bar{d}_{Ri}\gamma_\mu d_{Rj})
(\bar{d}_{Rk}\gamma^\mu d_{Rl})`.
"""

Q1ud = flavor_tensor_op("Q1ud")
r"""
RRRR type four-fermion operator
:math:`(Q^{(1)}_{ud})_{ijkl}=
(\bar{u}_{Ri}\gamma_\mu u_{Rj})
(\bar{d}_{Rk}\gamma^\mu d_{Rl})`.
"""

Q8ud = flavor_tensor_op("Q8ud")
r"""
RRRR type four-fermion operator
:math:`(Q^{(8)}_{ud})_{ijkl}=
(\bar{u}_{Ri}T_A \gamma_\mu u_{Rj})
(\bar{d}_{Rk}T_A \gamma^\mu d_{Rl})`.
"""

Qeu = flavor_tensor_op("Qeu")
r"""
RRRR type four-fermion operator
:math:`(Q_{eu})_{ijkl}=
(\bar{e}_{Ri}\gamma_\mu e_{Rj})
(\bar{u}_{Rk}\gamma^\mu u_{Rl})`.
"""

Qed = flavor_tensor_op("Qed")
r"""
RRRR type four-fermion operator
:math:`(Q_{ed})_{ijkl}=
(\bar{e}_{Ri}\gamma_\mu e_{Rj})
(\bar{d}_{Rk}\gamma^\mu d_{Rl})`.
"""

# *** LLRR and LRRL ***

Qle = flavor_tensor_op("Qle")
r"""
LLRR type four-fermion operator
:math:`(Q_{le})_{ijkl}=
(\bar{l}_{Li}\gamma_\mu l_{Lj})
(\bar{e}_{Rk}\gamma^\mu e_{Rl})`.
"""

Qqe = flavor_tensor_op("Qqe")
r"""
LLRR type four-fermion operator
:math:`(Q_{qe})_{ijkl}=
(\bar{q}_{Li}\gamma_\mu q_{Lj})
(\bar{e}_{Rk}\gamma^\mu e_{Rl})`.
"""

Qlu = flavor_tensor_op("Qlu")
r"""
LLRR type four-fermion operator
:math:`(Q_{lu})_{ijkl}=
(\bar{l}_{Li}\gamma_\mu l_{Lj})
(\bar{u}_{Rk}\gamma^\mu u_{Rl})`.
"""

Qld = flavor_tensor_op("Qld")
r"""
LLRR type four-fermion operator
:math:`(Q_{ld})_{ijkl}=
(\bar{l}_{Li}\gamma_\mu l_{Lj})
(\bar{d}_{Rk}\gamma^\mu d_{Rl})`.
"""

Q1qu = flavor_tensor_op("Q1qu")
r"""
LLRR type four-fermion operator
:math:`(Q^{(1)}_{qu})_{ijkl}=
(\bar{q}_{Li}\gamma_\mu q_{Lj})
(\bar{u}_{Rk}\gamma^\mu u_{Rl})`.
"""

Q8qu = flavor_tensor_op("Q8qu")
r"""
LLRR type four-fermion operator
:math:`(Q^{(8)}_{qu})_{ijkl}=
(\bar{q}_{Li}T_A\gamma_\mu q_{Lj})
(\bar{u}_{Rk}T_A\gamma^\mu u_{Rl})`.
"""

Q1qd = flavor_tensor_op("Q1qd")
r"""
LLRR type four-fermion operator
:math:`(Q^{(1)}_{qd})_{ijkl}=
(\bar{q}_{Li}\gamma_\mu q_{Lj})
(\bar{d}_{Rk}\gamma^\mu d_{Rl})`.
"""

Q8qd = flavor_tensor_op("Q8qd")
r"""
LLRR type four-fermion operator
:math:`(Q^{(8)}_{qd})_{ijkl}=
(\bar{q}_{Li}T_A\gamma_\mu q_{Lj})
(\bar{d}_{Rk}T_A\gamma^\mu d_{Rl})`.
"""

Qledq = flavor_tensor_op("Qledq")
r"""
LRRL type four-fermion operator
:math:`(Q_{leqd})_{ijkl}=
(\bar{l}_{Li} e_{Rj})
(\bar{d}_{Rk} q_{Ll})`.
"""

Qledqc = flavor_tensor_op("Qledqc")
r"""
LRRL type four-fermion operator
:math:`(Q_{leqd})^*_{ijkl}=
(\bar{e}_{Rj} l_{Li})
(\bar{q}_{Ll} d_{Rk})`.
"""

# *** LRLR ***

Q1quqd = flavor_tensor_op("Q1quqd")
r"""
LRLR type four-fermion operator
:math:`(Q^{(1)}_{quqd})_{ijkl}=
(\bar{q}_{Li} u_{Rj})i\sigma_2
(\bar{q}_{Lk} d_{Rl})^T`.
"""

Q1quqdc = flavor_tensor_op("Q1quqdc")
r"""
LRLR type four-fermion operator
:math:`(Q^{(1)}_{quqd})^*_{ijkl}=
(\bar{u}_{Rj} q_{Li})i\sigma_2
(\bar{d}_{Rl} q_{Lk})^T`.
"""

Q8quqd = flavor_tensor_op("Q8quqd")
r"""
LRLR type four-fermion operator
:math:`(Q^{(8)}_{quqd})_{ijkl}=
(\bar{q}_{Li}T_A u_{Rj})i\sigma_2
(\bar{q}_{Lk}T_A d_{Rl})^T`.
"""

Q8quqdc = flavor_tensor_op("Q8quqdc")
r"""
LRLR type four-fermion operator
:math:`(Q^{(8)}_{quqd})^*_{ijkl}=
(\bar{u}_{Rj} T_A q_{Li})i\sigma_2
(\bar{d}_{Rl} T_A q_{Lk}})^T`.
"""

Q1lequ = flavor_tensor_op("Q1lequ")
r"""
LRLR type four-fermion operator
:math:`(Q^{(1)}_{lequ})_{ijkl}=
(\bar{l}_{Li} e_{Rj}) i\sigma_2
(\bar{q}_{Lk} u_{Rl})^T`.
"""

Q3lequ = flavor_tensor_op("Q1lequ")
r"""
LRLR type four-fermion operator
:math:`(Q^{(3)}_{lequ})_{ijkl}=
(\bar{l}_{Li} \sigma_{\mu\nu} e_{Rj}) i\sigma_2
(\bar{q}_{Lk} \sigma_{\mu\nu} u_{Rl})^T`.
"""

Q1lequc = flavor_tensor_op("Q1lequc")
r"""
LRLR type four-fermion operator
:math:`(Q^{(1)}_{lequ})^*_{ijkl}`
"""

Q3lequc = flavor_tensor_op("Q3lequc")
r"""
LRLR type four-fermion operator
:math:`(Q^{(3)}_{lequ})^*_{ijkl}`
"""

# *** \slashed{B} and slashed{L} ***

Qduq = flavor_tensor_op("Qduq")
r"""
Four-fermion operator
:math:`(Q_{duq})_{ijkl}=
\epsilon_{ABC}
(\bar{d}^B_{Rk} u^{c,C}_{Rl})
(q^{c,A}_{Lj} i\sigma_2 \bar{l}_{Li}).`
"""

Qduqc = flavor_tensor_op("Qduqc")
r"""
Four-fermion operator :math:`(Q_{duq})^*_{ijkl}`
"""

Qqqu = flavor_tensor_op("Qqqu")
r"""
Four-fermion operator
:math:`(Q_{qqu})_{ijkl}=
\epsilon_{ABC}(\bar{q}^A_{Li} i\sigma_2 q^{c,B}_{Lj})
(u^{c,C}_{Rl} \bar{e}_{Rk})`.
"""

Qqquc = flavor_tensor_op("Qqquc")
r"""
Four-fermion operator
:math:`(Q_{qqu})^*_{ijkl}`.
"""

Q1qqq = flavor_tensor_op("Q1qqq")
r"""
Four-fermion operator
:math:`(Q^{{(1)}}_{qqq})_{ijkl}=
\epsilon_{ABC}
(\bar{q}^A_{Lk} i\sigma_2 q^{c,B}_{Ll})
(\bar{l}_{Li} i\sigma_2 q^{c,C}_{Lj})`.
"""

Q1qqqc = flavor_tensor_op("Q1qqqc")
r"""
Four-fermion operator
:math:`(Q^{{(1)}}_{qqq})^*_{ijkl}`
"""

Q3qqq = flavor_tensor_op("Q3qqq")
r"""
Four-fermion operator
:math:`(Q^{{(3)}}_{qqq})_{ijkl}=
\epsilon_{ABC}
(\bar{q}^A_{Lk} sigma_a i\sigma_2 q^{c,B}_{Ll})
(\bar{l}_{Li} sigma_a i\sigma_2 q^{c,C}_{Lj})`.
"""

Q3qqqc = flavor_tensor_op("Q3qqqc")
r"""
Four-fermion operator
:math:`(Q^{{(3)}}_{qqq})^*_{ijkl}`
"""

Qduu = flavor_tensor_op("Qduu")
r"""
Four-fermion operator
:math:`(Q_{duu})_{ijkl}=
\epsilon_{ABC}
(d^{c,A}_{Rj}) \bar{u}^B_{Ri})
(u^{c,C}_{Rl}) \bar{e}_{Rk})`.
"""

Qduuc = flavor_tensor_op("Qduuc")
r"""
Four-fermion operator
:math:`(Q_{duu})^*_{ijkl}`.
"""

# -- Standard Model dimension six operators other than four-fermion --

# *** S ***

Qphisq = tensor_op("Qphisq")
r"""
S type operator
:math:`Q_{\phi\square}=\phi^\dagger\phi\square(\phi^\dagger\phi)`.
"""

Qphi = tensor_op("Qphi")
r"""
S type six Higgs interaction operator
:math:`Q_\phi = (\phi^\dagger\phi)^3`.
"""

# *** SVF ***

Q1phil = flavor_tensor_op("Q1phil")
r"""
SVF type operator :math:`(Q^{(1)}_{\phi l})_{ij}=
(\phi^\dagger i \overset{\leftrightarrow{D}}_\mu \phi)
(\bar{l}_{Li}\gamma^\mu l_{Lj})`.
"""

Q1phiq = flavor_tensor_op("Q1phiq")
r"""
SVF type operator :math:`(Q^{(1)}_{\phi q})_{ij}=
(\phi^\dagger i \overset{\leftrightarrow{D}}_\mu \phi)
(\bar{q}_{Li}\gamma^\mu q_{Lj})`.
"""

Q3phil = flavor_tensor_op("Q3phil")
r"""
SVF type operator :math:`(Q^{(3)}_{\phi l})_{ij}=
(\phi^\dagger i \overset{\leftrightarrow{D}}^a_\mu \phi)
(\bar{l}_{Li} \sigma_a \gamma^\mu l_{Lj})`.
"""

Q3phiq = flavor_tensor_op("Q3phiq")
r"""
SVF type operator :math:`(Q^{(3)}_{\phi q})_{ij}=
(\phi^\dagger i \overset{\leftrightarrow{D}}^a_\mu \phi)
(\bar{q}_{Li} \sigma_a \gamma^\mu q_{Lj})`.
"""

Q1phie = flavor_tensor_op("Q1phie")
r"""
SVF type operator :math:`(Q^{(1)}_{\phi e})_{ij}=
(\phi^\dagger i \overset{\leftrightarrow{D}}_\mu \phi)
(\bar{e}_{Ri}\gamma^\mu e_{Rj})`.
"""

Q1phid = flavor_tensor_op("Q1phid")
r"""
SVF type operator :math:`(Q^{(1)}_{\phi d})_{ij}=
(\phi^\dagger i \overset{\leftrightarrow{D}}_\mu \phi)
(\bar{d}_{Ri}\gamma^\mu d_{Rj})`.
"""

Q1phiu = flavor_tensor_op("Q1phiu")
r"""
SVF type operator :math:`(Q^{(1)}_{\phi u})_{ij}=
(\phi^\dagger i \overset{\leftrightarrow{D}}_\mu \phi)
(\bar{u}_{Ri}\gamma^\mu u_{Rj})`.
"""

Qphiud = flavor_tensor_op("Qphiud")
r"""
SVF type operator :math:`(Q^{(1)}_{\phi ud})_{ij}=
(\tilde{\phi}^\dagger i \overset{\leftrightarrow{D}}_\mu \phi)
(\bar{u}_{Ri}\gamma^\mu d_{Rj})`.
"""

# *** STF ***

QeB = flavor_tensor_op("QeB")
r"""
STF type operator :math:`(Q_{eB})_{ij}=
(\bar{l}_{Li}\sigma^{\mu\nu}e_{Rj})\phi B_{\mu\nu}`.
"""

QeBc = flavor_tensor_op("QeBc")
r"""
STF type operator :math:`(Q_{eB})^*_{ij}=
\phi^\dagger (\bar{e}_{Rj}\sigma^{\mu\nu}l_{Li}) B_{\mu\nu}`.
"""

QeW = flavor_tensor_op("QeW")
r"""
STF type operator :math:`(Q_{eW})_{ij}=
(\bar{l}_{Li}\sigma^{\mu\nu}e_{Rj})\sigma^a\phi W^a_{\mu\nu}`.
"""

QeWc = flavor_tensor_op("QeWc")
r"""
STF type operator :math:`(Q_{eW})^*_{ij}=
\phi^\dagger\sigma^a(\bar{e}_{Rj}\sigma^{\mu\nu}l_{Li}) W^a_{\mu\nu}`.
"""

QuB = flavor_tensor_op("QuB")
r"""
STF type operator :math:`(Q_{uB})_{ij}=
(\bar{q}_{Li}\sigma^{\mu\nu}u_{Rj})\tilde{\phi} B_{\mu\nu}`.
"""

QuBc = flavor_tensor_op("QuBc")
r"""
STF type operator :math:`(Q_{uB})^*_{ij}=
\tilde{\phi}^\dagger(\bar{u}_{Rj}\sigma^{\mu\nu}q_{Li}) B_{\mu\nu}`.
"""

QuW = flavor_tensor_op("QuW")
r"""
STF type operator :math:`(Q_{uW})_{ij}=
(\bar{q}_{Li}\sigma^{\mu\nu}u_{Rj})\sigma^a\tilde{\phi} W^a_{\mu\nu}`.
"""

QuWc = flavor_tensor_op("QuWc")
r"""
STF type operator :math:`(Q_{uW})^*_{ij}=
\tilde{\phi}\sigma^a(\bar{u}_{Rj}\sigma^{\mu\nu}q_{Li}) W^a_{\mu\nu}`.
"""

QdB = flavor_tensor_op("QdB")
r"""
STF type operator :math:`(Q_{dB})_{ij}=
(\bar{q}_{Li}\sigma^{\mu\nu}d_{Rj})\phi B_{\mu\nu}`.
"""

QdBc = flavor_tensor_op("QdBc")
r"""
STF type operator :math:`(Q_{dB})^*_{ij}=
\phi^\dagger(\bar{d}_{Rj}\sigma^{\mu\nu}q_{Li}) B_{\mu\nu}`.
"""

QdW = flavor_tensor_op("QdW")
r"""
STF type operator :math:`(Q_{dW})_{ij}=
(\bar{q}_{Li}\sigma^{\mu\nu}d_{Rj})\sigma^a\phi W^a_{\mu\nu}`.
"""

QdWc = flavor_tensor_op("QdWc")
r"""
STF type operator :math:`(Q_{dW})^*_{ij}=
\phi^\dagger\sigma^a(\bar{d}_{Rj}\sigma^{\mu\nu}q_{Li}) W^a_{\mu\nu}`.
"""

QuG = flavor_tensor_op("QuG")
r"""
STF type operator :math:`(Q_{uG})_{ij}=
(\bar{q}_{Li}\sigma^{\mu\nu}T_A u_{Rj})\tilde{\phi} G^A_{\mu\nu}`.
"""

QuGc = flavor_tensor_op("QuGc")
r"""
STF type operator :math:`(Q_{uG})^*_{ij}=
\tilde{\phi}^\dagger(\bar{u}_{Rj}\sigma^{\mu\nu}T_A q_{Li}) G^A_{\mu\nu}`.
"""

QdG = flavor_tensor_op("QdG")
r"""
STF type operator :math:`(Q_{dG})_{ij}=
(\bar{q}_{Li}\sigma^{\mu\nu}T_A d_{Rj})\phi G^A_{\mu\nu}`.
"""

QdGc = flavor_tensor_op("QdGc")
r"""
STF type operator :math:`(Q_{dG})^*_{ij}=
\phi^\dagger(\bar{d}_{Rj}\sigma^{\mu\nu}T_A q_{Li}) G^A_{\mu\nu}`.
"""

# *** SF ***

Qephi = flavor_tensor_op("Qephi")
r"""
SF type operator :math:`(Q_{e\phi})_{ij}=
(\phi^\dagger\phi)(\bar{l}_{Li}\phi e_{Rj})`.
"""

Qdphi = flavor_tensor_op("Qdphi")
r"""
SF type operator :math:`(Q_{d\phi})_{ij}=
(\phi^\dagger\phi)(\bar{q}_{Li}\phi d_{Rj})`.
"""

Quphi = flavor_tensor_op("Quphi")
r"""
SF type operator :math:`(Q_{u\phi})_{ij}=
(\phi^\dagger\phi)(\bar{q}_{Li}\tilde{\phi} u_{Rj})`.
"""

Qephic = flavor_tensor_op("Qephic")
r"""
SF type operator :math:`(Q_{e\phi})^*_{ij}=
(\phi^\dagger\phi)(\bar{e}_{Rj}\phi^\dagger l_{Li})`.
"""

Qdphic = flavor_tensor_op("Qdphic")
r"""
SF type operator :math:`(Q_{d\phi})^*_{ij}=
(\phi^\dagger\phi)(\bar{d}_{Rj}\phi^\dagger q_{Li})`.
"""

Quphic = flavor_tensor_op("Quphic")
r"""
SF type operator :math:`(Q_{u\phi})^*_{ij}=
(\phi^\dagger\phi)(\bar{u}_{Rj}\tilde{\phi}^\dagger q_{Li})`.
"""

# *** Qblique ***

QphiD = tensor_op("QphiD")
r"""
Qblique operator :math:`Q_{\phi D}=(\phi^\dagger D_\mu \phi)((D^\mu\phi)^\dagger\phi)`.
"""

Qphi = tensor_op("Qphi")
"""
Six-Higgs operator `Q_{\phi} = \left(\phi^\dagger \phi\right)^2`.
"""

QphiB = tensor_op("QphiB")
r"""
Qblique operator 
:math:`Q_{\phi B}=\phi^\dagger\phi B_{\mu\nu}B^{\mu\nu}`.
"""

QphiBTilde = tensor_op("QphiBTilde")
r"""
Qblique operator 
:math:`Q_{\phi \tilde{B}}=
\phi^\dagger\phi \tilde{B}_{\mu\nu}B^{\mu\nu}`.
"""

QphiW = tensor_op("QphiW")
r"""
Qblique operator 
:math:`Q_{\phi W}=
\phi^\dagger\phi W^a_{\mu\nu}W^{a,\mu\nu}`.
"""

QphiWTilde = tensor_op("QphiWTilde")
r"""
Qblique operator 
:math:`Q_{\phi \tilde{W}}=
\phi^\dagger\phi \tilde{W}^a_{\mu\nu}W^{a,\mu\nu}`.
"""

QWB = tensor_op("QWB")
r"""
Qblique operator 
:math:`Q_{W B}=
\phi^\dagger\sigma^a\phi W^a_{\mu\nu}B^{\mu\nu}`.
"""

QWBTilde = tensor_op("QWBTilde")
r"""
Qblique operator 
:math:`Q_{\tilde{W} B}=
\phi^\dagger\sigma^a\phi \tilde{W}^a_{\mu\nu}B^{\mu\nu}`.
"""

QphiG = tensor_op("QphiG")
r"""
Qblique operator 
:math:`Q_{\phi W}=
\phi^\dagger\phi G^A_{\mu\nu}G^{A,\mu\nu}`.
"""

QphiGTilde = tensor_op("QphiGTilde")
r"""
Qblique operator 
:math:`Q_{\phi \tilde{W}}=
\phi^\dagger\phi \tilde{G}^A_{\mu\nu}G^{A,\mu\nu}`.
"""

# *** Gauge ***

QW = tensor_op("QW")
r"""
Gauge type operator
:math:`Q_W=
\varepsilon_{abc}W^{a,\nu}_\mu W^{b,\rho}_\nu W^{c,\mu}_\rho`.
"""

QWTilde = tensor_op("QWTilde")
r"""
Gauge type operator
:math:`Q_{\tilde{W}}=
\varepsilon_{abc}\tilde{W}^{a,\nu}_\mu
W^{b,\rho}_\nu W^{c,\mu}_\rho`.
"""

QG = tensor_op("QG")
r"""
Gauge type operator
:math:`Q_G=
f_{ABC}G^{A,\nu}_\mu G^{B,\rho}_\nu G^{C,\mu}_\rho`.
"""

QGTilde = tensor_op("QGTilde")
r"""
Gauge type operator
:math:`Q_{\tilde{G}}=
f_{ABC}\tilde{G}^{A,\nu}_\mu
G^{B,\rho}_\nu G^{C,\mu}_\rho`.
"""

rules_basis_defs_dim_6_5 = [
    
    # Standard Model dimension 6 four-fermion operators

    # LLLL type
    
    (Op(lLc(0, 1, -1), sigma4bar(2, 0, 3), lL(3, 1, -2),
        lLc(4, 5, -3), sigma4bar(2, 4, 6), lL(6, 5, -4)),
     OpSum(Qll(-1, -2, -3, -4))),

    (Op(qLc(0, 1, 2, -1), sigma4bar(3, 0, 4), qL(4, 1, 2, -2),
        qLc(5, 6, 7, -3), sigma4bar(3, 5, 8), qL(8, 6, 7, -4)),
     OpSum(Q1qq(-1, -2, -3, -4))),

    (Op(qLc(0, 1, 2, -1), sigmaSU2(9, 2, 10),
        sigma4bar(3, 0, 4), qL(4, 1, 10, -2),
        qLc(5, 6, 7, -3), sigmaSU2(9, 7, 11),
        sigma4bar(3, 5, 8), qL(8, 6, 11, -4)),
     OpSum(Q3qq(-1, -2, -3, -4))),

    (Op(lLc(0, 1, -1), sigma4bar(2, 0, 3), lL(3, 1, -2),
        qLc(4, 5, 6, -3), sigma4bar(2, 4, 7), qL(7, 5, 6, -4)),
     OpSum(Q1lq(-1, -2, -3, -4))),

    (Op(lLc(0, 1, -1), sigma4bar(2, 0, 3),
        sigmaSU2(4, 1, 5), lL(3, 5, -2),
        qLc(6, 7, 8, -3), sigma4bar(2, 6, 9),
        sigmaSU2(4, 8, 10), qL(9, 7, 10, -4)),
     OpSum(Q3lq(-1, -2, -3, -4))),

    # RRRR type

    (Op(eRc(0, -1), sigma4(1, 0, 2), eR(2, -2),
        eRc(3, -3), sigma4(1, 3, 4), eR(4, -4)),
     OpSum(Qee(-1, -2, -3, -4))),

    (Op(uRc(0, 1, -1), sigma4(2, 0, 3), uR(3, 1, -2),
        uRc(4, 5, -3), sigma4(2, 4, 6), uR(6, 5, -4)),
     OpSum(Quu(-1, -2, -3, -4))),

    (Op(dRc(0, 1, -1), sigma4(2, 0, 3), dR(3, 1, -2),
        dRc(4, 5, -3), sigma4(2, 4, 6), dR(6, 5, -4)),
     OpSum(Qdd(-1, -2, -3, -4))),

    (Op(uRc(0, 1, -1), sigma4(2, 0, 3), uR(3, 1, -2),
        dRc(4, 5, -3), sigma4(2, 4, 6), dR(6, 5, -4)),
     OpSum(Q1ud(-1, -2, -3, -4))),

    (Op(uRc(0, 1, -1), sigma4(2, 0, 3),
        TSU3(4, 1, 5), uR(3, 5, -2),
        dRc(6, 7, -3), sigma4(2, 6, 8),
        TSU3(4, 7, 9), dR(8, 9, -4)),
     OpSum(Q8ud(-1, -2, -3, -4))), 
    
    (Op(eRc(0, -1), sigma4(2, 0, 3), eR(3, -2),
        uRc(4, 5, -3), sigma4(2, 4, 6), uR(6, 5, -4)),
     OpSum(Qeu(-1, -2, -3, -4))),
    
    (Op(eRc(0, -1), sigma4(2, 0, 3), eR(3, -2),
        dRc(4, 5, -3), sigma4(2, 4, 6), dR(6, 5, -4)),
     OpSum(Qed(-1, -2, -3, -4))),

    # LLRR and LRRL type

    (Op(lLc(0, 1, -1), sigma4bar(2, 0, 3), lL(3, 1, -2),
        eRc(4, -3), sigma4(2, 4, 5), eR(5, -4)),
     OpSum(Qle(-1, -2, -3, -4))),

    (Op(qLc(0, 1, 2, -1), sigma4bar(3, 0, 4), qL(4, 1, 2, -2),
        eRc(5, -3), sigma4(3, 5, 6), eR(6, -4)),
     OpSum(Qqe(-1, -2, -3, -4))),

    (Op(lLc(0, 1, -1), sigma4bar(2, 0, 3), lL(3, 1, -2),
        uRc(4, 5, -3), sigma4(2, 4, 6), uR(6, 5, -4)),
     OpSum(Qlu(-1, -2, -3, -4))),

    (Op(lLc(0, 1, -1), sigma4bar(2, 0, 3), lL(3, 1, -2),
        dRc(4, 5, -3), sigma4(2, 4, 6), dR(6, 5, -4)),
     OpSum(Qld(-1, -2, -3, -4))),

    (Op(qLc(0, 1, 2, -1), sigma4bar(3, 0, 4), qL(4, 1, 2, -2),
        uRc(5, 6, -3), sigma4(3, 5, 7), uR(7, 6, -4)),
     OpSum(Q1qu(-1, -2, -3, -4))),

    (Op(qLc(0, 1, 2, -1), sigma4bar(3, 0, 4),
        TSU3(5, 1, 6), qL(4, 6, 2, -2),
        uRc(7, 8, -3), sigma4(3, 7, 9),
        TSU3(5, 8, 10), uR(9, 10, -4)),
     OpSum(Q8qu(-1, -2, -3, -4))),
    
    (Op(qLc(0, 1, 2, -1), sigma4bar(3, 0, 4), qL(4, 1, 2, -2),
        dRc(5, 6, -3), sigma4(3, 5, 7), dR(7, 6, -4)),
     OpSum(Q1qd(-1, -2, -3, -4))),

    (Op(qLc(0, 1, 2, -1), sigma4bar(3, 0, 4),
        TSU3(5, 1, 6), qL(4, 6, 2, -2),
        dRc(7, 8, -3), sigma4(3, 7, 9),
        TSU3(5, 8, 10), dR(9, 10, -4)),
     OpSum(Q8qd(-1, -2, -3, -4))),

    (Op(lLc(0, 1, -1), eR(0, -2), dRc(2, 3, -3), qL(2, 3, 1, -4)),
     OpSum(Qledq(-1, -2, -3, -4))),

    (Op(eRc(0, -2), lL(0, 1, -1), qLc(2, 3, 1, -4), dR(2, 3, -3)),
     OpSum(Qledqc(-1, -2, -3, -4))),

    # LRLR type

    (Op(qLc(0, 1, 2, -1), uR(0, 1, -2), epsSU2(2, 3),
        qLc(4, 5, 3, -3), dR(4, 5, -4)),
     OpSum(Q1quqd(-1, -2, -3, -4))),

    (Op(uRc(0, 1, -2), qL(0, 1, 2, -1), epsSU2(2, 3),
        dRc(4, 5, -4), qL(4, 5, 3, -3)),
     OpSum(Q1quqdc(-1, -2, -3, -4))),

    (Op(qLc(0, 1, 2, -1), TSU3(3, 1, 4), uR(0, 4, -2),
        epsSU2(2, 5),
        qLc(6, 7, 5, -3), TSU3(3, 7, 8), dR(0, 8, -4)),
     OpSum(Q8quqd(-1, -2, -3, -4))),

    (Op(uRc(0, 4, -2), TSU3(3, 4, 1), qLc(0, 1, 2, -1),
        epsSU2(2, 5),
        dRc(0, 8, -4), TSU3(3, 8, 7), qL(6, 7, 5, -3)),
     OpSum(Q8quqdc(-1, -2, -3, -4))),
    
    (Op(lLc(0, 1, -1), eR(0, -2), epsSU2(1, 2),
        qLc(3, 4, 2, -3), uR(3, 4, -4)),
     OpSum(Q1lequ(-1, -2, -3, -4))),

    (Op(eRc(0, -2), lL(0, 1, -1), epsSU2(1, 2),
        uRc(3, 4, -4), qL(3, 4, 2, -3)),
     OpSum(Q1lequc(-1, -2, -3, -4))),

    (Op(lLc(0, 1, -1), sigmaTensor(5, 6, 0, 7), eR(7, -2), epsSU2(1, 2),
        qLc(3, 4, 2, -3), sigmaTensor(5, 6, 3, 8), uR(8, 4, -4)),
     OpSum(Q3lequ(-1, -2, -3, -4))),

    (Op(eRc(0, -2), sigmaTensor(5, 6, 0, 7), lL(7, 1, -1), epsSU2(1, 2),
        uRc(3, 4, -4), sigmaTensor(5, 6, 3, 8), qL(8, 4, 2, -3)),
     OpSum(Q3lequc(-1, -2, -3, -4))),


    # \slashed{B} and \slashed{L} type

    (Op(epsSU3(0, 1, 2), epsSU2(3, 4),
        epsDownDot(5, 6), dR(6, 0, -1), uR(5, 1, -2),
        epsUp(7, 8), qL(8, 2, 3, -3), lL(7, 4, -4)),
     OpSum(Qduq(-1, -2, -3, -4))),

    (Op(epsSU3(0, 1, 2), epsSU2(3, 4),
        epsDown(5, 6), dRc(6, 0, -1), uRc(5, 1, -2),
        epsUpDot(7, 8), qLc(8, 2, 3, -3), lLc(7, 4, -4)),
     OpSum(Qduqc(-1, -2, -3, -4))),

    (Op(epsSU3(0, 1, 2), epsSU2(3, 4),
        epsUp(5, 6), qL(6, 0, 3, -1), qL(5, 1, 4, -2),
        epsDownDot(7, 8), uR(8, 2, -3), eR(7, -4)),
     OpSum(Qqqu(-1, -2, -3, -4))),

    (Op(epsSU3(0, 1, 2), epsSU2(3, 4),
        epsUpDot(5, 6), qLc(6, 0, 3, -1), qLc(5, 1, 4, -2),
        epsDown(7, 8), uRc(8, 2, -3), eRc(7, -4)),
     OpSum(Qqquc(-1, -2, -3, -4))),

    (Op(epsSU3(0, 1, 2), epsSU2(3, 4), epsSU2(5, 6),
        epsUp(7, 8), qL(8, 0, 3, -1), qL(7, 1, 4, -2),
        epsUp(9, 10), qL(10, 2, 5, -3), lL(9, 6, -4)),
     OpSum(Q1qqq(-1, -2, -3, -4))),

    (Op(epsSU3(0, 1, 2), epsSU2(3, 4), epsSU2(5, 6),
        epsUpDot(7, 8), qLc(8, 0, 3, -1), qLc(7, 1, 4, -2),
        epsUpDot(9, 10), qLc(10, 2, 5, -3), lLc(9, 6, -4)),
     OpSum(Q1qqqc(-1, -2, -3, -4))),

    (Op(epsSU3(0, 1, 2),
        sigmaSU2(3, 4, 5), epsSU2(5, 6),
        sigmaSU2(3, 7, 8), epsSU2(8, 9),
        epsUp(10, 11), qL(11, 0, 5, -1), qL(10, 1, 6, -2),
        epsUp(12, 13), qL(13, 2, 8, -3), lL(12, 9, -4)),
     OpSum(Q3qqq(-1, -2, -3, -4))),

    (Op(epsSU3(0, 1, 2),
        sigmaSU2(3, 4, 5), epsSU2(5, 6),
        sigmaSU2(3, 7, 8), epsSU2(8, 9),
        epsUpDot(10, 11), qLc(11, 0, 5, -1), qLc(10, 1, 6, -2),
        epsUpDot(12, 13), qLc(13, 2, 8, -3), lLc(12, 9, -4)),
     OpSum(Q3qqqc(-1, -2, -3, -4))),

    (Op(epsSU3(0, 1, 2),
        epsDownDot(3, 4), dR(4, 0, -1), uR(3, 1, -2),
        epsDownDot(5, 6), uR(6, 1, -3), eR(5, -4)),
     OpSum(Qduu(-1, -2, -3, -4))),

    (Op(epsSU3(0, 1, 2),
        epsDown(3, 4), dRc(4, 0, -1), uRc(3, 1, -2),
        epsDown(5, 6), uRc(6, 1, -3), eRc(5, -4)),
     OpSum(Qduuc(-1, -2, -3, -4))),

    # Standard Model dimension 6 operators other than four-fermion

    # S type

    (Op(D(0, phic(1)), D(0, phi(1)), phic(2), phi(2)),
     OpSum(number_op(Fraction(1, 2)) * Qphisq,
           -Op(mu2phi()) * Qphi4,
           number_op(6) * Op(lambdaphi()) * Qphi,
           number_op(Fraction(1, 2)) * Op(ye(0, 1)) * Qephi(0, 1),
           number_op(Fraction(1, 2)) * Op(yd(0, 1)) * Qdphi(0, 1),
           number_op(Fraction(1, 2)) * Op(Vc(0, 1), yu(0, 2)) * Quphi(1, 2),
           number_op(Fraction(1, 2)) * Op(yec(0, 1)) * Qephic(0, 1),
           number_op(Fraction(1, 2)) * Op(ydc(0, 1)) * Qdphic(0, 1),
           number_op(Fraction(1, 2)) * Op(V(0, 1), yuc(0, 2)) * Quphic(1, 2))),
           
    
    (Op(phic(0), phi(0), phic(1), phi(1), phic(2), phi(2)),
     OpSum(Qphi)),

    # SVF type

    (Op(phic(0), D(1, phi(0)),
        lLc(2, 3, -1), sigma4bar(1, 2, 4), lL(4, 3, -2)),
     OpSum(- i_op * Q1phil(-1, -2),
           Op(D(1, phic(0)), phi(0),
              lLc(2, 3, -2), sigma4bar(1, 2, 4), lL(4, 3, -1)),)),

    (Op(phic(0), sigmaSU2(1, 0, 2), D(3, phi(2)),
        lLc(4, 5, -1), sigma4bar(3, 4, 6),
        sigmaSU2(1, 5, 7), lL(6, 7, -2)),
     OpSum(- i_op * Q3phil(-1, -2),
           Op(D(3, phic(0)), sigmaSU2(1, 0, 2), phi(2),
              lLc(4, 5, -2), sigma4bar(3, 4, 6),
              sigmaSU2(1, 5, 7), lL(6, 7, -1)))),

    (Op(phic(0), D(1, phi(0)),
        qLc(2, 3, 4, -1), sigma4bar(1, 2, 5), qL(5, 3, 4, -2)),
     OpSum(- i_op * Q1phiq(-1, -2),
           Op(D(1, phic(0)), phi(0),
              qLc(2, 3, 4, -2), sigma4bar(1, 2, 5), qL(5, 3, 4, -1)))),

    (Op(phic(0), sigmaSU2(1, 0, 2), D(3, phi(2)),
        qLc(4, 5, 6, -1), sigma4bar(3, 4, 7),
        sigmaSU2(1, 6, 8), qL(7, 5, 8, -2)),
     OpSum(- i_op * Q3phiq(-1, -2),
           Op(D(3, phic(0)), sigmaSU2(1, 0, 2), phi(2),
              qLc(4, 5, 6, -2), sigma4bar(3, 4, 7),
              sigmaSU2(1, 6, 8), qL(7, 5, 8, -1)))),

    (Op(phic(0), D(1, phi(0)),
        eRc(2, -1), sigma4(1, 2, 3), eR(3, -2)),
     OpSum(- i_op * Q1phie(-1, -2),
           Op(D(1, phic(0)), phi(0),
              eRc(2, -2), sigma4(1, 2, 3), eR(3, -1)))),

    (Op(phic(0), D(1, phi(0)),
        dRc(2, 3, -1), sigma4(1, 2, 4), dR(4, 3, -2)),
     OpSum(- i_op * Q1phid(-1, -2),
           Op(D(1, phic(0)), phi(0),
              dRc(2, 3, -2), sigma4(1, 2, 4), dR(4, 3, -1)))),

    (Op(phic(0), D(1, phi(0)),
        uRc(2, 3, -1), sigma4(1, 2, 4), uR(4, 3, -2)),
     OpSum(- i_op * Q1phiu(-1, -2),
           Op(D(1, phic(0)), phi(0),
              uRc(2, 3, -2), sigma4(1, 2, 4), uR(4, 3, -1)))),

    (Op(phi(0), epsSU2(0, 1), D(2, phi(1)),
        uRc(3, 4, -1), sigma4(2, 3, 5), dR(5, 4, -2)),
     OpSum(- i_op * Qphiud(-1, -2),
           Op(phic(0), epsSU2(0, 1), D(2, phic(1)),
              dRc(3, 4, -2), sigma4(2, 3, 5), uR(5, 4, -1)))),

    # STF type

    (Op(lLc(0, 1, -1), sigmaTensor(2, 3, 0, 4), eR(4, -2),
        phi(1), bFS(2, 3)),
     OpSum(QeB(-1, -2))),

    (Op(eRc(4, -2), sigmaTensor(2, 3, 4, 0), lL(0, 1, -1),
        phic(1), bFS(2, 3)),
     OpSum(QeBc(-1, -2))),

    (Op(lLc(0, 1, -1), sigmaTensor(2, 3, 0, 4), eR(4, -2),
        sigmaSU2(5, 1, 6), phi(6), wFS(2, 3, 5)),
     OpSum(QeW(-1, -2))),

    (Op(eRc(4, -2), sigmaTensor(2, 3, 4, 0), lL(0, 1, -1),
        sigmaSU2(5, 6, 1), phic(6), wFS(2, 3, 5)),
     OpSum(QeWc(-1, -2))),

    (Op(qLc(0, 1, 2, -1), sigmaTensor(3, 4, 0, 5), uR(5, 1, -2),
        epsSU2(2, 6), phic(6), bFS(3, 4)),
     OpSum(QuB(-1, -2))),

    (Op(uRc(5, 1, -2), sigmaTensor(3, 4, 5, 0), qL(0, 1, 2, -1),
        epsSU2(2, 6), phi(6), bFS(3, 4)),
     OpSum(QuBc(-1, -2))),

    (Op(qLc(0, 1, 2, -1), sigmaTensor(3, 4, 0, 5), uR(5, 1, -2),
        sigmaSU2(6, 2, 7), epsSU2(7, 8), phic(8), wFS(3, 4, 6)),
     OpSum(QuW(-1, -2))),

    (Op(uRc(5, 1, -2), sigmaTensor(3, 4, 5, 0), qLc(0, 1, 2, -1),
        sigmaSU2(6, 7, 2), epsSU2(7, 8), phi(8), wFS(3, 4, 6)),
     OpSum(QuWc(-1, -2))),

    (Op(qLc(0, 1, 2, -1), sigmaTensor(3, 4, 0, 5), dR(5, 1, -2),
        phi(2), bFS(3, 4)),
     OpSum(QdB(-1, -2))),

    (Op(dRc(5, 1, -2), sigmaTensor(3, 4, 5, 0), qL(0, 1, 2, -1),
        phic(2), bFS(3, 4)),
     OpSum(QdBc(-1, -2))),

    (Op(qLc(0, 1, 2, -1), sigmaTensor(3, 4, 0, 5), dR(5, 1, -2),
        sigmaSU2(6, 2, 7), phi(7), wFS(3, 4, 6)),
     OpSum(QdW(-1, -2))),

    (Op(dRc(5, 1, -2), sigmaTensor(3, 4, 5, 0), qL(0, 1, 2, -1),
        sigmaSU2(6, 7, 2), phic(7), wFS(3, 4, 6)),
     OpSum(QdWc(-1, -2))),

    (Op(qLc(0, 1, 2, -1), sigmaTensor(3, 4, 0, 5),
        TSU3(6, 1, 7), uR(5, 7, -2),
        epsSU2(2, 8), phic(8), gFS(3, 4, 6)),
     OpSum(QuG(-1, -2))),

    (Op(uRc(5, 7, -2), sigmaTensor(3, 4, 5, 0),
        TSU3(6, 7, 1), qL(0, 1, 2, -1),
        epsSU2(2, 7), phi(8), gFS(3, 4, 6)),
     OpSum(QuGc(-1, -2))),

    (Op(qLc(0, 1, 2, -1), sigmaTensor(3, 4, 0, 5),
        TSU3(6, 1, 7), dR(5, 7, -2),
        phi(2), gFS(3, 4, 6)),
     OpSum(QdG(-1, -2))),

    (Op(dRc(5, 7, -2), sigmaTensor(3, 4, 5, 0),
        TSU3(6, 1, 7), qL(0, 1, 2, -1),
        phic(2), gFS(3, 4, 6)),
     OpSum(QdGc(-1, -2))),
     
    # SF type

    (Op(phic(0), phi(0), lLc(1, 2, -1), phi(2), eR(1, -2)),
     OpSum(Qephi(-1, -2))),

    (Op(phic(0), phi(0), eRc(1, -2), phic(2), lL(1, 2, -1)),
     OpSum(Qephic(-1, -2))),

    (Op(phic(0), phi(0), qLc(1, 2, 3, -1), phi(3), dR(1, 2, -2)),
     OpSum(Qdphi(-1, -2))),

    (Op(phic(0), phi(0), dRc(1, 2, -2), phic(3), qL(1, 2, 3, -1)),
     OpSum(Qdphic(-1, -2))),

    (Op(phic(0), phi(0), qLc(1, 2, 3, -1), epsSU2(3, 4),
        phic(4), uR(1, 2, -2)),
     OpSum(Quphi(-1, -2))),

    (Op(phic(0), phi(0), qLc(1, 2, 3, -1), epsSU2(4, 3),
        phic(4), uR(1, 2, -2)),
     OpSum(-Quphi(-1, -2))),

    (Op(phic(0), phi(0), uRc(1, 2, -2), qL(1, 2, 3, -1),
        epsSU2(3, 4), phi(4)),
     OpSum(Quphic(-1, -2))),

    (Op(phic(0), phi(0), uRc(1, 2, -2), qL(1, 2, 3, -1),
        epsSU2(4, 3), phi(4)),
     OpSum(-Quphic(-1, -2))),

    # Qblique type

    (Op(phic(0), D(1, phi(0)), D(1, phic(2)), phi(2)),
     OpSum(QphiD)),

    (Op(phic(0), phi(0), bFS(1, 2), bFS(1, 2)),
     OpSum(QphiB)),

    (Op(phic(0), phi(0), eps4(1, 2, 3, 4), bFS(3, 4), bFS(1, 2)),
     OpSum(QphiBTilde)),

    (Op(phic(0), sigmaSU2(1, 0, 2), phi(2), wFS(3, 4, 1), bFS(3, 4)),
     OpSum(QWB)),

    (Op(phic(0), sigmaSU2(1, 0, 2), phi(2),
        eps4(3, 4, 5, 6), wFS(5, 6, 1), bFS(3, 4)),
     OpSum(QWBTilde)),

    (Op(phic(0), phi(0), wFS(1, 2, 3), wFS(1, 2, 3)),
     OpSum(QphiW)),

    (Op(phic(0), phi(0), eps4(1, 2, 4, 5), wFS(3, 4, 3), wFS(1, 2, 3)),
     OpSum(QphiWTilde)),

    (Op(phic(0), phi(0), gFS(1, 2, 3), gFS(1, 2, 3)),
     OpSum(QphiG)),
    
    (Op(phic(0), phi(0), eps4(1, 2, 4, 5), gFS(3, 4, 3), gFS(1, 2, 3)),
     OpSum(QphiGTilde)),

    # Gauge type

    (Op(epsSU2triplets(0, 1, 2),
        wFS(3, 4, 0), wFS(4, 5, 1), wFS(5, 3, 2)),
     OpSum(QW)),

    (Op(epsSU2triplets(0, 1, 2),
        eps4(3, 4, 6, 7), wFS(6, 7, 0), wFS(4, 5, 1), wFS(5, 3, 2)),
     OpSum(QWTilde)),

    (Op(fSU3(0, 1, 2),
        gFS(3, 4, 0), gFS(4, 5, 1), gFS(5, 3, 2)),
     OpSum(QG)),

    (Op(fSU3(0, 1, 2),
        eps4(3, 4, 6, 7), gFS(6, 7, 0), gFS(4, 5, 1), gFS(5, 3, 2)),
     OpSum(QGTilde)),

    # Standard Model dimension 5 operators
    
    (Op(lL(0, 1, -1), epsSU2(1, 2), phi(2),
        epsSU2(3, 4), phi(4), epsUp(0, 5), lL(5, 3, -2)),
     OpSum(Q5(-1, -2))),

    (Op(lLc(0, 1, -2), epsSU2(1, 2), phic(2), epsUpDot(0, 3),
        epsSU2(4, 5), phic(5), lLc(3, 4, -1)),
     OpSum(Q5c(-1, -2)))]

rules_basis_defs_dim_4 = [
    # Standard Model dimension 4 operators
    
    (Op(D(0, phic(1)), D(0, phi(1))),
     OpSum(Qkinphi)),

    (Op(phic(0), phi(0), phic(1), phi(1)),
     OpSum(Qphi4)),

    (Op(phic(0), phi(0)),
     OpSum(Qphi2)),

    (Op(lLc(0, 1, -1), phi(1), eR(0, -2)),
     OpSum(Qye(-1, -2))),

    (Op(eRc(0, -2), phic(1), lL(0, 1, -1)),
     OpSum(Qyec(-1, -2))),

    (Op(qLc(0, 1, 2, -1), epsSU2(2, 3), phic(3), uR(0, 1, -2)),
     OpSum(Qyu(-1, -2))),

    (Op(uRc(0, 1, -2), epsSU2(2, 3), phi(3), qL(0, 1, 2, -1)),
     OpSum(Qyuc(-1, -2))),

    (Op(qLc(0, 1, 2, -1), phi(2), dR(0, 1, -2)),
     OpSum(Qyd(-1, -2))),

    (Op(dRc(0, 1, -2), phic(2), qL(0, 1, 2, -1)),
     OpSum(Qydc(-1, -2)))]

rules_basis_definitions = rules_basis_defs_dim_6_5 + rules_basis_defs_dim_4
"""
Rules defining the operators in the basis in terms of 
Standard Model fields.
"""


latex_basis_coefs = {
    # Dimension 4
    "Qkinphi": r"\alpha_{{kin,\phi}}", 
    "Qphi4": r"\alpha_{{\phi 4}}",
    "Qphi2": r"\alpha_{{\phi 2}}",
    "Qye": r"\left(\alpha_{{{{y^e}}}}\right)_{{{}{}}}",
    "Qyec": r"\left(\alpha_{{{{y^e}}}}\right)^*_{{{}{}}}",
    "Qyd": r"\left(\alpha_{{{{y^d}}}}\right)_{{{}{}}}",
    "Qydc": r"\left(\alpha_{{{{y^d}}}}\right)^*_{{{}{}}}",
    "Qyu": r"\left(\alpha_{{{{y^u}}}}\right)_{{{}{}}}",
    "Qyuc": r"\left(\alpha_{{{{y^u}}}}\right)^*_{{{}{}}}",

    # Dimension 5
    "Q5": r"\frac{{\left(\alpha_5\right)_{{{}{}}}}}{{\Lambda}}",
    "Q5c": r"\frac{{\left(\alpha_5\right)^*_{{{}{}}}}}{{\Lambda}}",

    # Dimension 6 four-fermion

    # LLLL
    
    "Qll":
    (r"\frac{{\left(\alpha^{{(1)}}_{{ll}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),
    
    "Q1qq":
    (r"\frac{{\left(\alpha^{{(1)}}_{{qq}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),
    
    "Q3qq":
    (r"\frac{{\left(\alpha^{{(3)}}_{{qq}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1lq":
    (r"\frac{{\left(\alpha^{{(1)}}_{{lq}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q3lq":
    (r"\frac{{\left(\alpha^{{(3)}}_{{lq}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    # RRRR
    
    "Qee":
    (r"\frac{{\left(\alpha_{{ee}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1uu":
    (r"\frac{{\left(\alpha^{{(1)}}_{{uu}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1dd":
    (r"\frac{{\left(\alpha^{{(1)}}_{{dd}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1ud":
    (r"\frac{{\left(\alpha^{{(1)}}_{{ud}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q8ud":
    (r"\frac{{\left(\alpha^{{(8)}}_{{ud}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qeu":
    (r"\frac{{\left(\alpha_{{eu}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qed":
    (r"\frac{{\left(\alpha_{{ed}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),
    
    # LLRR and LRRL
    
    "Qle":
    (r"\frac{{\left(\alpha_{{le}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qqe":
    (r"\frac{{\left(\alpha_{{qe}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qlu":
    (r"\frac{{\left(\alpha_{{lu}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qld":
    (r"\frac{{\left(\alpha_{{ld}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1qu":
    (r"\frac{{\left(\alpha^{{(1)}}_{{qu}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q8qu":
    (r"\frac{{\left(\alpha^{{(8)}}_{{qu}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1qd":
    (r"\frac{{\left(\alpha^{{(1)}}_{{qd}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q8qd":
    (r"\frac{{\left(\alpha^{{(8)}}_{{qd}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),
    
    "Qledq":
    (r"\frac{{\left(\alpha_{{ledq}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qledqc":
    (r"\frac{{\left(\alpha_{{ledq}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    # LRLR

    "Q1quqd":
    (r"\frac{{\left(\alpha^{{(1)}}_{{quqd}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1quqdc":
    (r"\frac{{\left(\alpha^{{(1)}}_{{quqd}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q8quqd":
    (r"\frac{{\left(\alpha^{{(8)}}_{{quqd}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q8quqdc":
    (r"\frac{{\left(\alpha^{{(8)}}_{{quqd}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1lequ":
    (r"\frac{{\left(\alpha^{{(1)}}_{{lequ}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1lequc":
    (r"\frac{{\left(\alpha^{{(1)}}_{{lequ}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q3lequ":
    (r"\frac{{\left(\alpha^{{(3)}}_{{lequ}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q3lequc":
    (r"\frac{{\left(\alpha^{{(3)}}_{{lequ}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    # \slashed{B} and \slashed{L} type
    
    "Qduq":
    (r"\frac{{\left(\alpha_{{duq}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qduqc":
    (r"\frac{{\left(\alpha_{{duq}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qqqu":
    (r"\frac{{\left(\alpha_{{qqu}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qqquc":
    (r"\frac{{\left(\alpha_{{qqu}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1lqqq":
    (r"\frac{{\left(\alpha^{{(1)}}_{{lqqq}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q1lqqqc":
    (r"\frac{{\left(\alpha^{{(1)}}_{{lqqq}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qduu":
    (r"\frac{{\left(\alpha_{{udeu}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Qduuc":
    (r"\frac{{\left(\alpha_{{udeu}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q3lqqq":
    (r"\frac{{\left(\alpha^{{(3)}}_{{lqqq}}\right)"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    "Q3lqqqc":
    (r"\frac{{\left(\alpha^{{(3)}}_{{lqqq}}\right)^*"
     r"_{{{}{}{}{}}}}}{{\Lambda^2}}"),

    # Dimesion 6 other than four-fermion

    # S type
    
    "Qphi": r"\frac{{\alpha_\phi}}{{\Lambda^2}}",
    "Qphisq": r"\frac{{\alpha_{{\phi\square}}}}{{\Lambda^2}}",

    # SVF type

    "Q1phil":
    (r"\frac{{\left(\alpha^{{(1)}}_{{\phi l}}\right)"
     r"_{{{}{}}}}}{{\Lambda^2}}"),
    
    "Q3phil":
    (r"\frac{{\left(\alpha^{{(3)}}_{{\phi l}}\right)"
     r"_{{{}{}}}}}{{\Lambda^2}}"),
    
    "Q1phiq":
    (r"\frac{{\left(\alpha^{{(1)}}_{{\phi q}}\right)"
     r"_{{{}{}}}}}{{\Lambda^2}}"),
    
    "Q3phiq":
    (r"\frac{{\left(\alpha^{{(3)}}_{{\phi q}}\right)"
     r"_{{{}{}}}}}{{\Lambda^2}}"),
    
    "Q1phie":
    (r"\frac{{\left(\alpha^{{(1)}}_{{\phi e}}\right)"
     r"_{{{}{}}}}}{{\Lambda^2}}"),
    
    "Q1phid":
    (r"\frac{{\left(\alpha^{{(1)}}_{{\phi d}}\right)"
     r"_{{{}{}}}}}{{\Lambda^2}}"),
    
    "Q1phiu":
    (r"\frac{{\left(\alpha^{{(1)}}_{{\phi u}}\right)"
     r"_{{{}{}}}}}{{\Lambda^2}}"),
    
    "Qphiud":
    (r"\frac{{\left(\alpha_{{\phi ud}}\right)"
     r"_{{{}{}}}}}{{\Lambda^2}}"),
    
    # STF type
    
    "QeB":
    r"\frac{{\left(\alpha_{{eB}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "QeW":
    r"\frac{{\left(\alpha_{{eW}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "QuB":
    r"\frac{{\left(\alpha_{{uB}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "QuW":
    r"\frac{{\left(\alpha_{{uW}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "QdB":
    r"\frac{{\left(\alpha_{{dB}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "QdW":
    r"\frac{{\left(\alpha_{{dW}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "QdG":
    r"\frac{{\left(\alpha_{{uG}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "QdG":
    r"\frac{{\left(\alpha_{{dG}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    # SF type

    "Qephi":
    r"\frac{{\left(\alpha_{{e\phi}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "Qephic":
    r"\frac{{\left(\alpha_{{e\phi}}\right)^*_{{{}{}}}}}{{\Lambda^2}}",

    "Qdphi":
    r"\frac{{\left(\alpha_{{d\phi}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "Qdphic":
    r"\frac{{\left(\alpha_{{d\phi}}\right)^*_{{{}{}}}}}{{\Lambda^2}}",

    "Quphi":
    r"\frac{{\left(\alpha_{{u\phi}}\right)_{{{}{}}}}}{{\Lambda^2}}",

    "Quphic":
    r"\frac{{\left(\alpha_{{u\phi}}\right)^*_{{{}{}}}}}{{\Lambda^2}}",

    # Qblique type
    
    "QphiD": r"\frac{{\alpha_{{\phi D}}}}{{\Lambda^2}}",
    "QphiB": r"\frac{{\alpha_{{\phi B}}}}{{\Lambda^2}}",
    "QWB": r"\frac{{\alpha_{{WB}}}}{{\Lambda^2}}",
    "QphiW": r"\frac{{\alpha_{{\phi W}}}}{{\Lambda^2}}",
    "QphiBTilde": r"\frac{{\alpha_{{\phi\tilde{{B}}}}}}{{\Lambda^2}}",
    "QWBTilde": r"\frac{{\alpha_{{W\tilde{{B}}}}}}{{\Lambda^2}}",
    "QphiWTilde": r"\frac{{\alpha_{{\phi\tilde{{W}}}}}}{{\Lambda^2}}",
    "QphiG": r"\frac{{\alpha_{{\phi G}}}}{{\Lambda^2}}",
    "QphiGTilde": r"\frac{{\alpha_{{\phi\tilde{{G}}}}}}{{\Lambda^2}}",

    # Gauge type

    "QW": r"\frac{{\alpha_W}}{{\Lambda^2}}",
    "QWTilde": r"\frac{{\alpha_{{\tilde{{W}}}}}}{{\Lambda^2}}",
    "QG": r"\frac{{\alpha_G}}{{\Lambda^2}}",
    "QGTilde": r"\frac{{\alpha_{{\tilde{{G}}}}}}{{\Lambda^2}}"}
"""
LaTeX representation of the coefficients of the
operators in the basis.
"""
