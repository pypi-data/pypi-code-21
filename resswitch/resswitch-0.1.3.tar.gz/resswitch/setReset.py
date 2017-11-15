# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""Contains the class that analizes all cycles.

Using resistiveAnalysisClass it extends the analysis
to all cycles.

"""

from resistiveAnalysisClass import rawDataReset
from resistiveAnalysisClass import rawDataSet
import matplotlib.pyplot as plt
import numpy


class setReset:

    """setReset class"""

    def __init__(self, data, ratioSet, ratioReset):
        """Initializes the object."""

        on = []
        off = []
        cycleNumber = len(data)
        flag = 1
        self.data = data
        self.comment = u''
        for i in range(cycleNumber):
            if flag == 1:
                on.append(rawDataSet(data[i], ratioSet))
                flag = 0
            else:
                off.append(rawDataReset(data[i], ratioReset))
                flag = 1
        self.onTension = []
        self.onCurrent = []
        self.onResistance = []
        self.offTension = []
        self.offCurrent = []
        self.offResistance = []
        flag = 1
        ion = 0
        ioff = 0
        for i in range(cycleNumber):
            if flag == 1:
                self.onTension.append(on[ion].set[0])
                self.onCurrent.append(on[ion].set[1])
                self.onResistance.append(on[ion].set[2])
                flag = 0
                ion = ion + 1
            else:
                self.offTension.append(off[ioff].reset[0])
                self.offCurrent.append(off[ioff].reset[1])
                self.offResistance.append(off[ioff].reset[2])
                flag = 1
                ioff = ioff + 1

    def tensionHistogram(self, minimum, maximum, width, save):
        """tension histogram"""

        onTens = [x for x in self.onTension if x != "no set"]
        offTens = [x for x in self.offTension if x != "no reset"]
        bins = numpy.linspace(minimum, maximum, width).tolist()
        histoga = numpy.histogram(onTens, bins)
        histogb = numpy.histogram(offTens, bins)
        cuma = numpy.cumsum(histoga[0].tolist())
        cumb = numpy.cumsum(histogb[0].tolist())
        cumax = []
        cumay = []
        previous = 0.
        for i in range(len(cuma)):
            if cuma[i] != previous:
                cumax.append(cuma[i])
                cumay.append(bins[1:][i])
                previous = cuma[i]
        cumbx = []
        cumby = []
        previous = 0.
        for i in range(len(cumb)):
            if cumb[i] != previous:
                cumbx.append(cumb[i])
                cumby.append(bins[1:][i])
                previous = cumb[i]

        return bins, cumay, cumby, onTens, offTens, cumax, cumbx

    def tensionCumulativeProbability(self):
        """tension cumulative probability"""

        cumon = [0]
        cumonX = [0]
        cumoff = [0]
        cumoffX = [0]
        onTens = [x for x in self.onTension if x != "no set"]
        offTens = [x for x in self.offTension if x != "no reset"]
        sumOn = len(onTens)
        sumOff = len(offTens)
        onTens.sort()
        offTens.sort()
        for i in onTens:
            if cumonX[-1] == i:
                cumon[-1] += 1
            else:
                cumonX.append(i)
                cumon.append(1 + cumon[-1])

        for i in offTens:
            if cumoffX[-1] == i:
                cumoff[-1] += 1
            else:
                cumoffX.append(i)
                cumoff.append(1 + cumoff[-1])
        cumon.pop(0)
        cumoff.pop(0)
        cumonX.pop(0)
        cumoffX.pop(0)
        cumon = map((lambda x: 100. * x / sumOn), cumon)
        cumoff = map((lambda x: 100. * x / sumOff), cumoff)

        return cumon, cumonX, cumoff, cumoffX

    def currentCumulativeProbability(self):
        """current cumulative probability"""

        cumon = [0]
        cumonX = [0]
        cumoff = [0]
        cumoffX = [0]
        onCur = [x for x in self.onCurrent if x != "no set"]
        offCur = [x for x in self.offCurrent if x != "no reset"]
        sumOn = len(onCur)
        sumOff = len(offCur)
        onCur.sort()
        offCur.sort()
        for i in onCur:
            if cumonX[-1] == i:
                cumon[-1] += 1
            else:
                cumonX.append(i)
                cumon.append(1 + cumon[-1])

        for i in offCur:
            if cumoffX[-1] == i:
                cumoff[-1] += 1
            else:
                cumoffX.append(i)
                cumoff.append(1 + cumoff[-1])
        cumon.pop(0)
        cumoff.pop(0)
        cumonX.pop(0)
        cumoffX.pop(0)
        cumon = map((lambda x: 100. * x / sumOn), cumon)
        cumoff = map((lambda x: 100. * x / sumOff), cumoff)

        return cumon, cumonX, cumoff, cumoffX

    def resistanceCumulativeProbability(self):
        """resistance cumulative probability"""

        onRes = [x for x in self.onResistance if x != "no set"]
        offRes = [x for x in self.offResistance if x != "no reset"]
        sumOn = len(onRes)
        sumOff = len(offRes)
        sortOn = sorted(onRes)
        sortOff = sorted(offRes)
        cumax = []
        cumay = []
        ncuma = 0
        for i in range(len(onRes)):
            ncuma = ncuma + 1
            cumax.append(sortOn[i])
            cumay.append(ncuma)
        cumbx = []
        cumby = []
        ncumb = 0
        for i in range(len(offRes)):
            ncumb = ncumb + 1
            cumbx.append(sortOff[i])
            cumby.append(ncumb)
        cumay = map((lambda x: 100. * x / sumOn), cumay)
        cumby = map((lambda x: 100. * x / sumOff), cumby)

        return cumax, cumay, cumbx, cumby

    def resistancePlot(self):
        """resistance plot"""

        onRes = []
        offRes = []
        for i in range(len(self.onResistance)):
            if self.onResistance[i] == 'no set':
                onRes.append(None)
            else:
                onRes.append(self.onResistance[i])
        for i in range(len(self.offResistance)):
            if self.offResistance[i] == 'no reset':
                offRes.append(None)
            else:
                offRes.append(self.offResistance[i])

        return onRes, offRes

    def tensionPlot(self):
        """tension plot"""

        onTen = []
        offTen = []
        for i in range(len(self.onTension)):
            if self.onTension[i] == 'no set':
                onTen.append(None)
            else:
                onTen.append(self.onTension[i])
        for i in range(len(self.offTension)):
            if self.offTension[i] == 'no reset':
                offTen.append(None)
            else:
                offTen.append(self.offTension[i])

        return onTen, offTen

    def tensionRoffPlot(self):
        """tension Roff plot"""

        Vset = []
        Vreset = []
        Roff = []
        for i in range(len(self.onTension)):
            cond1 = self.onTension[i] == 'no set'
            cond2 = self.offTension[i] == 'no reset'
            if cond1 or cond2:
                Vset.append(None)
                Vreset.append(None)
                Roff.append(None)
            else:
                Vset.append(self.onTension[i])
                Vreset.append(self.offTension[i])
                Roff.append(self.offResistance[i])

        return Roff, Vset, Vreset

    def tensionRonPlot(self):
        """tension Ron plot"""

        Vset = []
        Vreset = []
        Ron = []
        for i in range(len(self.onTension)):
            cond1 = self.onTension[i] == 'no set'
            cond2 = self.offTension[i] == 'no reset'
            if cond1 or cond2:
                Vset.append(None)
                Vreset.append(None)
                Ron.append(None)
            else:
                Vset.append(self.onTension[i])
                Vreset.append(self.offTension[i])
                Ron.append(self.onResistance[i])

        return Ron, Vset, Vreset

    def resistanceIonPlot(self):
        """resistance Ion plot"""

        Ron = []
        Roff = []
        ion = []
        for i in range(len(self.onTension)):
            cond1 = self.onTension[i] == 'no set'
            cond2 = self.offTension[i] == 'no reset'
            if cond1 or cond2:
                Ron.append(None)
                Roff.append(None)
                ion.append(None)
            else:
                Ron.append(self.onResistance[i])
                Roff.append(self.offResistance[i])
                ion.append(self.onCurrent[i])

        return ion, Ron, Roff

    def resistanceIoffPlot(self):
        """resistance Ioff plot"""

        Ron = []
        Roff = []
        ioff = []
        for i in range(len(self.onTension)):
            cond1 = self.onTension[i] == 'no set'
            cond2 = self.offTension[i] == 'no reset'
            if cond1 or cond2:
                Ron.append(None)
                Roff.append(None)
                ioff.append(None)
            else:
                Ron.append(self.onResistance[i])
                Roff.append(self.offResistance[i])
                ioff.append(self.offCurrent[i])

        return ioff, Ron, Roff

    def tensionIonPlot(self):
        """tension Ion plot"""

        Vset = []
        Vreset = []
        ion = []
        for i in range(len(self.onTension)):
            cond1 = self.onTension[i] == 'no set'
            cond2 = self.offTension[i] == 'no reset'
            if cond1 or cond2:
                Vset.append(None)
                Vreset.append(None)
                ion.append(None)
            else:
                Vset.append(self.onTension[i])
                Vreset.append(self.offTension[i])
                ion.append(self.onCurrent[i])

        return ion, Vset, Vreset

    def tensionIoffPlot(self):
        """tension Ioff plot"""

        Vset = []
        Vreset = []
        ioff = []
        for i in range(len(self.onTension)):
            cond1 = self.onTension[i] == 'no set'
            cond2 = self.offTension[i] == 'no reset'
            if cond1 or cond2:
                Vset.append(None)
                Vreset.append(None)
                ioff.append(None)
            else:
                Vset.append(self.onTension[i])
                Vreset.append(self.offTension[i])
                ioff.append(self.offCurrent[i])

        return ioff, Vset, Vreset

    def currentPlot(self):
        """current plot"""

        onCur = []
        offCur = []
        for i in range(len(self.onCurrent)):
            if self.onCurrent[i] == 'no set':
                onCur.append(None)
            else:
                onCur.append(self.onCurrent[i])
        for i in range(len(self.offCurrent)):
            if self.offCurrent[i] == 'no reset':
                offCur.append(None)
            else:
                offCur.append(self.offCurrent[i])

        return onCur, offCur

    def countNoSet(self):
        """count no set"""

        count = 0
        for i in range(len(self.onTension)):
            if self.onTension[i] == "no set":
                count = count + 1

        return count

    def countNoReset(self):
        """count no reset"""

        count = 0
        for i in range(len(self.offTension)):
            if self.offTension[i] == "no reset":
                count = count + 1

        return count

    def ResCum(self, minimum, maximum, width, save):
        """rescum"""

        onRes = [x for x in self.onResistance if x != "no set"]
        offRes = [x for x in self.offResistance if x != "no reset"]
        bins = 10 ** numpy.linspace(numpy.log10(minimum),
                                    numpy.log10(maximum), width)
        plt.xlabel('tension (V)')
        sortOn = sorted(onRes)
        sortOff = sorted(offRes)
        cumax = []
        cumay = []
        ncuma = 0
        for i in range(len(onRes)):
            ncuma = ncuma + 1
            cumax.append(sortOn[i])
            cumay.append(ncuma)
        cumbx = []
        cumby = []
        ncumb = 0
        for i in range(len(offRes)):
            ncumb = ncumb + 1
            cumbx.append(sortOff[i])
            cumby.append(ncumb)

        return bins, onRes, offRes, cumax, cumay, cumbx, cumby

    def currentHistogram(self, minimum, maximum, width, save):
        """current histogram"""

        onCur = [x for x in self.onCurrent if x != "no set"]
        offCur = [x for x in self.offCurrent if x != "no reset"]
        bins = 10 ** numpy.linspace(numpy.log10(minimum),
                                    numpy.log10(maximum), width)
        sortOn = sorted(onCur)
        sortOff = sorted(offCur)
        cumax = []
        cumay = []
        ncuma = 0
        for i in range(len(onCur)):
            ncuma = ncuma + 1
            cumax.append(sortOn[i])
            cumay.append(ncuma)
        cumbx = []
        cumby = []
        ncumb = 0
        for i in range(len(offCur)):
            ncumb = ncumb + 1
            cumbx.append(sortOff[i])
            cumby.append(ncumb)

        return bins, onCur, offCur, cumax, cumay, cumbx, cumby

    def results(self):
        """results"""

        avOnTension = numpy.mean([x for x in self.onTension if x != u'no set'])
        avOffTension = numpy.mean(
            [x for x in self.offTension if x != u'no reset'])
        avOnResistance = numpy.mean(
            [x for x in self.onResistance if x != u'no set'])
        avOffResistance = numpy.mean(
            [x for x in self.offResistance if x != u'no reset'])
        RoffRonRatio = avOffResistance / avOnResistance
        VsetVresetRatio = avOnTension / avOffTension
        Vset = []
        Vreset = []
        Ron = []
        Roff = []
        ion = []
        ioff = []
        for i in range(len(self.onTension)):
            cond1 = self.onTension[i] != u'no set'
            if cond1 and self.offTension[i] != u'no reset':
                Vset.append(self.onTension[i])
                Vreset.append(self.offTension[i])
                Ron.append(self.onResistance[i])
                Roff.append(self.offResistance[i])
                ion.append(self.onCurrent[i])
                ioff.append(self.offCurrent[i])
        corrVsetRon = numpy.corrcoef(Vset, Ron)[0][1]
        corrVresetRon = numpy.corrcoef(Vreset, Ron)[0][1]
        corrVsetRoff = numpy.corrcoef(Vset, Roff)[0][1]
        corrVresetRoff = numpy.corrcoef(Vreset, Roff)[0][1]
        corrVsetIon = numpy.corrcoef(Vset, ion)[0][1]
        corrVresetIon = numpy.corrcoef(Vreset, ion)[0][1]
        corrVsetIoff = numpy.corrcoef(Vset, ioff)[0][1]
        corrVresetIoff = numpy.corrcoef(Vreset, ioff)[0][1]
        corrRonIon = numpy.corrcoef(Ron, ion)[0][1]
        corrRoffIon = numpy.corrcoef(Roff, ion)[0][1]
        corrRonIoff = numpy.corrcoef(Ron, ioff)[0][1]
        corrRoffIoff = numpy.corrcoef(Roff, ioff)[0][1]

        result = ''
        result += "\nResistance and tension distributions\n\nAverage On "
        result += "Tension    \t %f" % avOnTension
        result += "\nAverage Off Tension    \t %f" % avOffTension
        result += "\n\nAverage On Resistance\t %f" % avOnResistance
        result += "\nAverage Off Resistance\t %f" % avOffResistance
        result += "\n\nRoff/Ron                     \t %f" % RoffRonRatio
        result += "\nVon/Voff                     \t %f" % VsetVresetRatio
        result += "\n\n\nCorrelation coefficients\n\nCorrelation coefficient "
        result += "Vset/Ron   \t %f" % corrVsetRon
        result += "\nCorrelation coefficient Vreset/Ron\t %f" % corrVresetRon
        result += "\nCorrelation coefficient Vset/Roff   \t %f" % corrVsetRoff
        result += "\nCorrelation coefficient Vreset/Roff\t %f" % corrVresetRoff
        result += "\nCorrelation coefficient Vset/ion   \t %f" % corrVsetIon
        result += "\nCorrelation coefficient Vreset/ion\t %f" % corrVresetIon
        result += "\nCorrelation coefficient Vset/ioff   \t %f" % corrVsetIoff
        result += "\nCorrelation coefficient Vreset/ioff\t %f" % corrVresetIoff
        result += "\nCorrelation coefficient Ron/ion   \t %f" % corrRonIon
        result += "\nCorrelation coefficient Roff/ion   \t %f" % corrRoffIon
        result += "\nCorrelation coefficient Ron/ioff   \t %f" % corrRonIoff
        result += "\nCorrelation coefficient Roff/ioff   \t %f" % corrRoffIoff

        return result

    def cyclePlot(self, columnX, columnY, scal, type, cycl):
        """cycle plot"""

        return self.data[cycl][columnX], self.data[cycl][columnY]

    def note(self, notes):
        """notes"""

        self.comment = notes
