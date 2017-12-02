import os

from plotly.offline import iplot, plot
import plotly.graph_objs as go
import plotly.figure_factory as ff
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import hashlib
from ipywidgets import interact
import random
import scipy.signal as signal
from sklearn.mixture import GaussianMixture
import colorlover as cl
from sklearn.ensemble import RandomForestRegressor

def get_spaced_colors(n):
    max_value = 255
    interval = int(max_value / n)
    hues = range(0, max_value, interval)
    return cl.to_rgb(["hsl(%d,100%%,40%%)"%i for i in hues])

class MatrixPlotter:
    def __init__(self, DS, mode="notebook"):
        self.DS = DS
        self.plot_mode = mode

    def makeplot(self, fig):
        """Make the plotly figure visable to the user in the way they want.

        Parameters
        ----------
        gid : :obj:`figure`
            An plotly figure.

        """
        
        if self.plot_mode == "notebook":
            iplot(fig)
        if self.plot_mode == "html":
            fig["layout"]["autosize"] = True
            h = random.getrandbits(128)
            fname = "%032x.html"%h
            plot(fig, output_type='file', filename=fname)
        if self.plot_mode == "div":
            fig["layout"]["autosize"] = True
            return plot(fig, output_type='div', include_plotlyjs=False)

class Heatmap(MatrixPlotter):
    titlestring = "%s Heatmap"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        xaxis = go.XAxis(
                title="observaions",
                ticktext = self.DS.D.index,
                showticklabels=False,
                tickvals = [i for i in range(len(self.DS.D.index))])
        yaxis = go.YAxis(
                title="dimensions",
                ticktext = self.DS.D.columns,
                showticklabels=False,
                tickvals = [i for i in range(len(self.DS.D.columns))])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = self.DS.D.as_matrix().T)
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig)

class LocationHeatmap(MatrixPlotter):
    titlestring = "%s Location Heatmap"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        means = np.mean(D, axis=1)
        medians = np.median(D, axis=1)
        z = np.vstack([means, medians])
        yaxis = go.YAxis(
                ticktext = ["mean", "median"],
                showticklabels=True,
                tickvals = [0, 1])
        xaxis = go.XAxis(
                title="dimensions",
                ticktext = self.DS.D.columns,
                showticklabels=False,
                tickvals = [i for i in range(len(self.DS.D.columns))])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = z)
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig)

class LocationLines(MatrixPlotter):
    titlestring = "%s Embedding Location Lines"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        means = np.mean(D, axis=1)
        medians = np.median(D, axis=1)
        trace0 = go.Scatter(x = np.arange(len(means)), y = means, name="means")
        trace1 = go.Scatter(x = np.arange(len(medians)), y = medians, name="medians")
        layout = dict(title=title,
                      xaxis=dict(title="Dimensions",
                                 ticktext = self.DS.D.columns,
                                 showticklabels=False,
                                 tickvals = [i for i in range(len(self.DS.D.columns))]),
                      yaxis=dict(title="Mean or Median Value"))
        data = [trace0, trace1]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig)

class HistogramHeatmap(MatrixPlotter):
    titlestring = "%s Histogram Heatmap"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        d, n = D.shape
        D = (D - np.mean(D, axis=1).reshape(d, 1)) / np.std(D, axis=1).reshape(d, 1)
        D = np.nan_to_num(D) # only nan if std all 0 -> all values 0
        num_bins = int(np.sqrt(n))
        bins = np.linspace(-5, 5, num_bins + 1)
        bin_centers = (bins[1:] + bins[:-1]) / 2
        H = []
        for i in range(D.shape[0]):
            hist = np.histogram(D[i, :], bins = bins)[0]
            H.append(hist)
        z = np.vstack(H)
        trace = go.Heatmap(z = z)
        data = [trace]
        xaxis = go.XAxis(
                title="Normalized Value",
                ticktext = list(map(lambda x: "%0.4f"%x, bin_centers)),
                ticks = "",
                showticklabels=True,
                mirror=True,
                tickvals = [i for i in range(len(bin_centers))])
        yaxis = go.YAxis(
                title="Dimensions",
                ticks = "",
                showticklabels=False,
                mirror=True)
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        fig = dict(data = data, layout = layout)
        return self.makeplot(fig)

