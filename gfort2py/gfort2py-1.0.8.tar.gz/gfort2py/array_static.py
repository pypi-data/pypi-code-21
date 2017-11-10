# SPDX-License-Identifier: GPL-2.0+

import ctypes

_index_t = ctypes.c_int64
_size_t = ctypes.c_int64

# Pre generate alloc array descriptors
class _bounds(ctypes.Structure):
    _fields_=[("stride",_index_t),
              ("lbound",_index_t),
              ("ubound",_index_t)]

class _fAllocArray1D(ctypes.Structure):
    ndims=1
    _fields_=[('base_addr',ctypes.c_void_p), 
              ('offset',_size_t), 
              ('dtype',_index_t),
              ('dims',_bounds*ndims)
              ]

class _fAllocArray2D(ctypes.Structure):
    ndims=2
    _fields_=[('base_addr',ctypes.c_void_p), 
              ('offset',_size_t), 
              ('dtype',_index_t),
              ('dims',_bounds*ndims)
              ]
              
class _fAllocArray3D(ctypes.Structure):
    ndims=3
    _fields_=[('base_addr',ctypes.c_void_p), 
              ('offset',_size_t), 
              ('dtype',_index_t),
              ('dims',_bounds*ndims)
              ]
              
class _fAllocArray4D(ctypes.Structure):
    ndims=4
    _fields_=[('base_addr',ctypes.c_void_p), 
              ('offset',_size_t), 
              ('dtype',_index_t),
              ('dims',_bounds*ndims)
              ]
class _fAllocArray5D(ctypes.Structure):
    ndims=5
    _fields_=[('base_addr',ctypes.c_void_p), 
              ('offset',_size_t), 
              ('dtype',_index_t),
              ('dims',_bounds*ndims)
              ]
              
class _fAllocArray6D(ctypes.Structure):
    ndims=6
    _fields_=[('base_addr',ctypes.c_void_p), 
              ('offset',_size_t), 
              ('dtype',_index_t),
              ('dims',_bounds*ndims)
              ]
              
class _fAllocArray7D(ctypes.Structure):
    ndims=7
    _fields_=[('base_addr',ctypes.c_void_p), 
              ('offset',_size_t), 
              ('dtype',_index_t),
              ('dims',_bounds*ndims)
              ]

# None is in there so we can do 1 based indexing
listFAllocArrays=[None,_fAllocArray1D,_fAllocArray2D,_fAllocArray3D,
                    _fAllocArray4D,_fAllocArray5D,_fAllocArray6D,
                    _fAllocArray7D] 
