__author__ = 'cbarnett'
try:
    import numpy as np
    import math
    import logging

except Exception as e:
    print("Error - Cannot import module: %s", e)
    exit(1)

logger = logging.getLogger(__name__)
#logger.critical(logger.getEffectiveLevel())


# logger.setLevel(level='DEBUG')

def calctt_pucker(atomiccoorsstring, noa):
    """
    Calculate Triangular Tessellation for 5-8 mem pucker.
    """
    # the numberofatoms variable is being used an error check,
    # as I can clearly work this out from the number of atomiccoords
    global obj, obj
    if type(noa) != type(int):
        logging.warning("Number of atoms not an integer, casting to an int: %s", noa)
        noa = int(noa)
    if not (len(atomiccoorsstring.split()) / 3 == noa):
        logger.error("Coords and supposed number of atoms, do not match")
        exit(1)
    atoms = np.zeros((noa + 1, 3), dtype='float64')
    r = np.zeros((noa, 3), dtype='float64')
    a = np.zeros((noa - 3, 3), dtype='float64')
    p = np.zeros((noa, 3), dtype='float64')
    q = np.zeros((noa - 3, 3), dtype='float64')
    logger.debug("Atom coordinate string %s", atomiccoorsstring)
    prepend = ["text"]
    sline = atomiccoorsstring.split()
    sline = prepend + sline
    if noa == 5:
        for i in range(4, 16, 3):
            atoms[int((i - 4) / 3)] = tofloat(sline[i:i + 3])
        for i in range(1, 7, 3):
            atoms[int((i - 1) / 3 + 4)] = tofloat(sline[i:i + 3])
    elif noa == 6:
        for i in range(4, 19, 3):
            atoms[int((i - 4) / 3)] = tofloat(sline[i:i + 3])
        for i in range(1, 7, 3):
            atoms[int((i - 1) / 3 + 5)] = tofloat(sline[i:i + 3])
    elif noa == 7:
        for i in range(4, 20, 3):
            atoms[int((i - 4) / 3)] = tofloat(sline[i:i + 3])
        for i in range(1, 7, 3):
            atoms[int((i - 1) / 3 + 6)] = tofloat(sline[i:i + 3])
    elif noa == 8:
        for i in range(4, 23, 3):
            atoms[int((i - 4) / 3)] = tofloat(sline[i:i + 3])
        for i in range(1, 7, 3):
            atoms[int((i - 1) / 3 + 7)] = tofloat(sline[i:i + 3])
    center = np.add.reduce(atoms[0:noa]) / noa
    logger.debug("Center is %s", center)
    atoms = atoms - center
    for i in range(0, noa):
        r[i] = atoms[i + 1] - atoms[i]
    for i in range(0, noa - 3):
        if (noa == 7 and i == 3) or (noa == 8 and i == 4):
            pass
        else:
            a[i] = atoms[2 * (i + 1)] - atoms[2 * i]
    if noa == 7:
        a[3] = atoms[7] - atoms[4]
        obj = np.cross(a[2], r[6])
    elif noa == 8:
        a[4] = atoms[8] - atoms[4]
        obj = np.cross(a[2], a[3])
    for i in range(1, noa):
        p[i] = np.cross(r[i - 1], r[i])
    for i in range(0, noa - 3):
        if (noa == 7 and i == 3) or (noa == 8 and i == 4):
            pass
        else:
            q[i] = np.cross(a[i], p[2 * i + 1])
    n = np.cross(a[1], a[0])
    theta = []
    n1 = 0.0
    if noa == 7:
        q[3] = np.cross(a[3], obj)
        n1 = np.cross(a[3], a[2])
    elif noa == 8:
        q[4] = np.cross(a[4], obj)
        n1 = np.cross(a[3], a[2])
    for i in q:
        theta.append(90 - math.degrees(math.acos(np.dot(i, n) / (np.linalg.norm(i) * np.linalg.norm(n)))))
    if noa == 5:
        return theta[0], theta[1]
    elif noa == 6:
        return theta[0], theta[1], theta[2]
    elif noa == 7:
        theta = [90 - math.degrees(math.acos(np.dot(q[0], n) / (np.linalg.norm(q[0]) * np.linalg.norm(n)))),
                 90 - math.degrees(math.acos(np.dot(q[1], n) / (np.linalg.norm(q[1]) * np.linalg.norm(n)))),
                 90 - math.degrees(math.acos(np.dot(q[2], n1) / (np.linalg.norm(q[2]) * np.linalg.norm(n1)))),
                 90 - math.degrees(math.acos(np.dot(q[3], n) / (np.linalg.norm(q[3]) * np.linalg.norm(n))))]
        return theta[0], theta[1], theta[2], theta[3]
    elif noa == 8:
        theta = [90 - math.degrees(math.acos(np.dot(q[0], n) / (np.linalg.norm(q[0]) * np.linalg.norm(n)))),
                 90 - math.degrees(math.acos(np.dot(q[1], n) / (np.linalg.norm(q[1]) * np.linalg.norm(n)))),
                 90 - math.degrees(math.acos(np.dot(q[2], n1) / (np.linalg.norm(q[2]) * np.linalg.norm(n1)))),
                 90 - math.degrees(math.acos(np.dot(q[3], n1) / (np.linalg.norm(q[3]) * np.linalg.norm(n1)))),
                 90 - math.degrees(math.acos(np.dot(q[4], n) / (np.linalg.norm(q[4]) * np.linalg.norm(n))))]
        return theta[0], theta[1], theta[2], theta[3], theta[4]


def tofloat(a):
    """  parse string list/tuple to float list """
    b = []
    for i in a:
        b.append(float(i))
    return b


def rmsd(V, W):
    """ Calculate Root-mean-square deviation from two sets of vectors V and W. """
    D = len(V[0])
    N = len(V)
    rmsd = 0.0
    for v, w in zip(V, W):
        rmsd += sum([(v[i] - w[i]) ** 2.0 for i in range(D)])
    return np.sqrt(rmsd / N)


def centroid(X):
    """ Calculate the centroid from a vectorset X """
    C = sum(X) / len(X)
    return C


def kabsch(P, Q):
    """ The Kabsch algorithm

    http://en.wikipedia.org/wiki/Kabsch_algorithm

    The algorithm starts with two sets of paired points P and Q.
    P and Q should already be centered on top of each other.

    Each vector set is represented as an NxD matrix, where D is the
    the dimension of the space.

    The algorithm works in three steps:
    - a translation of P and Q
    - the computation of a covariance matrix C
    - computation of the optimal rotation matrix U

    The optimal rotation matrix U is then used to
    rotate P unto Q so the RMSD can be caculated
    from a straight forward fashion.

    """

    # Computation of the covariance matrix
    C = np.dot(np.transpose(P), Q)

    # Computation of the optimal rotation matrix
    # This can be done using singular value decomposition (SVD)
    # Getting the sign of the det(V)*(W) to decide
    # whether we need to correct our rotation matrix to ensure a
    # right-handed coordinate system.
    # And finally calculating the optimal rotation matrix U
    # see http://en.wikipedia.org/wiki/Kabsch_algorithm
    V, S, W = np.linalg.svd(C)
    d = (np.linalg.det(V) * np.linalg.det(W)) < 0.0

    if d:
        S[-1] = -S[-1]
        V[:, -1] = -V[:, -1]

    # Create Rotation matrix U
    U = np.dot(V, W)

    # Rotate P
    P = np.dot(P, U)

    return rmsd(P, Q)


