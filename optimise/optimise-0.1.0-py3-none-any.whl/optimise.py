# -*- coding: utf-8 -*-
import yaml
import os
import sys
from time import time
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from .runs import Runs

from logcon import log
import logging


class Optimiser():
    """
    wrapper for hyperopt optimisation

    ### ADDITIONAL FUNCTIONALITY
        simplified search space
            max_depth=[8,10],       # int
            color=["r", "g", "b"],  # categoric
            normalize=[True,False], # bool
            c=[1., 5],              # float
            classifier="SVM"        # constant
            x=hp.lognormal("x",0,1) # the standard hyperopt format
        standard search spaces defined in yaml file
        log each iteration to file so resilient to crash
        plot results

    ### USAGE EXAMPLE
        from optimise.optimise import Optimiser

        def func(params):
            clf = RandomForestClassifier(n_estimators=100, verbose=0, n_jobs=-1, **params)
            return np.mean(cross_val_score(clf, X_train, y_train, scoring="roc_auc"))

        o = Optimiser()
        space = o.get_space("RandomForestClassifier")
        o.maximise(func, evals=50, space=space)
    """

    def __init__(self, folder="optimise", mode="w"):
        """
        folder for logging
        mode a=append, w=write
        """
        # int params need rounding due to hyperopt bug
        self.intparams = []
        self.scoresign = 1
        self.trials = Trials()
        self.runs = Runs(folder, mode)

    def convert(self, space):
        """ converts simple search space to hyperopt format
        """
        space = space.copy()
        for k, v in list(space.items()):
            # hypreopt expression or constant
            if not isinstance(v, list):
                continue

            # categoric and bool
            if len(v) > 2 \
                    or any(isinstance(v, str) for v in v) \
                    or any(isinstance(v, bool) for v in v):
                space[k] = hp.choice(k, v)
            # integer range
            elif all(isinstance(v, int) for v in v):
                space[k] = hp.quniform(k, v[0]-.5, v[1]+.5, 1)
                self.intparams.append(k)
            # float range
            else:
                space[k] = hp.uniform(k, v[0], v[1])
        return space

    def make_target(self, func, inputs):
        """ wrap func with pre and post processing
            func signature: score=func(params)
        """
        def target(params):
            """ called by optimiser for each iteration
            """
            starttime = time()

            # hyperopt integers stored as float (probably a bug)
            for k in self.intparams:
                params[k] = int(round(params[k]))

            # report params
            if self.verbose >= 20:
                paramsout = ', '.join(
                    f"{k!s}={v!r}" for (k, v) in params.items())
                log.info(f"[{len(self.trials)}] {paramsout}")

            #########################################
            funcparams = params.copy()
            funcparams.update(inputs)
            funcparams.pop("name")
            score = func(funcparams)
            #########################################

            # report score
            if self.verbose >= 20:
                log.info("****** %s ******" % score)

            # add iteration to trials object
            params.update(loss=score*self.scoresign,
                          status=STATUS_OK,
                          elapsed=time()-starttime)

            # save results so resilient to crash
            self.runs.append(params)

            return params

        return target

    def minimise(self, func, evals=1, verbose=20, clear=True,
                 inputs=dict(), **hpargs):
        """
        minimise func by varying parameters

        func=signature func(params). returns score to minimise
        evals=number of function evaluations excluding previous
        verbose=report each iteration
        clear=clear output before printing summary

        inputs=constants passed to each iteration e.g. x, y
                optional as can be set in class or in notebook
        hpargs=passed to hyperopt
        hpargs["space"]=simplified hyperopt space to be converted to hp format
        """
        logging.getLogger("hyperopt.tpe").setLevel(logging.WARNING)
        self.verbose = verbose

        self.trials = hpargs.get("trials", self.trials)
        hpargs["trials"] = self.trials

        hpargs.setdefault("max_evals", len(self.trials) + evals)
        hpargs.setdefault("algo", tpe.suggest)
        hpargs["space"] = self.convert(hpargs["space"])

        target = self.make_target(func, inputs)

        try:
            fmin(target, **hpargs)
        except KeyboardInterrupt:
            pass

        # output results
        self.runs.show_best(clear=clear)
        self.runs.plot()

    def maximise(self, *args, **kwargs):
        """ maximise func by varying parameters """
        self.scoresign = -1
        self.minimise(*args, **kwargs)

    def minimise_by_parameter(self,  *args, **kwargs):
        """ univariate runs of params """
        for k, v in kwargs["space"].items():
            if k in ["name"]:
                continue
            kwargs["trials"] = Trials()
            kwargs["space"] = {k: v}
            self.optimise(*args, **kwargs)

    def maximise_by_parameter(self, *args, **kwargs):
        self.scoresign = -1
        self.minimise(*args, **kwargs)

###############################################################

    def get_space(self, key, folder=None):
        """ lookup space using key in search.yaml
        """
        for path in [folder,
                     os.path.join(sys.prefix, "etc", "optimise"),
                     os.path.join(os.path.dirname(__file__), os.pardir)]:
            try:
                space = yaml.load(open(os.path.join(path, "search.yaml")))[key]
                space["name"] = key
                break
            except:
                continue

        return space

    def get_params_range(self, params, excluded=None, spread=None):
        """ gets params space in range
            spread is either side of params.values()
            e.g. v=10, spread=[.9, 1.1] ==> v=[9, 11]
        """
        if spread is None:
            spread = [.9, 1.1]
        for k, v in params.items():
            if k in excluded:
                continue
            if isinstance(v, float):
                params[k] = [v*spread[0], v*spread[1]]
            elif isinstance(v, int):
                params[k] = [round(v*spread[0]), round(v*spread[1])]
