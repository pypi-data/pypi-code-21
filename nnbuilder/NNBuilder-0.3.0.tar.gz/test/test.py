import numpy as np
from nnbuilder.kernel import *
'''
b='batch'
u='unit'
f='feature'

nx=np.random.randn(3,5).astype('float32')
nw1=np.random.uniform(-1,1,[5,4]).astype('float32')
nw2=np.ones([4,4]).astype('float32')


x=kernel.placeholder('x',[b,f])
w1=kernel.shared(nw1,'w1',[None,u])
w2=kernel.shared(nw2,'w2',[None,u])

ny0=(nx**2-1)*2/nx
ny1=np.dot(ny0,nw1)
ny2=np.dot(ny1+3,nw2)
ny3=ny2.sum(1)
ny4=np.stack([ny3,ny3])
ny5=ny4[:,1]
ny6=np.tanh(ny5)
ny6[1]=ny6[0]

y0=(x**T.constant(2)-1)*2/x
y1=T.dot(y0,w1)
y2=T.dot(y1+3,w2)
y3=y2.sum(1)
y4=T.stack([y3,y3])
y5=y4[:,1]
y6=T.tanh(y5)
y6[1]=y6[0]


f=kernel.compile([x],[y0,y1,y2,y3,y4,y5,y6])

ry0,ry1,ry2,ry3,ry4,ry5,ry6=f(nx)

nyl=[ny0,ny1,ny2,ny3,ny4,ny5,ny5,ry6]
ryl=[ry0,ry1,ry2,ry3,ry4,ry5,ry5,ry6]
for n,(i,j) in enumerate(zip(nyl,ryl)):
    if not np.equal(i,j).all():
        print n
'''
a=kernel.placeholder('X',['batch','unit'],dtype='float32')
b=kernel.placeholder('Y',['batch','unit'],dtype='float32')
def f(x):
    return x+1
#kernel.backend.scan(f,[a.graph])
print a == None
c = a[0]
o,u=kernel.scan(f,[a])
print o