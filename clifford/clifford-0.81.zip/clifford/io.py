
"""
Algorithms and tools of various kinds.

Determining Rotors From Frame Pairs or Orthogonal Matrices
==========================================================

Given two frames that are related by a orthogonal transform, we seek a rotor which enacts the transform. Detail of the mathematics and psuedo code used the create the algorithms below can be found at Allan Cortzen's website.

 http://ctz.dk/geometric-algebra/frames-to-versor-algorithm/

There are also some helper functions which can be used to translate matrices into GA frames, so an orthogonal (or complex unitary )matrix can be directly translated into a Verser. 

.. autosummary::
    :toctree: generated/
    
    orthoFrames2Verser
    orthoMat2Verser
    mat2Frame
    