class CorrelationMatrix(MatrixPlotter):
    titlestring = "%s Correlation Matrix"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        xaxis = dict(
            title = "Dimensions",
            ticks = "",
            ticktext = self.DS.D.columns,
            showgrid=False,
            showticklabels=False,
            tickvals = [i for i in range(len(self.DS.D.columns))]
        )
        yaxis = dict(
            scaleanchor="x",
            title = "Dimensions",
            ticks = "",
            ticktext = self.DS.D.columns,
            showgrid=False,
            showticklabels=False,
            tickvals = [i for i in range(len(self.DS.D.columns))]
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            C = np.nan_to_num(np.corrcoef(D))

        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = C)
        fig = dict(data=[trace], layout=layout)
        return self.makeplot(fig)

class ScreePlotter(MatrixPlotter): 
    titlestring = "%s Scree Plot"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        _, S, _ = np.linalg.svd(D, full_matrices=False)
        y = S
        x = np.arange(1, len(S) + 1)
        sy = np.sum(y)
        cy = np.cumsum(y)
        xaxis = dict(
            title = 'Factors'
        )
        yaxis = dict(
            title = 'Proportion of Total Variance'
        )
        var = go.Scatter(mode = 'lines+markers',
                         x = x,
                         y = y / sy,
                         name = "Variance")
        cumvar = go.Scatter(mode = 'lines+markers',
                            x = x,
                            y = cy / sy,
                            name = "Cumulative Variance")
        data = [var, cumvar]
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig)

class EigenvectorHeatmap(MatrixPlotter):
    titlestring = "%s Eigenvector Heatmap"

    def plot(self):
        title = self.titlestring % (self.DS.name)
        D = self.DS.D.as_matrix().T
        d, n = D.shape
        print(D.shape)
        U, _, _ = np.linalg.svd(D, full_matrices=False)
        print(U.shape)
        xaxis = go.XAxis(
                title="Eigenvectors",
                ticktext = ["Eigenvector %s"%i for i in range(1, d + 1)],
                ticks = "",
                showgrid=False,
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(d)])
        yaxis = go.YAxis(
                title="Eigenvector Components",
                scaleanchor="x",
                showgrid=False,
                ticktext = ["Component %s"%i for i in range(1, d + 1)],
                ticks = "",
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(d)])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = U)
        data = [trace]
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig)

class HGMMPlotter(MatrixPlotter):
    def __init__(self, *args, **kwargs):
        super(HGMMPlotter, self).__init__(*args, **kwargs)
        X = self.DS.D.as_matrix()
        levels = []
        n = X.shape[0]
        l0 = HGMMPlotter.hgmml0(X)
        levels.append(l0)
        li = HGMMPlotter.gmmBranch(l0[0])
        levels.append(li)
        while (len(li) < n) and (len(levels) < 5):
            print("Starting level", len(levels))
            lip = []
            for c in li:
                q = HGMMPlotter.gmmBranch(c)
                if q is not None:
                    lip.extend(q)
            levels.append(lip)
            li = lip
        self.levels = levels

    def gmmBranch(level):
        X, p, mu = level
        if X.shape[0] >= 2:
            gmm = GaussianMixture(n_components=2)
            gmm.fit(X)
            X0 = X[gmm.predict(X) == 0, :]
            X1 = X[gmm.predict(X) == 1, :]
            mypro = np.rint(gmm.weights_ * p)
            return [(X0, int(mypro[0]), gmm.means_[0, :],),
                    (X1, int(mypro[1]), gmm.means_[1, :],)]
        elif X.shape[0] == 1:
            gmm = GaussianMixture(n_components=1)
            gmm.fit(X)
            return [(X, int(np.rint(p * gmm.weights_[0])), gmm.means_[0, :],)] 

    def hgmml0(X):
        gmm = GaussianMixture(n_components=1)
        gmm.fit(X)
        return [(X, int(np.rint(X.shape[0] * gmm.weights_[0])), gmm.means_[0, :],)]

