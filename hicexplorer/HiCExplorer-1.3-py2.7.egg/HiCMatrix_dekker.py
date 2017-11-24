import numpy as np
from bisect import *
import gzip


class hiCMatrix:
    """
    Class to handle HiC matrices
    contains routines to get intrachromosomal distances
    get sub matrices by chrname.
    """
    
    def __init__(self, matrixFile=None, skiprows=None):
        if matrixFile:
            self.getBins(matrixFile)
            if not skiprows:
                skiprows = len(self.header) + 1 # +1 to include the column labels
            self.matrix = np.loadtxt(matrixFile, skiprows=skiprows, usecols=range(1,self.numCols))

        # convert nans to zeros
        #self.matrix[np.where(np.isnan(self.matrix)==True)] = 0


    def getBins(self, fileName):
        """
        Reads a gziped HiC matrix in Decker's format
        and extracts:
        1. Number of bins (equal to number of rows and columns)
        2. A dictionary containing the chromosome boundaries (row indices)
        3. A list where chromosome positions are 
           mapped their respective bin
        4. The list of chromosome names found in the matrix
        5. A list, that has the same length as the number of bins
           having the chromosome name
        6. A list, that has the same length as the number of bins
           having the start position
        7. A list, that has the same length as the number of bins
           having the end position
        """

        i = 0
        numCols = None
        self.header = []
        try:
            for line in gzip.open(fileName, 'r').readlines():
              if line[0] == '#':
                  self.header.append(line)
                  continue
              i += 1
              if i == 1:
                  colLabels = line.split("\t")
                  numCols = len(colLabels)
                  nameList = []
                  startList = []
                  endList = []
                  binIdList = []

                  for lab in colLabels[1:]:
                      (binId, species, position) = lab.split("|")
                      (chrName, pos) = position.split(":")
                      (start, end) = pos.split("-")
                      binIdList.append(binId)
                      nameList.append(chrName)
                      startList.append(int(start))
                      endList.append(int(end))

                  self.mappedBins, \
                  self.chrNamesValue, \
                  self.chrBinBoundaries  = \
                      self.mapPositionsToBins(endList, nameList)


                  break

        except IOError:
            print "Error reading {}. Is the file gzipped?".format(fileName)

        self.chrNames = self.chrNamesValue.keys()
        self.numCols = numCols
        self.binIdList = np.array(binIdList)
        self.nameList = np.array(nameList)
        self.startList = np.array(startList)
        self.endList = np.array(endList)

    @staticmethod
    def mapPositionsToBins(endList, nameList):
        """
        This methods creates s special list that speeds up
        the identification of any bin that corresponds to a chr position.
        It stores each bin start position
        plus a value associated to each chromosome.

        If, for example there are two chromosomes with
        two bins as follows. Chr1 -> (300, 500), chr2 -> (150, 400)
        the mappedBins list will contain

        [300+chr1value, 500+chr1value, 150+chr2value, 400+chr2value]

        the chrvalues are asigned such that no overlap of number will occur
        and the list will continue to be ordered.

        Thus, nowing the chromosome value, inmediatly and bin index 
        could be retrieved for a given position.

        >>> nameList = ['chr4', 'chr4', 'chr4', 'chrM', 'chrX', 'chrX']
        >>> endList = [500001, 1000001, 1351857, 19517, 500001, 1000001]
        >>> mappedbins, chrNamesValue, chrBinBoundaries=hiCMatrix.mapPositionsToBins(endList, nameList)
        >>> mappedbins
        [500001, 1000001, 1351857, 1371374, 3203715, 3703715]

        >>> chrNamesValue
        {'chrM': 1351857, 'chr4': 0, 'chrX': 2703714}

        >>> chrBinBoundaries
        {'chrM': (3, 4), 'chr4': (0, 3), 'chrX': (4, 6)}
        """

        chrNames, chrNamesIndex  = np.unique(nameList, return_index=True)
        # the unique list of chrnames is not ordered as the
        # nameList. The following line orders the names properly
        chrNames = chrNames[np.argsort(chrNamesIndex)]
        chrNamesIndex = chrNamesIndex[np.argsort(chrNamesIndex)]

        """
        The chrNamesIndex list contains the first bin where the chrName
        occurs:

        chrNamesIndex
        array([  0,   3,   4,  49,  50,  51, 110, 131, 137, 193, 199, 249, 256,
        299, 300])

        chrNames
        array(['chr4', 'chrM', 'chrX', 'chrYHet', 'chrXHet', 'chrUextra', 'chrU',
        'chr3RHet', 'chr3R', 'chr3LHet', 'chr3L', 'chr2RHet', 'chr2R',
        'chr2LHet', 'chr2L'], 
        dtype='|S9')
        """

        # create a dictionary containing each chromosome name and 
        # and associated value
        maxChrLength = max(endList)
        chrNamesValue = dict( [  (chrNames[x], x*maxChrLength) 
                                 for x in range(0, len(chrNames)) ] )


        mappedBins = [ endList[x] + chrNamesValue[nameList[x]] for x in range(0, len(endList))  ]

        chrNamesIndex = np.append(chrNamesIndex,len(endList))
        # dictionary containing the bin boundaries
        chrBinBoundaries = dict( [ ( chrNames[x], (chrNamesIndex[x], chrNamesIndex[x+1]) )
                                   for x in range(0, len(chrNames)) ] )

        return (mappedBins, chrNamesValue, chrBinBoundaries)

    def getMatrix(self):
        return self.matrix

    def getChrBinRange(self, chrName):
        """
        Given a chromosome name,
        This functions return the start and end bin indices in the matrix
        """
        return self.chrBinBoundaries[chrName]

    def getBinPos(self, binIndex, includeBinId=False):
        """
        given a bin, it returns the chromosome name, start position and end position
        """
        if includeBinId:
            ret = (self.nameList[binIndex], self.startList[binIndex], self.endList[binIndex], self.nameList[binIndex] )
        else:
            ret =(self.nameList[binIndex], self.startList[binIndex], self.endList[binIndex])
        return ret

    def getRegionBinRange(self, chrName, startPos, endPos):
        """
        Given a chromosome region, this function returns 
        the bin indices that overlap with such region.
        It uses the mappedBins list. See explanation 
        """
        try:
            chrValue = self.chrNamesValue[chrName]
        except:
            print "chromosome: {} name not found in matrix".format(chrName)
            print "valid names are:"
            print self.chrNames
            return None
        try:
            startPos = int(startPos)
            endPos = int(endPos)
        except:
            print "{} or {}  are not valid position values.".format(startPos, endPos)
            exit()
        # bisect_right returns the index of the list
        # that is less than  to startPos + chrValue
        startBin = bisect_right(self.mappedBins, startPos + chrValue)
        endBin   = bisect_left(self.mappedBins, endPos + chrValue) + 1

        return (startBin, endBin)

    def getCountsByDistance(self, chromosome=None,  mean=False, intraChromosomal=True):
        """
        computes counts for each intrachromosomal distance
        """
        try:
            return self.distanceCounts
        except:
            pass

        dist = {}
        distance = {}

        if intraChromosomal:
            for chrName in self.chrNames:
                if chromosome and chrName != chromosome:
                    continue
                if chrName in self.getUnwantedChrs():
                    continue
                index_start, index_end = self.getChrBinRange(chrName)
                dist[chrName] = self.getDistanceFromSubMatrix( self.matrix[index_start:index_end, index_start:index_end] )
                for i in range(len(dist[chrName].keys())):
                    distance.setdefault(i, np.array( [] ))
                    distance[i] = np.append( distance[i], dist[chrName][i] )

        else:
            distance = self.getDistanceFromSubMatrix(self.matrix)

        self.distanceCounts = distance
        if mean:
            return [ np.mean(distance[x]) for x in range(len(distance.keys())) ]
        else:
            return distance


    @staticmethod 
    def getDistanceFromSubMatrix(ma):
        """
        Given a matrix it returns a dictionary
        in which the key represents distance
        and the value is a numpy array
        containing all values at this distance.
        Distance is defined as i-j where 
        i is the row number and j the row number.

        Because the matrices used are always symetric
        only the upper triangle is used.

        Nans are removed.

        >>> ma = np.array( [[1, 2, 3], [1, 4, np.nan], [1, 8, 27]])
        >>> hiCMatrix.getDistanceFromSubMatrix(ma)
        {0: array([  1.,   4.,  27.]), 1: array([ 2.]), 2: array([ 3.])}
        """

        distance = {}
        size = ma.shape[0]
        for i in range(size):
            # values at distance i are all in the
            # the matrix diagonal offset by i
            d = np.diagonal(ma, i)
            # remove nans
            d = d[np.where(np.isnan(d) == False )] 
            # remove extrem values
            if len(d):
                d = d[d < np.percentile(d, 99)]
                if len(d):
                    distance[i] = d
