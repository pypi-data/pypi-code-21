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
        self.label_name = primary_label
        if type(dm.dataset).__name__ == 'DFDataSet':
            self.label = dm.dataset.D.index
        elif type(dm.dataset).__name__ == 'DiskDataSet':
            self.label = dm.dataset.D[primary_label]
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
            


class DistanceMatrixHeatmap(DistanceMatrixPlotter):
    titlestring = "%s Distance Matrix Heatmap under %s metric"

    def plot(self):
        """Constructs a distance matrix heatmap using the :obj:`DistanceMatrix` object, in plotly.

        """
        title = self.titlestring % (self.dataset_name, self.metric_name)
        xaxis = go.XAxis(
                title="data points",
                ticktext = self.label,
                ticks = "",
                showticklabels=False,
                showgrid=False,
                mirror=True,
                tickvals = [i for i in range(len(self.label))])
        yaxis = go.YAxis(
                scaleanchor="x",
                title="data points",
                ticktext = self.label,
                showgrid=False,
                ticks = "",
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(len(self.label))])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = self.dm)
        data = [trace]
        fig = dict(data=data, layout=layout)
        self.makeplot(fig)

class DistanceMatrixEigenvectorHeatmap(DistanceMatrixPlotter):
    titlestring = "%s Distance Matrix Eigenvector Heatmap under %s metric"

    def plot(self):
        """Constructs an eigenvector heatmap of the :obj:`DistanceMatrix` object, in plotly.

        This essentially a heatmap of the square left eigenvector matrix.

        """
        title = self.titlestring % (self.dataset_name, self.metric_name)
        U, _, _ = np.linalg.svd(self.dm, full_matrices=False)
        xaxis = go.XAxis(
                title="eigenvectors",
                ticktext = ["Eigenvector %s"%i for i in range(1, len(self.label) + 1)],
                ticks = "",
                showgrid=False,
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(len(self.label))])
        yaxis = go.YAxis(
                title="eigenvector components",
                scaleanchor="x",
                showgrid=False,
                ticktext = ["Component %s"%i for i in range(1, len(self.label) + 1)],
                ticks = "",
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(len(self.label))])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = U)
        data = [trace]
        fig = dict(data=data, layout=layout)
        self.makeplot(fig)

class DistanceMatrixScreePlotter(DistanceMatrixPlotter): 
    titlestring = "%s Distance Matrix Scree Plot under %s metric"

    def plot(self):
        """Constructs a scree plot of the spectrum of the :obj:`DistanceMatrix` object, in plotly.

        """
        title = self.titlestring % (self.dataset_name, self.metric_name)
        _, S, _ = np.linalg.svd(self.dm, full_matrices=False)
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
            self.label_name: self.label
        }
        D = pd.DataFrame(d)
        sns.lmplot('factor 1',
                   'factor 2',
                    data = D,
                    fit_reg = False,
                    hue=self.label_name)
        plt.title(title)
        plt.show()

class EmbeddingHeatmap(DistanceMatrixPlotter):
    titlestring = "%s %s Embedding Heatmap under %s metric"

    def plot(self, embedder):
        """Constructs a heatmap of the embedded :obj:`DistanceMatrix` object.

        Parameters
        ----------
        embedder : :obj:`BaseEmbedder`
            An embedder object which should be used to embed the data.

        """
        title = self.titlestring % (self.dataset_name, embedder.embedding_name, self.metric_name)
        emb = embedder.embed(self.dm).T
        xaxis = go.XAxis(
                title="data points",
                ticktext = self.label,
                ticks = "",
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(len(self.label))])
        yaxis = go.YAxis(
                title="embedding dimensions",
                ticktext = ["factor %s"%i for i in range(1, len(self.label) + 1)],
                ticks = "",
                showticklabels=False,
                mirror=True,
                tickvals = [i for i in range(len(self.label))])
        layout = dict(title=title, xaxis=xaxis, yaxis=yaxis)
        trace = go.Heatmap(z = emb)
        data = [trace]
        fig = dict(data=data, layout=layout)
        self.makeplot(fig)

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
        Pdf[self.label_name] = self.label
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
        unique_labels = np.unique(self.label)
        label_to_number = dict(zip(unique_labels, range(1, len(unique_labels) + 1)))
        dims = [dict(label = "factor %s"%(x + 1),
                values = D[x, :]) for x in range(embedder.num_components)]
        line = dict(color = [label_to_number[x] for x in self.label],
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
        unique_labels = np.unique(self.label)
        label_to_number = dict(zip(unique_labels, range(1, len(unique_labels) + 1)))
        number_labels = [label_to_number[l] for l in self.label]
        def distance_function(x):
            flattened = self.dm[np.triu_indices(self.dm.shape[0], k=1)].flatten()
            return [f for f in flattened] 
        dendro = ff.create_dendrogram(X = observations,
                                      distfun = distance_function,
                                      labels=number_labels)
        dendro.layout.update(dict(title=title))
        dendro.layout.xaxis.update(dict(ticktext=self.label,
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
        self.mode = mode

    def makeplot(self, fig):
        if self.plot_mode == "notebook":
            iplot(fig)
        if self.plot_mode == "html":
            plot(fig, output_type='file', filename="tempplot.html")

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