class HGMMClusterMeansDendrogram(HGMMPlotter):
    titlestring = "%s HGMM Cluster Means Dendrogram to Lev. %d"

    def plot(self, level=4):
        title = self.titlestring % (self.DS.name, level)
        means = []
        for c in self.levels[level]:
            means.append(c[2])
        X = np.column_stack(means).T
        fig = ff.create_dendrogram(X)
        fig["layout"]["title"] = title
        fig["layout"]["xaxis"]["title"] = "Cluster Labels"
        fig["layout"]["yaxis"]["title"] = "Cluster Mean Distances"
        del fig.layout["width"]
        del fig.layout["height"]
        return self.makeplot(fig)

class HGMMStackedClusterMeansHeatmap(HGMMPlotter):
    titlestring = "%s HGMM Stacked Cluster Means up to Level %d"

    def plot(self, level=4):
        title = self.titlestring % (self.DS.name, level)
        Xs = []
        for l in self.levels[1:level]:
            means = []
            for c in l:
                for _ in range(c[1]):
                    means.append(c[2])
            X = np.column_stack(means)
            Xs.append(X)
        X = np.vstack(Xs)[::-1, :]
        trace = go.Heatmap(z = X)
        data = [trace]
        xaxis = go.XAxis(
                title="Clusters",
                showticklabels=False,
                ticks="",
                mirror=True,
                tickvals = [i for i in range(X.shape[1])])
        yaxis = go.YAxis(
                title="Dimensions",
                showticklabels=False,
                ticks="",
                mirror=True,
                tickvals = [i for i in range(X.shape[0])])
        emb_size = len(self.levels[0][0][2])
        bar_locations = np.arange(0, X.shape[0]  + emb_size - 1, emb_size) - 0.5
        shapes = [dict(type="line",x0=-0.5, x1=X.shape[1] - 0.5, y0=b, y1=b) for b in bar_locations]
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis, shapes=shapes)
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig)

class HGMMClusterMeansLevelHeatmap(HGMMPlotter):
    titlestring = "%s HGMM Cluster Means, Level %d"

    def plot(self, level=4):
        title = self.titlestring % (self.DS.name, level)
        means = []
        for c in self.levels[level]:
            for _ in range(c[1]):
                means.append(c[2])
        X = np.column_stack(means)
        trace = go.Heatmap(z = X)
        data = [trace]
        xaxis = go.XAxis(
                title="clusters",
                showticklabels=False,
                ticks="",
                mirror=True,
                tickvals = [i for i in range(X.shape[1])])
        yaxis = go.YAxis(
                title="embedding dimensions",
                showticklabels=False,
                ticks="",
                mirror=True,
                tickvals = [i for i in range(X.shape[0])])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig)

class HGMMClusterMeansLevelLines(HGMMPlotter):
    titlestring = "%s HGMM Cluster Means Level %d"

    def plot(self, level=4):
        title = self.titlestring % (self.DS.name, level)
        data = []
        colors = get_spaced_colors(len(self.levels[level]))
        for i, c in enumerate(self.levels[level]):
            data.append(go.Scatter(x = c[2],
                                   y = list(range(len(c[2]))),
                                   mode="lines",
                                   line=dict(width=np.sqrt(c[1]), color=colors[i]),
                                   name="cluster " + str(i)))
        xaxis = go.XAxis(
                title="mean values",
                showticklabels=False,
                mirror=True)
        yaxis = go.YAxis(
                title="embedding dimensions",
                showticklabels=False,
                mirror=True)
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        fig = dict(data=data, layout=layout)
        return self.makeplot(fig)

