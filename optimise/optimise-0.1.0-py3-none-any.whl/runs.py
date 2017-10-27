# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import logging as log
from IPython.display import clear_output
import shutil
import json

from .gridplot import Gridplot
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


class Runs():
    """
    collection of model runs with params, scores and predictions
        logruns.json is list of json objects with params and scores
        preds0 is predictions for first row of logruns.json

    logruns format allows for different parameters in each run
    """
    excluded = ["elapsed", "loss", "status"]

    def __init__(self, folder, mode="a"):
        """
        folder is location for log and preds files
        mode a=append, w=write
        """
        self.folder = folder
        self.file = os.path.join(folder, "logruns.json")

        if mode == "w":
            shutil.rmtree(folder, ignore_errors=True)
            os.makedirs(folder, exist_ok=True)
            self.rows = 0
        else:
            with open(self.file) as f:
                self.rows = len(f.readlines())

    def append(self, row, preds=None):
        """ append row to log
            save preds to file
        """
        # append row to log
        with open(self.file, "a") as f:
            row = {k: str(v) for k, v in row.items()}
            json.dump(row, f)
            f.write("\n")

        # save predictions
        if preds:
            with open(os.path.join(self.folder,
                                   f"preds{self.rows}"), "wb") as f:
                np.save(f, preds)

        self.rows += 1

    def read(self):
        """ return logruns as dataframe """
        try:
            # each row is a json object. convert to "," delimited list
            with open(self.file) as f:
                data = [json.loads(row) for row in f.read().splitlines()]
        except FileNotFoundError as e:
            data = []
        df = pd.DataFrame(data)

        # convert numerics to float
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass

        # convert floats with nulls back to integer or bool
        for col in df.select_dtypes(include=[np.float]).columns:
            df[col] = df[col].fillna(0)
            if all(x.is_integer() for x in df[col]):
                if df[col].min() == 0 and df[col].max() == 1:
                    df[col] = df[col].astype(bool)
                else:
                    df[col] = df[col].astype(int)
        return df

    def show_best(self, clear=True):
        """ report best run """
        if clear:
            clear_output()

        df = self.read()

        # print best
        best = df.ix[df.loss.idxmin()].to_dict()
        best_params = ', '.join(f"{k!s}={v!r}"
                                for (k, v) in best.items()
                                if k not in self.excluded
                                and v)
        print("Best model:\n%s" % (best_params))
        print("loss=%s" % (best["loss"]))

    def plot(self, metric="loss", aggfunc="mean"):
        """ plot results by parameter
        metric = loss, elapsed
        aggfunc = mean, var, count
        """
        df = self.read()

        # looks better plotted as positive
        df[metric] = df[metric].apply(abs)

        # show the plots in a grid
        Gridplot()

        # overall plot including all runs
        plt.plot(range(1, len(df)+1), df[metric])
        plt.title("%s by run" % metric)
        ax = plt.gca()
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.ylabel(metric)

        # plots for each parameter
        for param in df.drop(self.excluded, axis=1):
            agg = df.groupby(param).agg(aggfunc)

            if len(agg) < 2:
                # 0=not used 1=constant
                continue
            # lineplot for numeric
            if agg.index.is_numeric():
                plt.plot(agg.index, agg[metric])
                if agg.index.is_integer():
                    ax = plt.gca()
                    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            else:
                # barchart for category
                xpos = np.arange(len(agg))
                plt.bar(xpos, agg[metric], align='center', alpha=0.5)
                plt.xticks(xpos, agg.index)
                plt.ylim(min(agg[metric])*.98, max(agg[metric]*1.02))
            plt.title(param)
            plt.ylabel(metric)
        plt.tight_layout()
        plt.show()

    def barchart(self):
        """ barchart comparing scores between models
        """
        df = pd.DataFrame(self.results,
                          index=range(len(self.results)))["name", "loss"]
        df.loss = df.loss.apply(abs)

        plt.figure(figsize=((10, 5)))
        plt.xlim(df.score.min()*.98, df.score.max()*1.02)
        df = df.set_index("name")
        df.loss.plot(kind="barh", legend=False)
        plt.title("CV scores")

    def get_correlations(self):
        """ return dataframe with scores and correlations for all runs
            candidates for ensemble need high scores, low correlations
        """
        # get prediction data and correlate
        predfiles = [f for f in os.listdir(
            self.folder) if f.startswith("preds")]
        data = []
        for pred in predfiles:
            with open(os.path.join(self.folder, pred), "rb") as f:
                data.append(np.load(f).reshape(-1))
        df = pd.DataFrame(np.corrcoef(data))

        runs = self.read()

        # add row and column labels
        df.index.name = "runid1"
        df.columns = df.index.copy()
        df.columns.name = "runid2"

        # stack correlations. index is runid1/runid2
        df = pd.DataFrame(df.stack())
        df.columns = ["r2"]
        df = df.reset_index()
        df = df[df.runid1 != df.runid2]

        # add scores and names
        df["score1"] = df.runid1.map(runs.score)
        df["score2"] = df.runid2.map(runs.score)
        df["name1"] = df.runid1.map(runs.name)
        df["name2"] = df.runid2.map(runs.name)

        df = df.sort_values(["r2"])
        return df

    def plot_correlations(self, runid):
        """ scatter plot a runid against other runs to find
        candidates for ensemble """
        df = self.get_correlations()
        df = df[(df.runid1 == runid) & (df.runid2 != runid)]
        plt.plot(df.r2, df.score2, "o")
        plt.title("model %s" % runid)
        plt.xlabel("correlation")
        plt.ylabel("score")
        plt.gca().invert_xaxis()
        for row in df.itertuples():
            plt.annotate(row.runid2, (row.r2, row.score2))
