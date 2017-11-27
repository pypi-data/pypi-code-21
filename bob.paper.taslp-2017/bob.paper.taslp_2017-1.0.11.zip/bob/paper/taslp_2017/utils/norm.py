#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import numpy
import math
import sys

""" Utility functions for column-wise normalization of data
"""

def calc_mean(c0, c1=[]):
  """ Calculates the mean of the data.""" 
  if c1 != []:   
    return (numpy.mean(c0, 0) + numpy.mean(c1, 0)) / 2.
  else:
    return numpy.mean(c0, 0)  

def calc_std(c0,mi,c1=[]):
  """ Calculates the variance of the data."""
  if c1 == []:
    return numpy.std(c0, 0)
  prop = float(len(c0)) / float(len(c1))
  if prop < 1: 
    p0 = int(math.ceil(1/prop))
    p1 = 1
  else:
    p0 = 1
    p1 = int(math.ceil(prop))

  l0=p0*c0.shape[0]+p1*c1.shape[0]
  l1=c0.shape[1]
  std=numpy.zeros(l1)
  
  i=0
  len_chunk=1000
  for i in range(int(math.ceil(len(c0)/float(len_chunk)))):
    i0=i*len_chunk
    i1=min(i0+len_chunk,len(c0))
    chunk=c0[i0:i1,:]
    std+=p0*numpy.sum(abs(chunk - mi)**2,axis=0)

  for i in range(int(math.ceil(len(c1)/float(len_chunk)))):
    i0=i*len_chunk
    i1=min(i0+len_chunk,len(c1))
    chunk=c1[i0:i1,:]
    std+=p1*numpy.sum(abs(chunk - mi)**2,axis=0)

  std/=l0
  std=numpy.sqrt(std)

  return std
  
"""
@param c0
@param c1
@param nonStdZero if the std was zero, convert to one. This will avoid a zero division
"""
def calc_mean_std(c0, c1=[], nonStdZero=False):
  """ Calculates both the mean of the data. """
  mi = calc_mean(c0,c1)
  std = calc_std(c0,mi,c1)
  if(nonStdZero):
    std[std==0] = 1

  return mi, std

def zeromean_unitvar_norm(data, mean, std):
  """ Normalized the data with zero mean and unit variance. Mean and variance are in numpy.ndarray format"""
  for i in range(len(std)):
    data[:,i]-=mean[i]
    data[:,i]/=std[i]
  return data