class HGMMPairsPlot(HGMMPlotter):
    titlestring = "%s HGMM Classification Pairs Plot Level %d"

    def plot(self, level=2):
        title = self.titlestring % (self.DS.name, level)
        data = []
        colors = get_spaced_colors(len(self.levels[level]))
        samples = []
        labels = []
        for i, c in enumerate(self.levels[level]):
            samples.append(c[0].T)
            labels.append(c[0].shape[0] * [i])
        samples = np.hstack(samples)[:3, :]
        labels = np.hstack(labels)
        df = pd.DataFrame(samples.T, columns=["Dim %d"%i for i in range(samples.shape[0])])
        df["label"] = ["Cluster %d"%i for i in labels]
        fig = ff.create_scatterplotmatrix(df, diag='box', index="label", colormap=colors)
        fig["layout"]["title"] = title
        del fig.layout["width"]
        del fig.layout["height"]
        return self.makeplot(fig)

class DistanceMatrixPlotter:
    """A generic aggregate plotter acting on a distance matrix to be extended.

    Parameters
    ----------
    dm : :obj:`DistanceMatrix`
        The distance matrix object.
    primary_label : string
        The name of the column of the dataset which contains the primary label. By default, this is the `resource_path` column which is just the path to the data point resource.
    Attributes
    ----------
    dataset_name : string
        The name of the dataset from which this distance matrix was computed.
    dm : :obj:`ndarray`
        The distance matrix.
    label_name : string
        The name of the primary label to be conditioned on in some plots.
    label : :obj:`list`
        A list of labels (the primary label) for each data point.
    metric_name : string
        The name of the metric which with the distance matrix was computed.

    """

    def __init__(self, dm, mode = "notebook", primary_label = "resource_path"):
        self.dataset_name = dm.dataset.name
        self.dm = dm.getMatrix()
        self.labels = dm.labels
        self.label_name = dm.label_name
        self.metric_name = dm.metric.__name__
        self.plot_mode = mode

    def makeplot(self, fig):
        """Make the plotly figure visable to the user in the way they want.

        Parameters
        ----------
        gid : :obj:`figure`
            An plotly figure.

        """
        
        if self.plot_mode == "notebook":
            iplot(fig)
        if self.plot_mode == "html":
            fig["layout"]["autosize"] = True
            h = random.getrandbits(128)
            fname = "%032x.html"%h
            plot(fig, output_type='file', filename=fname)

class CSVPlotter:
    def __init__(self, ds, mode = "notebook"):
        self.ds = ds
        self.plot_mode = mode

    def makeplot(self, fig):
        """Make the plotly figure visable to the user in the way they want.

        Parameters
        ----------
        gid : :obj:`figure`
            An plotly figure.

        """
        
        if self.plot_mode == "notebook":
            iplot(fig)
        if self.plot_mode == "html":
            fig["layout"]["autosize"] = True
            h = random.getrandbits(128)
            fname = "%032x.html"%h
            plot(fig, output_type='file', filename=fname)
        if self.plot_mode == "div":
            fig["layout"]["autosize"] = True
            return plot(fig, output_type='div', include_plotlyjs=False)


class ColumnDistributionPlotter(CSVPlotter):
    def plot(self, column):
        x, y = self.ds.getColumnDistribution(column)
        yn = y / np.nansum(y)
        # title = "Column Distribution Plot<br>" + self.ds.getColumnDescription(column, sep="<br>")
        title = "Column Distribution Plot<br>"
        trace_frequency = go.Bar(
            x = x,
            y = y,
            name = 'Frequency'
        )
        trace_proportion = go.Bar(
            x = x,
            y = yn,
            visible = False,
            name = 'Proportion'
        )
        layout = go.Layout(
            title = title,
            xaxis = dict(title="Value"),
            yaxis = dict(title="Frequency")
        )
        updatemenus = list([
            dict(buttons = list([
                dict(args = [{'visible': [True, False]}, {'yaxis': dict(title="Frequency")}],
                     label = 'Frequency',
                     method = 'update'
                ),
                dict(args = [{'visible': [False, True]}, {'yaxis': dict(title="Proportion")}],
                     label = 'Proportion',
                     method = 'update'
                ),
                ]),
                showactive = True,
                type = 'buttons'
            )
        ])
        layout.updatemenus = updatemenus
        fig = go.Figure(data = [trace_frequency, trace_proportion], layout=layout)
        return self.makeplot(fig)