class Pucker(object):
    """ Ring pucker calculation module"""

    def __init__(self, arg):
        self._coords = arg
        if len(self._coords) < 15 or len(self._coords) > 24:
            self._coords = None
            self._ringsize = None
            return
        self.ringsize = int(len(arg) / 3)  # working in int so this rounds.
        self._calculatedtt = None
        initoptions = {5: self._init5, 6: self._init6, 7: self._init7, 8: self._init8}
        initoptions[self._ringsize]()

    def _init5(self):
        self._fmt = '%8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f'
        self._TTdict = {"5T1": (-13.1, -33.89), "3T4": (-42.16, 13.21), "2T3": (34.5, -34.5), "1T2": (-13.21, 42.16),
                        "4T5": (33.89, 13.11), "1T5": (13.1, 33.89), "4T3": (42.16, -13.21), "3T2": (-34.5, 34.5),
                        "2T1": (13.21, -42.16), "5T4": (-33.89, -13.11), "E2": (-24.88, 40.0), "E1": (0.0, -39.9),
                        "E5": (24.5, 24.5), "E4": (-39.5, 0.0), "E3": (39.5, -24.9), "2E": (24.88, -40.0),
                        "1E": (0.0, 39.9), "5E": (-24.5, -24.5), "4E": (39.5, 0.0), "3E": (-39.5, 24.9),
                        "P": (0.0, 0.0)}
        self._TTnum = {"1E": 1, "1T5": 2, "E5": 3, "4T5": 4, "4E": 5, "4T3": 6, "E3": 7, "2T3": 8, "2E": 9, "2T1": 10,
                       "E1": 11, "5T1": 12, "5E": 13, "5T4": 14, "E4": 15, "3T4": 16, "3E": 17, "3T2": 18, "E2": 19,
                       "1T2": 20, "P": 21, "UAS": 98, "UAP": 99}

    def _init6(self):
        self._fmt = '%8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f'
        self._TTdict = {"E6": (35.26, 35.26, -17.37), "6E": (-35.26, -35.26, 17.37), "E5": (-46.86, 00.00, 00.00),
                        "5E": (46.86, 00.00, 00.00), "E4": (35.26, -17.37, 35.26), "4E": (-35.26, 17.37, -35.26),
                        "E3": (00.00, 00.00, -46.86), "3E": (00.00, 00.00, 46.86), "E2": (-17.37, 35.26, 35.26),
                        "2E": (17.37, -35.26, -35.26), "E1": (00.00, -46.86, 00.00), "1E": (00.00, 46.86, 00.00),
                        "2S6": (50.84, 00.00, -50.84), "6S2": (-50.84, 00.00, 50.84), "1S5": (-50.84, 50.84, 00.00),
                        "5S1": (50.84, -50.84, 00.00), "3S1": (00.00, -50.84, 50.84), "1S3": (00.00, 50.84, -50.84),
                        "1H6": (17.83, 42.16, -9.07), "6H1": (-17.83, -42.16, 9.07), "6H5": (-42.16, -17.83, 9.06),
                        "5H6": (42.16, 17.83, -9.06), "5H4": (42.16, -9.07, 17.83), "4H5": (-42.16, 9.07, -17.83),
                        "4H3": (-17.83, 9.07, -42.16), "3H4": (17.83, -9.07, 42.16), "3H2": (-9.07, 17.83, 42.16),
                        "2H3": (9.07, -17.83, -42.16), "2H1": (9.07, -42.16, -17.83), "1H2": (-9.07, 42.16, 17.83),
                        "B36": (35.26, 35.26, -74.2), "36B": (-35.26, -35.26, 74.2), "B25": (-74.20, 35.26, 35.26),
                        "25B": (74.20, -35.26, -35.26), "B14": (35.26, -74.20, 35.26), "14B": (-35.26, 74.20, -35.26),
                        "4C1": (-35.26, -35.26, -35.26), "1C4": (35.26, 35.26, 35.26), "P": (0.00, 0.00, 0.00)}
        self._TTnum = {"E6": 1, "6E": 2, "E5": 3, "5E": 4, "E4": 5, "4E": 6, "E3": 7, "3E": 8, "E2": 9, "2E": 10,
                       "E1": 11, "1E": 12, "2S6": 13, "6S2": 14, "1S5": 15, "5S1": 16, "3S1": 17, "1S3": 17, "1H6": 18,
                       "6H1": 19, "6H5": 20, "5H6": 21, "5H4": 22, "4H5": 23, "4H3": 24, "3H4": 25, "3H2": 26,
                       "2H3": 27, "2H1": 28, "1H2": 29, "B36": 30, "36B": 31, "B25": 32, "25B": 33, "B14": 34,
                       "14B": 35, "4C1": 36, "1C4": 37, "P": 38}

    def _init7(self):
        self._fmt = '%8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f'
        self._TTdict = {1: (-77.50192, 32.40371, -49.76511, 65.42500), 2: (77.50192, -32.40371, 49.76511, -65.42500),
                        3: (32.40371, -77.50192, 50.31823, 35.47121), 4: (-32.40371, 77.50192, -50.31823, -35.47121),
                        5: (60.84334, 1.17297, 29.27174, -78.24974), 6: (-60.84334, -1.17297, -29.27174, 78.24974),
                        7: (-60.65524, 78.70045, -60.65524, 0.00000), 8: (60.65524, -78.70045, 60.65524, 0.00000),
                        9: (-32.66638, -32.66638, 0.00000, 77.12168), 10: (32.66638, 32.66638, 0.00000, -77.12168),
                        11: (78.70045, -60.65524, 61.48592, -37.03982), 12: (-78.70045, 60.65524, -61.48592, 37.03982),
                        13: (1.17297, 60.84334, -29.12466, -60.82208), 14: (-1.17297, -60.84334, 29.12466, 60.82208),
                        15: (-54.35579, -30.97780, 70.78396, 0.65068), 16: (54.35579, 30.97780, -70.78396, -0.65068),
                        17: (71.29310, -30.68553, -53.87472, -0.60287), 18: (-71.29310, 30.68553, 53.87472, 0.60287),
                        19: (-30.68553, 71.29310, 54.19666, -33.13285), 20: (30.68553, -71.29310, -54.19666, 33.13285),
                        21: (-30.97780, -54.35579, -70.65310, 44.71937), 22: (30.97780, 54.35579, 70.65310, -44.71937),
                        23: (55.75935, 27.57775, 55.75935, 0.00000), 24: (-55.75935, -27.57775, -55.75935, 0.00000),
                        25: (-35.44850, -35.44850, 0.00000, -38.42127), 26: (35.44850, 35.44850, 0.00000, 38.42127),
                        27: (27.57775, 55.75935, -57.32676, 33.96153), 28: (-27.57775, -55.75935, 57.32676, -33.96153),
                        29: (-17.13184, -48.15510, 14.81912, 70.64266), 30: (17.13184, 48.15510, -14.81912, -70.64266),
                        31: (80.68790, -47.04433, 57.53897, -53.15196), 32: (-80.68790, 47.04433, -57.53897, 53.15196),
                        33: (-16.08891, 70.42456, -41.09076, -49.32166), 34: (16.08891, -70.42456, 41.09076, 49.32166),
                        35: (-70.42456, 16.08891, -40.65824, 73.72534), 36: (70.42456, -16.08891, 40.65824, -73.72534),
                        37: (47.04433, -80.68790, 57.14694, 18.55392), 38: (-47.04433, 80.68790, -57.14694, -18.55392),
                        39: (48.15510, 17.13184, 14.97718, -79.52547), 40: (-48.15510, -17.13184, -14.97718, 79.52547),
                        41: (-71.86272, 71.86272, -61.82503, 18.75908), 42: (71.86272, -71.86272, 61.82503, -18.75908),
                        43: (56.51677, 34.60064, 73.13733, -31.51102), 44: (-56.51677, -34.60064, -73.13733, 31.51102),
                        45: (-48.50386, -21.04445, -34.76145, -27.06592), 46: (48.50386, 21.04445, 34.76145, 27.06592),
                        47: (21.04445, 48.50386, -34.81829, 47.68243), 48: (-21.04445, -48.50386, 34.81829, -47.68243),
                        49: (-34.60064, -56.51677, 74.94603, -15.03468), 50: (34.60064, 56.51677, -74.94603, 15.03468),
                        51: (71.20159, 3.42804, -59.71206, -14.56853), 52: (-71.20159, -3.42804, 59.71206, 14.56853),
                        53: (-63.16443, 63.16443, 45.49329, -13.52829), 54: (63.16443, -63.16443, -45.49329, 13.52829),
                        55: (-3.42804, -71.20159, -61.43118, 51.46177), 56: (3.42804, 71.20159, 61.43118, -51.46177),
                        57: (-67.63902, -13.41602, 21.49166, 58.37633), 58: (67.63902, 13.41602, -21.49166, -58.37633),
                        59: (75.85689, -75.85689, 13.92493, -4.01711), 60: (-75.85689, 75.85689, -13.92493, 4.01711),
                        61: (13.41602, 67.63902, 22.73623, -71.27524), 62: (-13.41602, -67.63902, -22.73623, 71.27524),
                        63: (-77.83523, 10.75720, -75.34012, 50.68680), 64: (77.83523, -10.75720, 75.34012, -50.68680),
                        65: (36.69794, -32.42743, 42.72177, 43.69378), 66: (-36.69794, 32.42743, -42.72177, -43.69378),
                        67: (32.42743, -36.69794, 43.20896, -69.63493), 68: (-32.42743, 36.69794, -43.20896, 69.63493),
                        69: (-10.75720, 77.83523, -72.25213, -4.45489), 70: (10.75720, -77.83523, 72.25213, 4.45489),
                        71: (0.00000, 0.00000, 0.00000, 0.00000, 0.00000)}
        self._TTnum = {1: '7Bzz-1', 2: '7Bzz-2', 3: '7Bzz-3', 4: '7Bzz-4', 5: '7Bzz-5', 6: '7Bzz-6', 7: '7Bzz-7',
                       8: '7Bzz-8', 9: '7Bzz-9', 10: '7Bzz-10', 11: '7Bzz-11', 12: '7Bzz-12', 13: '7Bzz-13',
                       14: '7Bzz-14', 15: '7Czz-1', 16: '7Czz-2', 17: '7Czz-3', 18: '7Czz-4', 19: '7Czz-5',
                       20: '7Czz-6', 21: '7Czz-7', 22: '7Czz-8', 23: '7Czz-9', 24: '7Czz-10', 25: '7Czz-11',
                       26: '7Czz-12', 27: '7Czz-13', 28: '7Czz-14', 29: '7TBz-1', 30: '7TBz-2', 31: '7TBz-3',
                       32: '7TBz-4', 33: '7TBz-5', 34: '7TBz-6', 35: '7TBz-7', 36: '7TBz-8', 37: '7TBz-9',
                       38: '7TBz-10', 39: '7TBz-11', 40: '7TBz-12', 41: '7TBz-13', 42: '7TBz-14', 43: '7TCz-1',
                       44: '7TCz-2', 45: '7TCz-3', 46: '7TCz-4', 47: '7TCz-5', 48: '7TCz-6', 49: '7TCz-7', 50: '7TCz-8',
                       51: '7TCz-9', 52: '7TCz-10', 53: '7TCz-11', 54: '7TCz-12', 55: '7TCz-13', 56: '7TCz-14',
                       57: '7TS3-1', 58: '7TS3-2', 59: '7TS3-3', 60: '7TS3-4', 61: '7TS3-5', 62: '7TS3-6', 63: '7TS3-7',
                       64: '7TS3-8', 65: '7TS3-9', 66: '7TS3-10', 67: '7TS3-11', 68: '7TS3-12', 69: '7TS3-13',
                       70: '7TS3-14', 71: 'P'}
        self._map = {'7TBz-2': 'TB ', '7Bzz-8': 'B  ', '7Bzz-9': 'B  ', '7Bzz-6': 'B  ', '7Bzz-7': 'B  ',
                     '7Bzz-4': 'B  ', '7Bzz-5': 'B  ', '7Bzz-2': 'B  ', '7Bzz-3': 'B  ', '7TBz-10': 'TB ',
                     '7Bzz-1': 'B  ', '7TS3-4': 'TS3', '7TCz-10': 'TC ', '7TS3-5': 'TS3', '7TBz-6': 'TB ',
                     '7TCz-9': 'TC ', '7TCz-8': 'TC ', '7TCz-7': 'TC ', '7TCz-6': 'TC ', '7TCz-5': 'TC ',
                     '7TCz-4': 'TC ', '7TCz-3': 'TC ', '7TCz-2': 'TC ', '7TCz-1': 'TC ', '7TS3-10': 'TS3',
                     '7TS3-11': 'TS3', '7TS3-12': 'TS3', '7TS3-13': 'TS3', '7TS3-14': 'TS3', '7TBz-14': 'TB ',
                     '7TS3-6': 'TS3', '7Czz-14': 'C  ', '7Czz-13': 'C  ', '7Czz-12': 'C  ', '7Czz-11': 'C  ',
                     '7Czz-10': 'C  ', '7TS3-7': 'TS3', '7TBz-12': 'TB ', '7TCz-14': 'TC ', '7TCz-13': 'TC ',
                     '7TCz-12': 'TC ', '7TCz-11': 'TC ', '7TBz-13': 'TB ', '7Czz-7': 'C  ', '7Czz-6': 'C  ',
                     '7Czz-5': 'C  ', '7Czz-4': 'C  ', '7Czz-3': 'C  ', '7Czz-2': 'C  ', '7Czz-1': 'C  ',
                     '7TBz-3': 'TB ', '7TBz-11': 'TB ', '7TBz-8': 'TB ', '7TBz-9': 'TB ', '7Czz-9': 'C  ',
                     '7Czz-8': 'C  ', '7TBz-4': 'TB ', '7TS3-8': 'TS3', '7TS3-9': 'TS3', '7TBz-5': 'TB ',
                     '7Bzz-14': 'B  ', '7TS3-3': 'TS3', '7TS3-1': 'TS3', '7Bzz-10': 'B  ', '7Bzz-11': 'B  ',
                     '7Bzz-12': 'B  ', '7Bzz-13': 'B  ', '7TS3-2': 'TS3', '7TBz-7': 'TB ', '7TBz-1': 'TB ', 'P': 'P'}

    def _init8(self):
        self._fmt = '%8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f %8.6f'
        self._TTdict = {1: (-29.78641, -29.78641, -29.78641, -29.78641, 89.26168),
                        2: (29.78641, 29.78641, 29.78641, 29.78641, -89.26168),
                        3: (74.02437, -74.02437, 74.02437, -74.02437, 0.00000),
                        4: (-74.02437, 74.02437, -74.02437, 74.02437, 0.00000),
                        5: (25.12550, 70.07297, -86.70206, 70.07297, 0.00000),
                        6: (-25.12550, -70.07297, 86.70206, -70.07297, 0.00000),
                        7: (-80.27601, -7.61403, -7.61403, -80.27601, 67.51024),
                        8: (80.27601, 7.61403, 7.61403, 80.27601, -67.51024),
                        9: (70.07297, -86.70206, 70.07297, 25.12550, 0.00000),
                        10: (-70.07297, 86.70206, -70.07297, -25.12550, 0.00000),
                        11: (36.92654, 36.92654, -35.62407, -35.62407, -62.15863),
                        12: (-36.92654, -36.92654, 35.62407, 35.62407, 62.15863),
                        13: (-86.70206, 70.07297, 25.12550, 70.07297, 0.00000),
                        14: (86.70206, -70.07297, -25.12550, -70.07297, 0.00000),
                        15: (-7.61403, -80.27601, -80.27601, -7.61403, 67.51024),
                        16: (7.61403, 80.27601, 80.27601, 7.61403, -67.51024),
                        17: (70.07297, 25.12550, 70.07297, -86.70206, 0.00000),
                        18: (-70.07297, -25.12550, -70.07297, 86.70206, 0.00000),
                        19: (-35.62407, -35.62407, 36.92654, 36.92654, -62.15863),
                        20: (35.62407, 35.62407, -36.92654, -36.92654, 62.15863),
                        21: (-30.72856, 78.11269, -30.72856, 78.11269, -69.25804),
                        22: (30.72856, -78.11269, 30.72856, -78.11269, 69.25804),
                        23: (-78.11269, 30.72856, -78.11269, 30.72856, 69.25804),
                        24: (78.11269, -30.72856, 78.11269, -30.72856, -69.25804),
                        25: (79.67871, 31.92012, -79.67871, -31.92012, 0.00000),
                        26: (-79.67871, -31.92012, 79.67871, 31.92012, 0.00000),
                        27: (-79.67871, 31.92012, 79.67871, -31.92012, 0.00000),
                        28: (79.67871, -31.92012, -79.67871, 31.92012, 0.00000),
                        29: (31.92012, -79.67871, -31.92012, 79.67871, 0.00000),
                        30: (-31.92012, 79.67871, 31.92012, -79.67871, 0.00000),
                        31: (31.92012, 79.67871, -31.92012, -79.67871, 0.00000),
                        32: (-31.92012, -79.67871, 31.92012, 79.67871, 0.00000),
                        33: (46.43672, 46.43672, 46.43672, 46.43672, 0.00000),
                        34: (-46.43672, -46.43672, -46.43672, -46.43672, 0.00000),
                        35: (84.52038, 9.49665, -44.90659, -51.54107, -34.52284),
                        36: (-84.52038, -9.49665, 44.90659, 51.54107, 34.52284),
                        37: (-72.02550, 74.57808, 67.74998, 13.82080, -31.37154),
                        38: (72.02550, -74.57808, -67.74998, -13.82080, 31.37154),
                        39: (-13.82080, -67.74998, -74.57808, 72.02550, 31.37154),
                        40: (13.82080, 67.74998, 74.57808, -72.02550, -31.37154),
                        41: (51.54107, 44.90659, -9.49665, -84.52038, 34.52284),
                        42: (-51.54107, -44.90659, 9.49665, 84.52038, -34.52284),
                        43: (-44.90659, -51.54107, 84.52038, 9.49665, -34.52284),
                        44: (44.90659, 51.54107, -84.52038, -9.49665, 34.52284),
                        45: (67.74998, 13.82080, -72.02550, 74.57808, -31.37154),
                        46: (-67.74998, -13.82080, 72.02550, -74.57808, 31.37154),
                        47: (-74.57808, 72.02550, -13.82080, -67.74998, 31.37154),
                        48: (74.57808, -72.02550, 13.82080, 67.74998, -31.37154),
                        49: (-9.49665, -84.52038, 51.54107, 44.90659, 34.52284),
                        50: (9.49665, 84.52038, -51.54107, -44.90659, -34.52284),
                        51: (38.65923, 68.40284, 38.65923, 68.40284, -19.82499),
                        52: (-38.65923, -68.40284, -38.65923, -68.40284, 19.82499),
                        53: (-68.40284, -38.65923, -68.40284, -38.65923, 19.82499),
                        54: (68.40284, 38.65923, 68.40284, 38.65923, -19.82499),
                        55: (55.38745, 25.68480, 55.38745, 25.68480, 16.89077),
                        56: (-55.38745, -25.68480, -55.38745, -25.68480, -16.89077),
                        57: (-25.68480, -55.38745, -25.68480, -55.38745, -16.89077),
                        58: (25.68480, 55.38745, 25.68480, 55.38745, 16.89077),
                        59: (7.34854, -82.58074, -34.61746, -79.39169, 55.30954),
                        60: (-7.34854, 82.58074, 34.61746, 79.39169, -55.30954),
                        61: (79.39169, 34.61746, 82.58074, -7.34854, -55.30954),
                        62: (-79.39169, -34.61746, -82.58074, 7.34854, 55.30954),
                        63: (-62.32176, 0.86048, -45.33422, 42.63742, -44.65443),
                        64: (62.32176, -0.86048, 45.33422, -42.63742, 44.65443),
                        65: (-0.86048, 62.32176, -42.63742, 45.33422, 44.65443),
                        66: (0.86048, -62.32176, 42.63742, -45.33422, -44.65443),
                        67: (-34.61746, -79.39169, 7.34854, -82.58074, 55.30954),
                        68: (34.61746, 79.39169, -7.34854, 82.58074, -55.30954),
                        69: (82.58074, -7.34854, 79.39169, 34.61746, -55.30954),
                        70: (-82.58074, 7.34854, -79.39169, -34.61746, 55.30954),
                        71: (-45.33422, 42.63742, -62.32176, 0.86048, -44.65443),
                        72: (45.33422, -42.63742, 62.32176, -0.86048, 44.65443),
                        73: (-42.63742, 45.33422, -0.86048, 62.32176, 44.65443),
                        74: (42.63742, -45.33422, 0.86048, -62.32176, -44.65443),
                        75: (-85.64878, 23.99643, 30.46456, 67.92169, 22.44158),
                        76: (85.64878, -23.99643, -30.46456, -67.92169, -22.44158),
                        77: (39.58368, -81.16460, -73.88305, -19.82142, 52.52672),
                        78: (-39.58368, 81.16460, 73.88305, 19.82142, -52.52672),
                        79: (39.41702, 45.72430, 83.89598, -78.70292, -21.74106),
                        80: (-39.41702, -45.72430, -83.89598, 78.70292, 21.74106),
                        81: (-45.56607, -37.39456, 16.56783, 75.46062, -51.37974),
                        82: (45.56607, 37.39456, -16.56783, -75.46062, 51.37974),
                        83: (30.46456, 67.92169, -85.64878, 23.99643, 22.44158),
                        84: (-30.46456, -67.92169, 85.64878, -23.99643, -22.44158),
                        85: (-73.88305, -19.82142, 39.58368, -81.16460, 52.52672),
                        86: (73.88305, 19.82142, -39.58368, 81.16460, -52.52672),
                        87: (83.89598, -78.70292, 39.41702, 45.72430, -21.74106),
                        88: (-83.89598, 78.70292, -39.41702, -45.72430, 21.74106),
                        89: (16.56783, 75.46062, -45.56607, -37.39456, -51.37974),
                        90: (-16.56783, -75.46062, 45.56607, 37.39456, 51.37974),
                        91: (60.43454, -60.43454, -60.43454, 60.43454, 0.00000),
                        92: (-60.43454, 60.43454, 60.43454, -60.43454, 0.00000),
                        93: (0.00000, 88.05935, 0.00000, -88.05935, 0.00000),
                        94: (0.00000, -88.05935, 0.00000, 88.05935, 0.00000),
                        95: (-60.43454, -60.43454, 60.43454, 60.43454, 0.00000),
                        96: (60.43454, 60.43454, -60.43454, -60.43454, 0.00000),
                        97: (88.05935, 0.00000, -88.05935, 0.00000, 0.00000),
                        98: (-88.05935, 0.00000, 88.05935, 0.00000, 0.00000),
                        99: (-20.13975, -56.34027, -56.34027, -20.13975, 85.60396),
                        100: (20.13975, 56.34027, 56.34027, 20.13975, -85.60396),
                        101: (75.79678, -30.95602, 75.79678, -88.86847, 0.00000),
                        102: (-75.79678, 30.95602, -75.79678, 88.86847, 0.00000),
                        103: (-0.67245, -0.67245, 37.69431, 37.69431, -83.24564),
                        104: (0.67245, 0.67245, -37.69431, -37.69431, 83.24564),
                        105: (-30.95602, 75.79678, -88.86847, 75.79678, 0.00000),
                        106: (30.95602, -75.79678, 88.86847, -75.79678, 0.00000),
                        107: (-56.34027, -20.13975, -20.13975, -56.34027, 85.60396),
                        108: (56.34027, 20.13975, 20.13975, 56.34027, -85.60396),
                        109: (75.79678, -88.86847, 75.79678, -30.95602, 0.00000),
                        110: (-75.79678, 88.86847, -75.79678, 30.95602, 0.00000),
                        111: (37.69431, 37.69431, -0.67245, -0.67245, -83.24564),
                        112: (-37.69431, -37.69431, 0.67245, 0.67245, 83.24564),
                        113: (-88.86847, 75.79678, -30.95602, 75.79678, 0.00000),
                        114: (88.86847, -75.79678, 30.95602, -75.79678, 0.00000), 115: (0.0, 0.0, 0.0, 0.0, 0.0)}
        self._TTnum = {1: '8BBzzz-1', 2: '8BBzzz-1-neg1', 3: '8BBzzz-2', 4: '8BBzzz-2-neg1', 5: '8BCzzz-1',
                       6: '8BCzzz-1-neg1', 7: '8BCzzz-2', 8: '8BCzzz-2-neg1', 9: '8BCzzz-3', 10: '8BCzzz-3-neg1',
                       11: '8BCzzz-4', 12: '8BCzzz-4-neg1', 13: '8BCzzz-5', 14: '8BCzzz-5-neg1', 15: '8BCzzz-6',
                       16: '8BCzzz-6-neg1', 17: '8BCzzz-7', 18: '8BCzzz-7-neg1', 19: '8BCzzz-8', 20: '8BCzzz-8-neg1',
                       21: '8boatz-1', 22: '8boatz-1-neg1', 23: '8boatz-2', 24: '8boatz-2-neg1', 25: '8chair-1',
                       26: '8chair-1-neg1', 27: '8chair-2', 28: '8chair-2-neg1', 29: '8chair-3', 30: '8chair-3-neg1',
                       31: '8chair-4', 32: '8chair-4-neg1', 33: '8Crown-1', 34: '8Crown-1-neg1', 35: '8TBCzz-1',
                       36: '8TBCzz-1-neg1', 37: '8TBCzz-2', 38: '8TBCzz-2-neg1', 39: '8TBCzz-3', 40: '8TBCzz-3-neg1',
                       41: '8TBCzz-4', 42: '8TBCzz-4-neg1', 43: '8TBCzz-5', 44: '8TBCzz-5-neg1', 45: '8TBCzz-6',
                       46: '8TBCzz-6-neg1', 47: '8TBCzz-7', 48: '8TBCzz-7-neg1', 49: '8TBCzz-8', 50: '8TBCzz-8-neg1',
                       51: '8TCCzz-1', 52: '8TCCzz-1-neg1', 53: '8TCCzz-2', 54: '8TCCzz-2-neg1', 55: '8TCCzz-3',
                       56: '8TCCzz-3-neg1', 57: '8TCCzz-4', 58: '8TCCzz-4-neg1', 59: '8TS1zz-1', 60: '8TS1zz-1-neg1',
                       61: '8TS1zz-2', 62: '8TS1zz-2-neg1', 63: '8TS1zz-3', 64: '8TS1zz-3-neg1', 65: '8TS1zz-4',
                       66: '8TS1zz-4-neg1', 67: '8TS1zz-5', 68: '8TS1zz-5-neg1', 69: '8TS1zz-6', 70: '8TS1zz-6-neg1',
                       71: '8TS1zz-7', 72: '8TS1zz-7-neg1', 73: '8TS1zz-8', 74: '8TS1zz-8-neg1', 75: '8TS2zz-1',
                       76: '8TS2zz-1-neg1', 77: '8TS2zz-2', 78: '8TS2zz-2-neg1', 79: '8TS2zz-3', 80: '8TS2zz-3-neg1',
                       81: '8TS2zz-4', 82: '8TS2zz-4-neg1', 83: '8TS2zz-5', 84: '8TS2zz-5-neg1', 85: '8TS2zz-6',
                       86: '8TS2zz-6-neg1', 87: '8TS2zz-7', 88: '8TS2zz-7-neg1', 89: '8TS2zz-8', 90: '8TS2zz-8-neg1',
                       91: '8TS3zz-1', 92: '8TS3zz-1-neg1', 93: '8TS3zz-2', 94: '8TS3zz-2-neg1', 95: '8TS3zz-3',
                       96: '8TS3zz-3-neg1', 97: '8TS3zz-4', 98: '8TS3zz-4-neg1', 99: '8TS4zz-1', 100: '8TS4zz-1-neg1',
                       101: '8TS4zz-2', 102: '8TS4zz-2-neg1', 103: '8TS4zz-3', 104: '8TS4zz-3-neg1', 105: '8TS4zz-4',
                       106: '8TS4zz-4-neg1', 107: '8TS4zz-5', 108: '8TS4zz-5-neg1', 109: '8TS4zz-6',
                       110: '8TS4zz-6-neg1', 111: '8TS4zz-7', 112: '8TS4zz-7-neg1', 113: '8TS4zz-8',
                       114: '8TS4zz-8-neg1', 115: 'P'}
        self._map = {'8BCzzz-1-neg1': 'BC ', '8TS1zz-7-neg1': 'TS1', '8TS1zz-8-neg1': 'TS1', '8BCzzz-7-neg1': 'BC ',
                     '8BBzzz-2-neg1': 'BB ', '8TBCzz-6-neg1': 'TBC', '8TS1zz-1-neg1': 'TS1', '8TS1zz-7': 'TS1',
                     '8TS1zz-6': 'TS1', '8TS1zz-5': 'TS1', '8TS1zz-4': 'TS1', '8TS1zz-3': 'TS1', '8TS1zz-2': 'TS1',
                     '8TS1zz-1': 'TS1', '8chair-4-neg1': 'C  ', '8TCCzz-1': 'TCC', '8TS1zz-5-neg1': 'TS1',
                     '8TCCzz-3': 'TCC', '8TCCzz-2': 'TCC', '8TCCzz-4': 'TCC', '8TS1zz-8': 'TS1', '8boatz-2-neg1': 'B  ',
                     '8TS2zz-1-neg1': 'TS2', '8chair-1': 'C  ', '8chair-2': 'C  ', '8chair-3': 'C  ', '8chair-4': 'C  ',
                     '8TS3zz-4-neg1': 'TS3', '8TBCzz-2': 'TBC', '8TBCzz-3': 'TBC', '8TBCzz-1': 'TBC', '8TBCzz-6': 'TBC',
                     '8TBCzz-7': 'TBC', '8TBCzz-4': 'TBC', '8TBCzz-5': 'TBC', '8TBCzz-8': 'TBC', '8TS4zz-4-neg1': 'TS4',
                     '8TS4zz-5-neg1': 'TS4', '8TS1zz-2-neg1': 'TS1', '8TBCzz-2-neg1': 'TBC', '8TS1zz-3-neg1': 'TS1',
                     '8TS4zz-7-neg1': 'TS4', '8BCzzz-5-neg1': 'BC ', '8BCzzz-4-neg1': 'BC ', '8TS2zz-6-neg1': 'TS2',
                     '8TS1zz-4-neg1': 'TS1', '8TBCzz-7-neg1': 'TBC', '8BBzzz-1': 'BB ', '8BBzzz-2': 'BB ',
                     '8BCzzz-8-neg1': 'BC ', '8TCCzz-2-neg1': 'TCC', '8TS2zz-8-neg1': 'TS2', '8chair-3-neg1': 'C  ',
                     '8chair-1-neg1': 'C  ', '8TBCzz-5-neg1': 'TBC', '8TBCzz-3-neg1': 'TBC', '8TCCzz-4-neg1': 'TCC',
                     '8TS2zz-3-neg1': 'TS2', '8TBCzz-8-neg1': 'TBC', '8BCzzz-2-neg1': 'BC ', '8TS2zz-2-neg1': 'TS2',
                     '8TS2zz-4-neg1': 'TS2', '8TS4zz-3-neg1': 'TS4', '8TS4zz-1-neg1': 'TS4', '8TS3zz-1': 'TS3',
                     '8TS3zz-3': 'TS3', '8TS3zz-2': 'TS3', '8TS3zz-4': 'TS3', '8TS4zz-6-neg1': 'TS4',
                     '8TS2zz-7-neg1': 'TS2', '8boatz-2': 'B  ', '8boatz-1': 'B  ', '8TS4zz-2-neg1': 'TS4',
                     '8boatz-1-neg1': 'B  ', '8TS1zz-6-neg1': 'TS1', '8TBCzz-4-neg1': 'TBC', '8chair-2-neg1': 'C  ',
                     '8BCzzz-6': 'BC ', '8BCzzz-7': 'BC ', '8BCzzz-4': 'BC ', '8BCzzz-5': 'BC ', '8BCzzz-2': 'BC ',
                     '8BCzzz-3': 'BC ', '8BCzzz-1': 'BC ', '8BCzzz-8': 'BC ', '8BBzzz-1-neg1': 'BB ',
                     '8TCCzz-1-neg1': 'TCC', '8TS4zz-2': 'TS4', '8TS4zz-3': 'TS4', '8Crown-1': 'CWN', '8TS4zz-6': 'TS4',
                     '8TS4zz-7': 'TS4', '8TS4zz-4': 'TS4', '8TS4zz-5': 'TS4', '8TS4zz-8': 'TS4', '8BCzzz-6-neg1': 'BC ',
                     '8TS2zz-5-neg1': 'TS2', '8TBCzz-1-neg1': 'TBC', '8TS4zz-8-neg1': 'TS4', '8TS3zz-2-neg1': 'TS3',
                     '8TS3zz-3-neg1': 'TS3', '8TS4zz-1': 'TS4', '8BCzzz-3-neg1': 'BC ', '8Crown-1-neg1': 'CWN',
                     '8TS2zz-1': 'TS2', '8TS2zz-2': 'TS2', '8TS2zz-3': 'TS2', '8TS2zz-4': 'TS2', '8TS2zz-5': 'TS2',
                     '8TS2zz-6': 'TS2', '8TS2zz-7': 'TS2', '8TS2zz-8': 'TS2', '8TCCzz-3-neg1': 'TCC',
                     '8TS3zz-1-neg1': 'TS3', 'P': 'P'}

    def calculate_triangular_tessellation(self):
        """docstring for calculate_triangular_tessellation"""
        calcoptions = {5: self._calc5, 6: self._calc6, 7: self._calc7, 8: self._calc8}
        self._calculatedtt = calcoptions[self._ringsize]()
        return self._calculatedtt

    def _calc5(self):
        """docstring for calculate_triangular_tessellation 5 """
        formatted = self._fmt % self._coords
        return calctt_pucker(formatted, self._ringsize)

    def _calc6(self):
        """docstring for calculate_triangular_tessellation 6 """
        # for now just call global calcHR use dims=3
        formatted = self._fmt % self._coords
        return calctt_pucker(formatted, self._ringsize)

    def _calc7(self):
        """docstring for calculate_triangular_tessellation 7 """
        formatted = self._fmt % self._coords
        return calctt_pucker(formatted, self._ringsize)

    def _calc8(self):
        """docstring for calculate_triangular_tessellation 8 """
        formatted = self._fmt % self._coords
        return calctt_pucker(formatted, self._ringsize)

    def deduce_canonical_conformation(self, oldbehaviour=False, nextguess=False):
        """Return canonical conf, delx,dely,del*, dist"""
        confoptions = {5: self._conf5, 6: self._conf6, 7: self._conf7, 8: self._conf8}
        if self._calculatedtt is not None:
            return confoptions[self._ringsize](self._calculatedtt, oldbehaviour, nextguess)
        else:
            return confoptions[self._ringsize](self.calculate_triangular_tessellation(), oldbehaviour, nextguess)

    def _conf5(self, tupin, oldbehaviour=False, nextguess=False):
        """ Return canonical conf, delx,dely, shortest perp dist, square dist"""
        rads = tupin
        listofdiff = []
        for key, itm in self._TTdict.items():
            x = itm[0] - rads[0]
            y = itm[1] - rads[1]
            if key == "P":
                shortestdist = math.sqrt(x * x + y * y)
                py = math.sqrt(x * x + y * y)
            else:
                py = math.sqrt(x * x + y * y)
                shortestdist = math.fabs((itm[0]) * (-1. * rads[1]) - (-1. * rads[0]) * (itm[1])) / math.sqrt(
                    itm[0] * itm[0] + itm[1] * itm[1])
            listofdiff.append((key, x, y, shortestdist, py))
        # sort by x2y2 distance
        ma = sorted(listofdiff, key=lambda dist: dist[4])
        # when using this Planar may be chosen incorrectly
        if (ma[0][0] == "P") and (ma[0][4] < 15.0):
            if ma[0][4] < 4.0:
                # return planar from list
                return ma[0]
            else:
                logger.debug(
                    "Return UAP conformer as conformer is almost planar but not quite within the error margins: %s",
                    ma[0])
                return "UAP", 0.0, 0.0, 0.0
        else:
            # pop first item from list to be destroyed
            logger.debug("Popping first item to be destroyed as it does not meet conditions: %s", ma[0])
            ma.pop()

        # now use the shortest deviation to resort the first four items..
        ma2 = [ma[0], ma[1], ma[2], ma[3], ma[4]]
        ma3 = sorted(ma2, key=lambda dist: dist[3])
        if ma3[0][3] > 3.5 and oldbehaviour:
            return "UAS", 0.0, 0.0, 0.0
        if (nextguess) and (ma[0][4] > 13.0):  # hardcoded parameter :(
            return ma3[1]
        return ma3[0]

    def _conf6(self, tupin, oldbehaviour=False, nextguess=False):
        """docstring for deduce_canonical_conformation 6"""
        rads = tupin

        listofdiff = []
        for key, itm in self._TTdict.items():
            x = itm[0] - rads[0]
            y = itm[1] - rads[1]
            z = itm[2] - rads[2]
            py = math.sqrt(x * x + y * y + z * z)
            listofdiff.append((key, x, y, z, py))
        ma = sorted(listofdiff, key=lambda dist: dist[4])
        # if deviations from planar then
        if (ma[0][0] == "P") and (ma[0][4] > 13.0):
            # deviations from planar that are not negligible (especially for macrocycles where the radius of the cycle is large)
            logger.debug(
                "deviations from planar that are not negligible (especially for macrocycles where the radius of the cycle is large). Ignore %s , return %s",
                ma[0], ma[1])
            return ma[1]

        if oldbehaviour:
            return ma[0]

        if (nextguess) and (ma[0][4] > 13.0):  # hardcoded parameter which is map dependent :(
            logger.debug("deviations that are not negligible and nextguess set to true. Ignore %s , return %s", ma[0],
                         ma[1])
            return ma[1]

        return ma[0]

    def _conf7(self, tupin, oldbehaviour=False, nextguess=False):
        """docstring for deduce_canonical_conformation 7"""
        rads = tupin

        listofdiff = []
        for key, itm in self._TTdict.items():
            x = itm[0] - rads[0]
            y = itm[1] - rads[1]
            z = itm[2] - rads[2]
            w = itm[3] - rads[3]
            py = math.sqrt(x * x + y * y + z * z + w * w)
            listofdiff.append((self._map[self._TTnum[key]], x, y, z, w, py))
        ma = sorted(listofdiff, key=lambda dist: dist[5])
        if (ma[0][0] == "P") and (ma[0][5] > 11.0):
            # deviations from planar that are not negligible (especially for macrocycles where the radius of the cycle is large)
            logger.debug(
                "deviations from planar that are not negligible (especially for macrocycles where the radius of the cycle is large). Ignore %s , return %s",
                ma[0], ma[1])
            return ma[1]
        if oldbehaviour:
            return ma[0]
        if (nextguess) and (ma[0][5] > 13.0):  # hardcoded parameter which is map dependent :(
            logger.debug("deviations that are not negligible and nextguess set to true. Ignore %s , return %s", ma[0],
                         ma[1])
            return ma[1]
        return ma[0]

    def _conf8(self, tupin, oldbehaviour=False, nextguess=False):
        """docstring for deduce_canonical_conformation 8"""
        rads = tupin

        listofdiff = []
        for key, itm in self._TTdict.items():
            x = itm[0] - rads[0]
            y = itm[1] - rads[1]
            z = itm[2] - rads[2]
            v = itm[3] - rads[3]
            w = itm[4] - rads[4]
            py = math.sqrt(x * x + y * y + z * z + v * v + w * w)
            listofdiff.append((self._map[self._TTnum[key]], x, y, z, v, w, py))
        ma = sorted(listofdiff, key=lambda dist: dist[6])
        if (ma[0][0] == "P") and (ma[0][5] > 11.0):
            # deviations from planar that are not negligible (especially for macrocycles where the radius of the cycle is large)
            logger.debug(
                "deviations from planar that are not negligible (especially for macrocycles where the radius of the cycle is large). Ignore %s , return %s",
                ma[0], ma[1])
            return ma[1]
        if oldbehaviour:
            return ma[0]
        if (nextguess) and (ma[0][6] > 13.0):  # hardcoded parameter which is map dependent :(
            logger.debug("deviations that are not negligible and nextguess set to true. Ignore %s , return %s", ma[0],
                         ma[1])
            return ma[1]
        return ma[0]

    def contextualise_conformer(self, conformer, ring):
        """The conformer choice depends on the ring atom ordering and direction. If this was not deduced then the guessed ring conformer will not seem appropriate. Use the ring atom names and the guessed conformer to provide a better guess (read in the guessed conformer just in case :) )"""
        contoptions = {5: self._cont5, 6: self._cont6, 7: self._cont7, 8: self._cont8}
        return contoptions[self._ringsize](conformer, ring)

    def _cont5(self, conformer, ring):
        """docstring for contextualise conformer 5 """
        ordering = {'2': ring[0], '3': ring[1], '4': ring[2], '5': ring[3], '1': ring[4]}
        # . note this choice is based on the string length and name inside conformer e.g. UAS, 1T2, P etc.
        if len(conformer) > 2:
            if conformer[0] == 'U':
                return conformer
            else:
                return ''.join([ordering[conformer[0]], '|T|', ordering[conformer[2]]])
        elif len(conformer) < 2:  # no error check, assume this is P
            return '|P|'
        else:  # it's an E
            if conformer[0] == 'E':
                return ''.join(['|E|', ordering[conformer[1]]])
            else:
                return ''.join([ordering[conformer[0]], '|E|'])

    def _cont6(self, conformer, ring):
        """docstring for contextualise conformer 6 """
        ordering = {'3': ring[0], '4': ring[1], '5': ring[2], '6': ring[3], '1': ring[4], '2': ring[5]}
        # . note this choice is based on the string length and name inside conformer e.g. 1C4, 1T2, P etc.
        if len(conformer) > 2:
            if conformer[0] == 'B':
                return ''.join(['|B|', ordering[conformer[1]], ordering[conformer[2]]])
            elif conformer[1] == 'C':
                return ''.join([ordering[conformer[0]], '|C|', ordering[conformer[2]]])
            elif conformer[1] == 'H':
                return ''.join([ordering[conformer[0]], '|H|', ordering[conformer[2]]])
            elif conformer[1] == 'S':
                return ''.join([ordering[conformer[0]], '|S|', ordering[conformer[2]]])
            elif conformer[2] == 'B':
                return ''.join([ordering[conformer[0]], ordering[conformer[1]], '|B|'])
        elif len(conformer) < 2:  # no error check, assume this is P
            return '|P|'
        else:  # it's an E
            if conformer[0] == 'E':
                return ''.join(['|E|', ordering[conformer[1]]])
            else:
                return ''.join([ordering[conformer[0]], '|E|'])

    def _cont7(self, conformer, ring):
        """docstring for contextualise conformer 7 """
        return conformer

    def _cont8(self, conformer, ring):
        """docstring for contextualise conformer 8 """
        return conformer

    def rmsd(self, comparison_coords):
        """
        Calculate the RMSD of this conformer relative to the guessed conformer
        """
        if self._coords:
            if self._calculatedtt is None:
                self.calculate_triangular_tessellation()

            P = self.coords_array
            Q = comparison_coords
            # Calculate 'dumb' RMSD
            normal_rmsd = rmsd(P, Q)
            # Create the centroid of P and Q which is the geometric center of a
            # N-dimensional region and translate P and Q onto that center.
            # http://en.wikipedia.org/wiki/Centroid
            Pc = centroid(P)
            Qc = centroid(Q)
            P -= Pc
            Q -= Qc
            return kabsch(P, Q)

    @property
    def fmt(self):
        """I'm the 'fmt' property."""
        return self._fmt

    @fmt.setter
    def fmt(self, value):
        self._fmt = value

    @property
    def ttdict(self):
        """I'm the 'TTdict' property."""
        return self._TTdict

    @ttdict.setter
    def ttdict(self, value):
        self._TTdict = value

    @property
    def ringsize(self):
        """I'm the 'ringsize' property."""
        return self._ringsize

    @ringsize.setter
    def ringsize(self, value):
        self._ringsize = value

    @property
    def ttnum(self):
        """I'm the 'TTnum' property."""
        return self._TTnum

    @ttnum.setter
    def ttnum(self, value):
        self._TTnum = value

    @property
    def coords_array(self):
        if self._coords:
            return np.array(self._coords).reshape(len(self._coords) / 3, 3)

    @property
    def isvalid(self):
        if self._ringsize:
            return True
        else:
            return False


