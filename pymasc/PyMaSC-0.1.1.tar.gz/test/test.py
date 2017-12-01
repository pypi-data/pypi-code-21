import numpy as np

SHIFT = 37
READLEN = 36


def strip(l):
    return ''.join(map(str, l))


f = [0] * 100
f[57] = f[58] = 1

g = [0]*(READLEN - 1) + [1]*57 + [0] * 8

m = []
for i, n in enumerate([15, 10, 4, 26, 7, 4, 37, 11, 89]):
    m += [0 if i%2 else 1] * n


f = np.array(f)
g = np.array(g)


def calcDM(d):
    shift = abs(READLEN - 1 - d)

    return [i*j for i, j in zip(m, m[shift:])][:100]


print strip(f)
print strip(m[:100])
print strip(g)


for i in range(SHIFT + 1):
    dm = np.array(calcDM(i))
    fm = f * dm
    rm = g * dm
    print i, sum(fm), sum(rm), sum(fm * rm)
    print strip(f)
    # print strip(dm)
    print strip(m[:100])
    print strip(m[READLEN - 1 - i:][:100])
    print strip(g[i:])
    print

# print [sum(f * np.array(calcDM(i))) for i in range(SHIFT + 1)]
