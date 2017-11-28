import xun
import numpy as np
import matplotlib.pyplot as plt

# Add constant to vector
a = np.zeros(3)
b = xun.sum_const_vec(2.,a)
print(a)
print(b)

# Add constant to matrix
a2 = np.zeros((2,3))
b2 = xun.sum_const_mat(2.,a2)
print(a2)
print(b2)

# Sample Weibull (2,4)
a = 2.
b = 4.
def pdf(x):
    return a/b * (x/b)**(a-1.) * np.exp(-(x/b)**a)
n = 10000
c = xun.weird_samples(n)
xx = np.linspace(np.min(c),np.max(c),100)
plt.figure()
plt.hist(c,bins=20,normed=True,histtype='step')
plt.plot(xx,pdf(xx))
plt.show(False)