if __name__ == '__main__':
    # from pucker import Pucker

    print("Proper Unit tests are in tests, run using PyCharm")
    print("Non-definitive examples below :")
    examples = [Pucker((
        -2.060182, 0.212443, -0.286206, -1.612655, -0.195526, 1.185520, -1.469215, 1.164065, 1.933079, -1.873591,
        2.217447,
        1.020096, -1.910382, 1.749863, -0.358366))]
    examples.append(Pucker((
        -3.904, -4.906, 3.181, -3.576, -3.540, 3.944, -4.115, -3.556, 5.339, -5.551, -3.941, 5.380, -5.799, -5.308,
        4.847,
        -5.383, -5.328, 3.394)))
    examples.append(Pucker((
        1.41314, -0.58963, 0.00000, 0.65034, -0.87437, 1.29569, -0.67974, -0.11113, 1.43779, -0.67974, 1.27340, 0.77848,
        -0.67974, 1.27340, -0.77848, -0.67974, -0.11113, -1.43779, 0.65034, -0.87437, -1.29569)))
    examples.append(Pucker((
        1.31918, 1.31918, 0.00000, 0.00000, 1.53627, 0.75830, -1.31918, 1.31918, 0.00000, -1.53627, 0.00000, -0.75830,
        -1.31918, -1.31918, 0.00000, 0.00000, -1.53627, 0.75830, 1.31918, -1.31918, 0.00000, 1.53627, 0.00000,
        -0.75830)))
    for ring in examples:
        print(ring.deduce_canonical_conformation())
