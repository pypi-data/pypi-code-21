#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import pymt64 


n= 1000000

# initial seed value
seed=12338

# initialisation:
# mt is the stage vector of the Mersenne Twister pseudorandom number generator
# in the case of multrithreading, each thread must have its own vector mt
mt = pymt64.init(seed)

# generating a uniform distribution
x = pymt64.uniform(mt,n)
plt.figure(0)
plt.clf()
plt.hist(x,bins=100)


# generating a Poisson distribution
lam = 10. # the characteristic mean 'lambda'
y = pymt64.poisson(mt,lam,n)
plt.figure(1)
plt.hist(y,bins=100)

# generating two independent Normal distributions
(u,v) = pymt64.normal(mt,n)
plt.figure(2)
plt.clf()
plt.hist(u,bins=100)

# Poisson distribution for a set of lambda values:
# generate poisson distributed values as many as lambda values 
lam =  np.random.uniform(low=1.,high=1e5,size=n)  # in this test case we generate n random values of 'lambda'
x = pymt64.poisson_multlam(mt,lam) 


plt.show()