#            distance.setdefault(i, []).extend(d.tolist)
        return distance

    @staticmethod
    def getUnwantedChrs():
        unwantedChr = set( ['chrM', 'chrYHet', 'chrXHet', 
                            'chrUextra', 'chrU', 'chr3RHet', 'chr3LHet',
                            'chr2RHet', 'chr2LHet'] )
        return unwantedChr

    def filterUnwantedChr(self, chromosome=None):
        size = self.matrix.shape
        # initialize a 1D array containing the columns (and rows) to 
        # select. By default none are selected
        sel = np.empty(size[0], dtype=np.bool)
        sel[:] = False

        for chrName in self.chrNames:
            if chromosome and chrName != chromosome:
                continue
            if chrName in self.getUnwantedChrs():
                continue

            index_start, index_end = self.getChrBinRange(chrName)
            sel[index_start:index_end] = True

        # for some reason rows has to be selected independently 
        # from columns, otherwise the matrix is broken
        mat = self.matrix[sel,:]
        mat = mat[:,sel]

        # update bin ids 
        self.nameList = self.nameList[sel]
        self.binIdList = self.binIdList[sel]
        self.startList = self.startList[sel]
        self.endList = self.endList[sel]
        self.numCols = len(self.nameList)

        self.mappedBins, \
        self.chrNamesValue, \
        self.chrBinBoundaries  = \
            self.mapPositionsToBins(self.endList, self.nameList)
        
        self.chrNames = self.chrNamesValue.keys()
        self.matrix = mat

        return self.matrix

    def save(self, fileName):
        """
        Saves the matrix
        """

        colNames = [ "{}|dm3|{}:{}-{}".format(self.binIdList[x], 
                                               self.nameList[x],
                                               self.startList[x],
                                               self.endList[x]) for x in range(self.matrix.shape[0]) ]
        
        try:
            fileh = gzip.open(fileName, 'w')
        except:
            msg = "{} file can be opened for writting".format(fileName)
            raise argparse.ArgumentTypeError(msg)

        
        fileh.write( "".join(self.header) )
        fileh.write( "\t" + "\t".join(colNames) + "\n" )
        for row in range(self.matrix.shape[0]):
            values = [ str(x) for x in self.matrix[row,:] ]
            fileh.write("{}\t{}\n".format(colNames[row], "\t".join(values) ) )

        fileh.close()
                                         
    def diagflat(self):
        self.matrix = self.matrix + np.diagflat( np.repeat(np.nan, self.matrix.shape[0]) ) # set diagonal to nan
        return self.matrix

    def filterOutInterChrCounts(self, chromosome=None):
        """
        set all inter chromosomal counts to np.nan
        """
        dist = np.array( [], dtype = 'int' )
        for row in range(self.matrix.shape[0]):
            for column in range(self.matrix.shape[0]):
                if self.nameList[row] != self.nameList[column]:
                    self.matrix[i,j] = np.nan

        return self.matrix

    def setMatrixValues(self, newMatrix):
        if self.matrix.shape == newMatrix.shape:
            self.matrix = newMatrix
        else:
            msg = "Given matrix has different shape. New values need to have the same shape as previous matrix. "
            raise argparse.ArgumentTypeError(msg)

