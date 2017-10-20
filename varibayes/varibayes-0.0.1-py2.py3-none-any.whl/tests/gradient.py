import numpy as np
import varibayes.infer as infer


def gradtest(vb, p0, h=1E-8, nsamples=12):
    vb.params = p0
    vb.samples = nsamples
    zs = vb.sampledistn()
    grad = vb.gradlogdistn(zs=zs)
    logdistn0 = vb.logdistn(zs=zs)
    fd_grad = []
    for i in range(len(p0)):
        vb.params[i] += h
        fd_grad += [vb.logdistn(zs=zs)-logdistn0]
        vb.params[i] -= h
    fd_grad = np.array(fd_grad).T/h
    return grad, fd_grad


if __name__=='__main__':

    vb = infer.VariationalInferenceMF(lambda x: x, samples=1)
    ps = []
    print("Running gradient test:")
    for i in range(10):
        vb.params = np.hstack([np.random.randn(10), np.random.rand(10)])
        ps += [vb.params.copy()]
        grad, fd_grad = gradtest(vb, vb.params)
        rms = np.sqrt(np.mean((grad-fd_grad)**2))
        print("Test {}: rms error = {}".format(i, rms))