class ColumnNADistPlotter(CSVPlotter):
    def plot(self, column):
        na, not_na = self.ds.getColumnNADist(column)
        title = "Column NA Distribution Plot<br>" + self.ds.getColumnDescription(column, sep="<br>")
        trace = go.Pie(
            labels = ['NA', 'Not NA'],
            values = [na, not_na]
        )
        layout = go.Layout(
            title=title
        )
        fig = go.Figure(data = [trace], layout=layout)
        return self.makeplot(fig)

class EverythingPlotter(CSVPlotter):
    html_data = """
	<html>
	    <head>
		<title>
		%s
		</title>
		<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
	    </head>
	    <body>
              %s
            </body>
         </html>
	"""
    def plot(self, base, plotter):
        cp = plotter(self.ds, mode="div")
        for c in self.ds.D.columns:
            path = os.path.join(base, *c)
            os.makedirs(path, exist_ok=True)
            div = cp.plot(c)
            with open(os.path.join(path, plotter.__name__ + ".html"), "w") as f:
                f.write(self.html_data%(plotter.__name__, div))




class DistanceMatrixHeatmap(DistanceMatrixPlotter):
    titlestring = "%s %s Distance Matrix Heatmap"

    def plot(self):
        """Constructs a distance matrix heatmap using the :obj:`DistanceMatrix` object, in plotly.

        """
        title = self.titlestring % (self.dataset_name, self.metric_name)
        xaxis = go.XAxis(
                title="Observations",
                ticktext = self.labels,
                ticks = "",
                showticklabels=False,
                showgrid=False,
                mirror=True,
                tickvals = [i for i in range(len(self.labels))])
        yaxis = go.YAxis(
                scaleanchor="x",
                title="Observations",
                ticktext = self.labels,
                showgrid=False,
                ticks = "",
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(len(self.labels))])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = self.dm)
        data = [trace]
        fig = dict(data=data, layout=layout)
        self.makeplot(fig)


    
class Embedding2DScatter(DistanceMatrixPlotter):
    titlestring = "%s 2D %s Embedding Scatter under %s metric"

    def plot(self, embedder):
        """Constructs a 2d scatter plot of the embedded :obj:`DistanceMatrix` object, colorized by primary label.

        Parameters
        ----------
        embedder : :obj:`BaseEmbedder`
            An embedder object which should be used to embed the data into 2d space.

        """
        title = self.titlestring % (self.dataset_name, embedder.embedding_name, self.metric_name)
        emb = embedder.embed(self.dm)
        d = {
            'factor 1': emb[:, 0],
            'factor 2': emb[:, 1],
            self.label_name: self.labels
        }
        D = pd.DataFrame(d)
        sns.lmplot('factor 1',
                   'factor 2',
                    data = D,
                    fit_reg = False,
                    hue=self.label_name)
        plt.title(title)
        plt.show()


class EmbeddingPairsPlotter(DistanceMatrixPlotter):
    titlestring = "%s %s Embedding Pairs Plot under %s metric"

    def plot(self, embedder):
        """Constructs a pairs plot of the embedded :obj:`DistanceMatrix` object dimensions.

        Parameters
        ----------
        embedder : :obj:`BaseEmbedder`
            An embedder object which should be used to embed the data.

        """
        title = self.titlestring % (self.dataset_name, embedder.embedding_name, self.metric_name)
        emb = embedder.embed(self.dm)
        Pdf = pd.DataFrame(emb, columns = ["factor %s"%x for x in range(1, emb.shape[1] + 1)])
        Pdf[self.label_name] = self.labels
        sns.pairplot(data=Pdf, hue=self.label_name, diag_kind="hist")
        plt.subplots_adjust(top=0.9)
        plt.suptitle(title)
        plt.show()

