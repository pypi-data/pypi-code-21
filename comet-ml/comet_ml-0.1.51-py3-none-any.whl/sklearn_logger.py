import sys
from comet_ml import config


# def accuracy_score_logger(accuracy):
#     def wrapper(*args, **kwargs):
#         result = accuracy(*args, **kwargs)
#         config.experiment.log_metric("accuracy",result)
#         return result
#     return wrapper

def fit_logger(real_fit):
    def wrapper(*args, **kwargs):
        try:
            ret_val = real_fit(*args, **kwargs)
            config.experiment.log_multiple_params(ret_val.get_params())
            return ret_val
        except:
            print("Failed to extract parameters from estimator")
            return real_fit(*args, **kwargs)

    return wrapper


def pipeline_fit_logger(real_fit):
    def wrapper(*args, **kwargs):
        try:
            ret_val = real_fit(*args, **kwargs)

            params = ret_val.get_params()
            if params is not None and "steps" in params:
                for step in params["steps"]:
                    step_name, step_mdl = step
                    config.experiment.log_multiple_params(step_mdl.get_params(), prefix=step_name)

            return ret_val
        except:
            print("Comet: Failed to extract parameters from Pipeline")
            return real_fit(*args, **kwargs)

    return wrapper


def patch():
    if sys.version_info[0] >= 3:
        from comet_ml.class_loader_py3 import Finder

        sys.meta_path.insert(0, Finder('sklearn.pipeline', "fit", pipeline_fit_logger, class_name="Pipeline"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.stochastic_gradient', "fit", fit_logger,
                                       class_name="SGDClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.ensemble.weight_boosting', "fit", fit_logger,
                                       class_name="AdaBoostClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.ensemble.bagging', "fit", fit_logger, class_name="BaggingClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.naive_bayes', "fit", fit_logger, class_name="BernoulliNB"))
        sys.meta_path.insert(0, Finder('sklearn.calibration', "fit", fit_logger, class_name="CalibratedClassifierCV"))
        sys.meta_path.insert(0, Finder('sklearn.tree.tree', "fit", fit_logger, class_name="DecisionTreeClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.tree.tree', "fit", fit_logger, class_name="ExtraTreeClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.ensemble.forest', "fit", fit_logger, class_name="ExtraTreesClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.naive_bayes', "fit", fit_logger, class_name="GaussianNB"))
        sys.meta_path.insert(0, Finder('sklearn.gaussian_process.gpc', "fit", fit_logger,
                                       class_name="GaussianProcessClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.ensemble.gradient_boosting', "fit", fit_logger,
                                       class_name="GradientBoostingClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.neighbors.classification', "fit", fit_logger,
                                       class_name="KNeighborsClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.semi_supervised.label_propagation', "fit", fit_logger,
                                       class_name="LabelPropagation"))
        sys.meta_path.insert(0, Finder('sklearn.semi_supervised.label_propagation', "fit", fit_logger,
                                       class_name="LabelSpreading"))
        sys.meta_path.insert(0, Finder('sklearn.discriminant_analysis', "fit", fit_logger,
                                       class_name="LinearDiscriminantAnalysis"))
        sys.meta_path.insert(0, Finder('sklearn.svm.classes', "fit", fit_logger, class_name="LinearSVC"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.logistic', "fit", fit_logger,
                                       class_name="LogisticRegression"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.logistic', "fit", fit_logger,
                                       class_name="LogisticRegressionCV"))
        sys.meta_path.insert(0, Finder('sklearn.neural_network.multilayer_perceptron', "fit", fit_logger,
                                       class_name="MLPClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.naive_bayes', "fit", fit_logger, class_name="MultinomialNB"))
        sys.meta_path.insert(0, Finder('sklearn.neighbors.nearest_centroid', "fit", fit_logger,
                                       class_name="NearestCentroid"))
        sys.meta_path.insert(0, Finder('sklearn.svm.classes', "fit", fit_logger, class_name="NuSVC"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.passive_aggressive', "fit", fit_logger,
                                       class_name="PassiveAggressiveClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.perceptron', "fit", fit_logger, class_name="Perceptron"))
        sys.meta_path.insert(0, Finder('sklearn.discriminant_analysis', "fit", fit_logger,
                                       class_name="QuadraticDiscriminantAnalysis"))
        sys.meta_path.insert(0, Finder('sklearn.neighbors.classification', "fit", fit_logger,
                                       class_name="RadiusNeighborsClassifier"))
        sys.meta_path.insert(0,
                             Finder('sklearn.ensemble.forest', "fit", fit_logger, class_name="RandomForestClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.ridge', "fit", fit_logger, class_name="RidgeClassifier"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.ridge', "fit", fit_logger, class_name="RidgeClassifierCV"))

        sys.meta_path.insert(0, Finder('sklearn.svm.classes', "fit", fit_logger, class_name="SVC"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.bayes', "fit", fit_logger, class_name="ARDRegression"))
        sys.meta_path.insert(0, Finder('sklearn.ensemble.weight_boosting', "fit", fit_logger,
                                       class_name="AdaBoostRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.ensemble.bagging', "fit", fit_logger, class_name="BaggingRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.bayes', "fit", fit_logger, class_name="BayesianRidge"))
        sys.meta_path.insert(0, Finder('sklearn.cross_decomposition.cca_', "fit", fit_logger, class_name="CCA"))
        sys.meta_path.insert(0, Finder('sklearn.tree.tree', "fit", fit_logger, class_name="DecisionTreeRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.coordinate_descent', "fit", fit_logger,
                                       class_name="ElasticNet"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.coordinate_descent', "fit", fit_logger,
                                       class_name="ElasticNetCV"))
        sys.meta_path.insert(0, Finder('sklearn.tree.tree', "fit", fit_logger, class_name="ExtraTreeRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.ensemble.forest', "fit", fit_logger, class_name="ExtraTreesRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.gaussian_process.gaussian_process', "fit", fit_logger,
                                       class_name="GaussianProcess"))
        sys.meta_path.insert(0, Finder('sklearn.gaussian_process.gpr', "fit", fit_logger,
                                       class_name="GaussianProcessRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.ensemble.gradient_boosting', "fit", fit_logger,
                                       class_name="GradientBoostingRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.huber', "fit", fit_logger, class_name="HuberRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.neighbors.regression', "fit", fit_logger,
                                       class_name="KNeighborsRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.kernel_ridge', "fit", fit_logger, class_name="KernelRidge"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.least_angle', "fit", fit_logger, class_name="Lars"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.least_angle', "fit", fit_logger, class_name="LarsCV"))
        sys.meta_path.insert(0,
                             Finder('sklearn.linear_model.coordinate_descent', "fit", fit_logger, class_name="Lasso"))
        sys.meta_path.insert(0,
                             Finder('sklearn.linear_model.coordinate_descent', "fit", fit_logger, class_name="LassoCV"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.least_angle', "fit", fit_logger, class_name="LassoLars"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.least_angle', "fit", fit_logger, class_name="LassoLarsCV"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.least_angle', "fit", fit_logger, class_name="LassoLarsIC"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.base', "fit", fit_logger, class_name="LinearRegression"))
        sys.meta_path.insert(0, Finder('sklearn.svm.classes', "fit", fit_logger, class_name="LinearSVR"))
        sys.meta_path.insert(0, Finder('sklearn.neural_network.multilayer_perceptron', "fit", fit_logger,
                                       class_name="MLPRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.coordinate_descent', "fit", fit_logger,
                                       class_name="MultiTaskElasticNet"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.coordinate_descent', "fit", fit_logger,
                                       class_name="MultiTaskElasticNetCV"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.coordinate_descent', "fit", fit_logger,
                                       class_name="MultiTaskLasso"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.coordinate_descent', "fit", fit_logger,
                                       class_name="MultiTaskLassoCV"))
        sys.meta_path.insert(0, Finder('sklearn.svm.classes', "fit", fit_logger, class_name="NuSVR"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.omp', "fit", fit_logger,
                                       class_name="OrthogonalMatchingPursuit"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.omp', "fit", fit_logger,
                                       class_name="OrthogonalMatchingPursuitCV"))
        sys.meta_path.insert(0,
                             Finder('sklearn.cross_decomposition.pls_', "fit", fit_logger, class_name="PLSCanonical"))
        sys.meta_path.insert(0,
                             Finder('sklearn.cross_decomposition.pls_', "fit", fit_logger, class_name="PLSRegression"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.passive_aggressive', "fit", fit_logger,
                                       class_name="PassiveAggressiveRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.ransac', "fit", fit_logger, class_name="RANSACRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.neighbors.regression', "fit", fit_logger,
                                       class_name="RadiusNeighborsRegressor"))
        sys.meta_path.insert(0,
                             Finder('sklearn.ensemble.forest', "fit", fit_logger, class_name="RandomForestRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.ridge', "fit", fit_logger, class_name="Ridge"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.ridge', "fit", fit_logger, class_name="RidgeCV"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.stochastic_gradient', "fit", fit_logger,
                                       class_name="SGDRegressor"))
        sys.meta_path.insert(0, Finder('sklearn.svm.classes', "fit", fit_logger, class_name="SVR"))
        sys.meta_path.insert(0, Finder('sklearn.linear_model.theil_sen', "fit", fit_logger,
                                       class_name="TheilSenRegressor"))
    else:
        from comet_ml import class_loader_py2

        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'pipeline', "Pipeline", "fit", pipeline_fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'naive_bayes', 'BernoulliNB', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'calibration', 'CalibratedClassifierCV', 'fit',
        #                                                 fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'naive_bayes', 'GaussianNB', 'fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'naive_bayes', 'MultinomialNB', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'discriminant_analysis',
        #                                                 'QuadraticDiscriminantAnalysis', 'fit', fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'discriminant_analysis', 'LinearDiscriminantAnalysis',
        #                                              'fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'kernel_ridge', 'KernelRidge', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'ensemble', 'weight_boosting', 'AdaBoostClassifier','fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'ensemble', 'bagging', 'BaggingClassifier', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'tree', 'tree', 'DecisionTreeClassifier', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'tree', 'tree', 'ExtraTreeClassifier', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'ensemble', 'forest', 'ExtraTreesClassifier', 'fit',fit_logger))
        #sys.meta_path.insert(0,class_loader_py2.Finder('sklearn', 'gaussian_process', 'gpc', 'GaussianProcessClassifier','fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'ensemble', 'gradient_boosting','GradientBoostingClassifier', 'fit', fit_logger))
        #sys.meta_path.insert(0,class_loader_py2.Finder('sklearn', 'neighbors', 'classification', 'KNeighborsClassifier','fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'semi_supervised', 'label_propagation','LabelPropagation', 'fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'semi_supervised', 'label_propagation','LabelSpreading', 'fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'svm', 'classes', 'LinearSVC', 'fit', fit_logger))
        #sys.meta_path.insert(0,class_loader_py2.Finder('sklearn', 'linear_model', 'logistic', 'LogisticRegression', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'logistic', 'LogisticRegressionCV','fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'neural_network', 'multilayer_perceptron','MLPClassifier', 'fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'neighbors', 'nearest_centroid', 'NearestCentroid','fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'svm', 'classes', 'NuSVC', 'fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'passive_aggressive','PassiveAggressiveClassifier', 'fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'perceptron', 'Perceptron', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'neighbors', 'classification','RadiusNeighborsClassifier', 'fit', fit_logger))
        #sys.meta_path.insert(0,class_loader_py2.Finder('sklearn', 'ensemble', 'forest', 'RandomForestClassifier', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'ridge', 'RidgeClassifier', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'ridge', 'RidgeClassifierCV', 'fit',fit_logger))
        #sys.meta_path.insert(0,class_loader_py2.Finder('sklearn', 'linear_model', 'stochastic_gradient', 'SGDClassifier','fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'svm', 'classes', 'SVC', 'fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'bayes', 'ARDRegression', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'ensemble', 'weight_boosting', 'AdaBoostRegressor','fit', fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'ensemble', 'bagging', 'BaggingRegressor', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'bayes', 'BayesianRidge', 'fit',fit_logger))
        #sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'cross_decomposition', 'cca_', 'CCA', 'fit',fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'tree', 'tree', 'DecisionTreeRegressor', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'coordinate_descent', 'ElasticNet',
        #                                                 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'coordinate_descent', 'ElasticNetCV',
        #                                                 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'tree', 'tree', 'ExtraTreeRegressor', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'ensemble', 'forest', 'ExtraTreesRegressor', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'gaussian_process', 'gaussian_process',
        #                                                 'GaussianProcess', 'fit', fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'gaussian_process', 'gpr', 'GaussianProcessRegressor',
        #                                              'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'ensemble', 'gradient_boosting',
        #                                                 'GradientBoostingRegressor', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'huber', 'HuberRegressor', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'neighbors', 'regression', 'KNeighborsRegressor', 'fit',
        #                                              fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'least_angle', 'Lars', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'least_angle', 'LarsCV', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'coordinate_descent', 'Lasso', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'linear_model', 'coordinate_descent', 'LassoCV', 'fit',
        #                                              fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'least_angle', 'LassoLars', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'least_angle', 'LassoLarsCV', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'least_angle', 'LassoLarsIC', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'base', 'LinearRegression', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'svm', 'classes', 'LinearSVR', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'neural_network', 'multilayer_perceptron',
        #                                                 'MLPRegressor', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'coordinate_descent',
        #                                                 'MultiTaskElasticNet', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'coordinate_descent',
        #                                                 'MultiTaskElasticNetCV', 'fit', fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'linear_model', 'coordinate_descent', 'MultiTaskLasso',
        #                                              'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'coordinate_descent',
        #                                                 'MultiTaskLassoCV', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'svm', 'classes', 'NuSVR', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'omp', 'OrthogonalMatchingPursuit',
        #                                                 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'omp', 'OrthogonalMatchingPursuitCV',
        #                                                 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'cross_decomposition', 'pls_', 'PLSCanonical', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'cross_decomposition', 'pls_', 'PLSRegression', 'fit',
        #                                              fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'passive_aggressive',
        #                                                 'PassiveAggressiveRegressor', 'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'ransac', 'RANSACRegressor', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'neighbors', 'regression', 'RadiusNeighborsRegressor',
        #                                              'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'ensemble', 'forest', 'RandomForestRegressor', 'fit',
        #                                                 fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'linear_model', 'ridge', 'Ridge', 'fit', fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'linear_model', 'ridge', 'RidgeCV', 'fit', fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'linear_model', 'stochastic_gradient', 'SGDRegressor',
        #                                              'fit', fit_logger))
        # sys.meta_path.insert(0, class_loader_py2.Finder('sklearn', 'svm', 'classes', 'SVR', 'fit', fit_logger))
        # sys.meta_path.insert(0,
        #                      class_loader_py2.Finder('sklearn', 'linear_model', 'theil_sen', 'TheilSenRegressor', 'fit',
        #                                              fit_logger))


if "sklearn" in sys.modules:
    raise SyntaxError("Please import comet before importing any sklearn modules")

patch()

# https://blog.sqreen.io/dynamic-instrumentation-agent-for-python/
