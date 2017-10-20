from sequana.lazy import pylab
from sequana.lazy import pandas as pd


__all__ = ["BUSCO"]


class BUSCO(object):
    """Wrapper of the BUSCO output

    "BUSCO provides a quantitative measures for the assessment
    of a genome assembly, gene set, transcriptome completeness, based on
    evolutionarily-informed expectations of gene content from near-universal
    single-copy orthologs selected from OrthoDB v9." -- BUSCO website 2017

    This class reads the full report generated by BUSCO and provides some
    visualisation of this report. The information is stored in a dataframe
    :attr:`df`. The score can be retrieve with the attribute :attr:`score` in
    percentage in the range 0-100.

    :reference: http://busco.ezlab.org/
    """
    def __init__(self, filename="full_table_testbusco.tsv"):
        """.. rubric:: constructor

        :filename: a valid BUSCO input file (full table). See example in sequana
            code source (testing)

        """
        self.df = pd.read_csv(filename, sep="\t", skiprows=4)

    def pie_plot(self, filename=None, hold=False):
        """Plot PIE plot of the status (complete / fragment / missed)

        .. plot::
            :include-source:

            from sequana import BUSCO, sequana_data
            b = BUSCO(sequana_data("test_busco_full_table.tsv"))
            b.pie_plot()

        """
        if hold is False:
            pylab.clf()
        self.df.groupby('Status').count()['# Busco id'].plot(kind="pie")
        pylab.ylabel("")
        #pylab.title("Distribution Complete/Fragmented/Missing")
        #pylab.legend()
        if filename:
            pylab.savefig(filename)

    def scatter_plot(self, filename=None, hold=False):
        """Scatter plot of the score versus length of each ortholog

        .. plot::
            :include-source:

            from sequana import BUSCO, sequana_data
            b = BUSCO(sequana_data("test_busco_full_table.tsv"))
            b.scatter_plot()
        """
        if hold is False:
            pylab.clf()
        colors = ["green", "orange", "red", "blue"]
        markers = ['o', 's', 'x', 'o']
        for i, this in enumerate(["Complete", "Fragmented", "Missing",  "Duplicated"]):
            mask = self.df.Status == "Complete"
            if sum(mask)>0:
                self.df[mask].plot(x="Length", y="Score", kind="scatter", 
                    color=colors[i],
                    marker=markers[i], label="Complete")

        pylab.legend()
        pylab.grid()
        if filename:
            pylab.savefig(filename)

    def summary(self):
        """Return summary information of the missing, completed, fragemented
        orthologs

        """
        df = self.df.drop_duplicates(subset=["# Busco id"])
        data = {}
        data['S'] = sum(df.Status == "Complete")
        data['F'] = sum(df.Status == "Fragmented")
        data['D'] = sum(df.Status == "Duplicated")
        data['C'] = data['S'] + data['D']
        data['M'] = sum(df.Status == "Missing")
        data['total'] = len(df)
        data['C_pc'] = data['C'] *100. / data['total']
        data['D_pc'] = data['D'] *100. / data['total']
        data['S_pc'] = data['S'] *100. / data['total']
        data['M_pc'] = data['M'] *100. / data['total']
        data['F_pc'] = data['F'] *100. / data['total']
        return data

    def get_summary_string(self):
        data = self.summary()
        C = data['C_pc']
        F = data["F_pc"]
        D = data["D_pc"]
        S = data["S_pc"]
        M = data["M_pc"]
        N = data["total"]
        string = "C:{:.1f}%[S:{:.1f}%,D:{:.1f}%],F:{:.1f}%,M:{:.1f}%,n:{}"
        return string.format(C, S, D, F, M, N)

    def _get_score(self):
        return self.summary()["C_pc"]
    score = property(_get_score)

    def __str__(self):
        data = self.summary()
        C = data['C']
        F = data["F"]
        D = data["D"]
        S = data["S"]
        M = data["M"]
        N = data["total"]
        string = """# BUSCO diagnostic

{}

    {} Complete BUSCOs (C)
    {}   Complete and single-copy BUSCOs (S)
    {}   Complete and duplicated  BUSCOs (D)
    {}   Fragmented BUSCOs (F)
    {}   Missing BUSCOs (M)
    {} Total BUSCO groups searched
    """
        return string.format(self.get_summary_string(), C, S, D, F, M, N)