class EmbeddingParallelCoordinatePlotter(DistanceMatrixPlotter):
    titlestring = "%s %s Embedding Parallel Coordinate Plot under %s metric"

    def plot(self, embedder):
        """Constructs a parallel coordinate plot of the embedded :obj:`DistanceMatrix` object.

        Parameters
        ----------
        embedder : :obj:`BaseEmbedder`
            

        """
        title = self.titlestring % (self.dataset_name, embedder.embedding_name, self.metric_name)
        emb = embedder.embed(self.dm)
        D = emb.T
        d, n = D.shape
        D = D - np.min(D, axis=1).reshape(d, 1)
        D = D / np.max(D, axis=1).reshape(d, 1)
        unique_labels = np.unique(self.labels)
        label_to_number = dict(zip(unique_labels, range(1, len(unique_labels) + 1)))
        dims = [dict(label = "factor %s"%(x + 1),
                values = D[x, :]) for x in range(embedder.num_components)]
        line = dict(color = [label_to_number[x] for x in self.labels],
                    cmin = 0,
                    cmax = len(unique_labels),
                    colorscale = "Jet",
                    showscale=True,
                    colorbar = dict(tickmode = "array",
                                    ticktext = unique_labels,
                                    tickvals = [label_to_number[x] for x in unique_labels]))
        trace = go.Parcoords(line = line, dimensions = list(dims))
        data = [trace]
        layout = go.Layout(
            title=title
        )
        fig = dict(data = data, layout = layout)
        self.makeplot(fig)



class DendrogramPlotter(DistanceMatrixPlotter):
    titlestring = "%s Dendrogram under %s metric"

    def plot(self):
        """Constructs a dendrogram using the :obj:`DistanceMatrix` object, in plotly.

        """
        title = self.titlestring % (self.dataset_name, self.metric_name)
        observations = np.zeros([2, 2])
        unique_labels = np.unique(self.labels)
        label_to_number = dict(zip(unique_labels, range(1, len(unique_labels) + 1)))
        number_labels = [label_to_number[l] for l in self.labels]
        def distance_function(x):
            flattened = self.dm[np.triu_indices(self.dm.shape[0], k=1)].flatten()
            return [f for f in flattened] 
        dendro = ff.create_dendrogram(X = observations,
                                      distfun = distance_function,
                                      labels=number_labels)
        dendro.layout.update(dict(title=title))
        dendro.layout.xaxis.update(dict(ticktext=self.labels,
                                        title=self.label_name,
                                        ticklen=1))
        dendro.layout.xaxis.tickfont.update(dict(size=12))
        dendro.layout.yaxis.update(dict(title=self.metric_name))
        dendro.layout.margin.update(dict(b = 200))
        del dendro.layout["width"]
        del dendro.layout["height"]
        self.makeplot(dendro)

class TimeSeriesPlotter:
    """A generic one-to-one plotter for time series data to be extended.

    Parameters
    ----------
    data : :obj:`ndarray`
        The time series data.
    resource_name : string
        The name of the time series being plotted.
    row_name : string
        The name of the rows in the time-series (e.g. channels, sources. ect.).
    column_name : string
        The name of the columns in the time-series (e.g. time points, time steps, seconds, ect.).

    Attributes
    ----------
    data : :obj:`ndarray`
        The time series data.
    d : int
        The number of dimensions in the time series
    n : int
        The number of time points in the time series
    row_name : string
        The name of the rows in the time-series (e.g. channels, sources. ect.).
    column_name : string
        The name of the columns in the time-series (e.g. time points, time steps, seconds, ect.).
    resource_name : string
        The name of the time series being plotted.

    """

    def __init__(self, data, mode = "notebook", resource_name = "single resource", 
                 row_name = "sources", col_name = "time points"):
        self.data = data
        self.d, self.n = data.shape
        self.row_name = row_name
        self.col_name = col_name
        self.resource_name = resource_name
        self.plot_mode = mode

    def makeplot(self, fig):
        """Make the plotly figure visable to the user in the way they want.

        Parameters
        ----------
        gid : :obj:`figure`
            An plotly figure.

        """
        
        if self.plot_mode == "notebook":
            iplot(fig)
        if self.plot_mode == "html":
            fig["layout"]["autosize"] = True
            h = random.getrandbits(128)
            fname = "%032x.html"%h
            plot(fig, output_type='file', filename=fname)


