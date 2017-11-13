"Classes that hold the genotype containers for individuals"


class ChromosomePair(object):
    "Holds a pair of AlleleContainers"
    __slots__ = ['chroms']

    def __init__(self, paternal, maternal):
        """
        Create the pair

        :param paternal: paternal chromatid
        :param maternal: maternal chromatid
        """
        self.chroms = paternal, maternal

    def __getitem__(self, key):
        return self.chroms[key]

    def __setitem__(self, key, value):
        self.chroms[key] = value

    def set_genotype(self, markidx, genotype):
        """
        Set an individual genotype.

        :param markidx: allele index
        :param allele: genotype pair
        :type markidx: int
        :type genotype: 2-tuple

        :rtype void:
        """

        a, b = genotype

        self.chroms[0][markidx] = a
        self.chroms[1][markidx] = b

    def get_genotype(self, markidx):
        """
        Get a genotype at an index

        :param markidx: allele index
        :type markidx: int

        :rtype: tuple
        """
        return self.chroms[0][markidx], self.chroms[1][markidx]


class GenotypeSet(object)
    """
    Holds a complement of AlleleContainers
    
    :ivar chroms: Allele containers
    :type chroms: list of ChromosomePairs
    """
    __slots__ = ['chroms']

    def __init__(self, chroms=None):
        self.chroms = chroms if chroms is not None else []

    def set_genotype(self, locus, genotype):
        """
        Set an individual genotype.

        :param markidx: chromosome and marker index
        :param allele: genotype pair
        :type markidx: tuple(int, int)
        :type genotype: tuple

        :rtype void:
        """
        chromidx, markidx = locus
        self.chroms[chromidx].set_genotype(markidx, genotype)