#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

#from .extraction import *
import numpy 

def smoothing(labels, smoothing_window):
  """ Applies a smoothing on VAD"""

  if numpy.sum(labels)< smoothing_window:
    return labels
  segments = []
  for k in range(1,len(labels)-1):
    if labels[k]==0 and labels[k-1]==1 and labels[k+1]==1 :
      labels[k]=1
  for k in range(1,len(labels)-1):
    if labels[k]==1 and labels[k-1]==0 and labels[k+1]==0 :
      labels[k]=0

  seg = numpy.array([0,0,labels[0]])
  for k in range(1,len(labels)):
    if labels[k] != labels[k-1]:
      seg[1]=k-1
      segments.append(seg)
      seg = numpy.array([k,k,labels[k]])
  seg[1]=len(labels)-1
  segments.append(seg)

  if len(segments) < 2:
    return labels

  curr = segments[0]
  next = segments[1]

  # Look at the first segment. If it's short enough, just change its labels
  if (curr[1]-curr[0]+1) < smoothing_window and (next[1]-next[0]+1) > smoothing_window:
    if curr[2]==1:
      labels[curr[0] : (curr[1]+1)] = numpy.zeros(curr[1] - curr[0] + 1)
      curr[2]=0
    else: #curr[2]==0
      labels[curr[0] : (curr[1]+1)] = numpy.ones(curr[1] - curr[0] + 1)
      curr[2]=1

  for k in range(1,len(segments)-1):
    prev = segments[k-1]
    curr = segments[k]
    next = segments[k+1]

    if (curr[1]-curr[0]+1) < smoothing_window and (prev[1]-prev[0]+1) > smoothing_window and (next[1]-next[0]+1) > smoothing_window:
      if curr[2]==1:
        labels[curr[0] : (curr[1]+1)] = numpy.zeros(curr[1] - curr[0] + 1)
        curr[2]=0
      else: #curr[2]==0
        labels[curr[0] : (curr[1]+1)] = numpy.ones(curr[1] - curr[0] + 1)
        curr[2]=1

  prev = segments[-2]
  curr = segments[-1]

  if (curr[1]-curr[0]+1) < smoothing_window and (prev[1]-prev[0]+1) > smoothing_window:
    if curr[2]==1:
      labels[curr[0] : (curr[1]+1)] = numpy.zeros(curr[1] - curr[0] + 1)
      curr[2]=0
    else: #if curr[2]==0
      labels[curr[0] : (curr[1]+1)] = numpy.ones(curr[1] - curr[0] + 1)
      curr[2]=1

  return labels


def normalize_std_array(vector):
  """Applies a unit mean and variance normalization to an arrayset"""

  # Initializes variables
  length = 1
  n_samples = len(vector)
  mean = numpy.ndarray((length,), 'float64')
  std = numpy.ndarray((length,), 'float64')
  mean.fill(0)
  std.fill(0)

  # Computes mean and variance
  for array in vector:
    x = array.astype('float64')
    mean += x
    std += (x ** 2)

  mean /= n_samples
  std /= n_samples
  std -= (mean ** 2)
  std = std ** 0.5
  arrayset = numpy.ndarray(shape=(n_samples,mean.shape[0]), dtype=numpy.float64)

  for i in range (0, n_samples):
    arrayset[i,:] = (vector[i]-mean) / std
  return arrayset


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