class SparkLinePlotter(TimeSeriesPlotter):
    titlestring = "Sparklines for %s"

    def plot(self, sample_freq):
        """Constructs a downsampled spark line plot of the time series.

        If there are more than 500 time points, the time series will be down sampled to
        500 column variables by windowed averaging. This is done by splitting the time series 
        into 500 equal sized segments in the time domain, then plotting the mean for each segment.

        Parameters
        ----------
        sample_freq : int
            The sampling frequency (how many times sampled per second).

        """
        title = self.titlestring % (self.resource_name)
        xaxis = dict(
            title = "Time in Seconds"
        )
        yaxis = dict(
            title = "Intensity"
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        if self.n > 500:
            winsize = self.n // 500
            df = pd.DataFrame(self.data.T)
            df = df.groupby(lambda x: x // winsize).mean()
            downsampled_data = df.as_matrix().T
            data = [dict(mode="lines",
                         hoverinfo="none",
                         x=(np.arange(downsampled_data.shape[1]) * winsize) / sample_freq,
                         y=downsampled_data[i, :]) for i in range(downsampled_data.shape[0])]
        fig = dict(data=data, layout=layout)
        self.makeplot(fig)

class CorrelationMatrixPlotter(TimeSeriesPlotter):
    titlestring = "Correlation Matrix for %s"

    def plot(self):
        title = self.titlestring % (self.resource_name)
        xaxis = dict(
            title = "Channels"
        )
        yaxis = dict(
                scaleanchor="x",
            title = "Channels"
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            C = np.nan_to_num(np.corrcoef(self.data))

        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = C)
        fig = dict(data=[trace], layout=layout)
        self.makeplot(fig)

class CoherenceMatrixPlotter(TimeSeriesPlotter):
    titlestring = "Coherence Matrix for %s"

    def plot(self, samp_freq = 500):
        title = self.titlestring % (self.resource_name)
        xaxis = dict(
            title = "Channels"
        )
        yaxis = dict(
                scaleanchor="x",
            title = "Channels"
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        C = np.zeros([self.d, self.d])
        for i in range(self.d):
            for j in range(i + 1):
                C[i, j] = np.mean(np.nan_to_num(signal.coherence(self.data[i, :],
                                                              self.data[j, :],
                                                              fs=samp_freq)[1]))
                C[j, i] = C[i, j]

        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = C)
        fig = dict(data=[trace], layout=layout)
        self.makeplot(fig)

class SpectrogramPlotter(TimeSeriesPlotter):
    titlestring = "Spectrograms for %s"

    def plot(self, channel = 0, sample_freq = 500):
        """Constructs a spectrogram plot of the time series.


        Parameters
        ----------
        sample_freq : int
            The sampling frequency (how many times sampled per second).

        """
        title = self.titlestring % (self.resource_name)
        xaxis = dict(
            title = "Hz",
            range = [0, 10]
        )
        yaxis = dict(
            title = "Intensity",
            range = [0, 1000]
        )
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)

        dt = 1./sample_freq
        sample_points = np.arange(self.data.T.shape[1]) * dt
        signal = self.data.T[channel, :]
        ft = np.fft.fft(signal) * dt
        ft = ft[: len(sample_points)//2]
        freq = np.fft.fftfreq(len(sample_points), dt)
        freq = freq[:len(sample_points)//2]

        trace = go.Scatter(
            x = freq[:2000],
            y = np.abs(ft)[:2000],
            mode = 'markers'
        )

        fig= dict(data=[trace], layout=layout)
        iplot(fig)

