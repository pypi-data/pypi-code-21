import pymc3 as pm, theano.tensor as tt



# Below we have code for calculating PLS balances
def _solve(w1, w2, m1, m2, std1, std2):
    # from stackoverflow
    # https://stackoverflow.com/a/22579904/1167475
    a = 1/(2*std1**2) - 1/(2*std2**2)
    b = m2/(std2**2) - m1/(std1**2)
    c = m1**2 /(2*std1**2) - m2**2 / (2*std2**2) - np.log((w1/w2) * np.sqrt(std2/std1))
    return np.roots([a,b,c])


class Gaussian3Mixture():
    """
    Gaussian Mixture Model with 3 components and very specific priors.
    """
    def __init__(data):
        """
        Parameters
        ----------
        data : np.array
           1 dimensional array that will be fitted.
        """
        ndata = len(data)
        k = 3
        self.model = pm.Model()
        with model:
            # cluster sizes
            p = pm.Dirichlet('p',
                             # prior with everything equally weighted
                             a=np.array([1., 1., 1.]), shape=k)
            # ensure all clusters have some points
            p_min_potential = pm.Potential('p_min_potential',
                                           tt.switch(tt.min(p) < .1, -np.inf, 0))


            # cluster centers
            self.means = pm.Normal('means', mu=[-1, 0, 1], sd=5, shape=k)
            # break symmetry
            order_means_potential = pm.Potential(
                'order_means_potential',
                tt.switch(means[1]-means[0] < 0, -np.inf, 0)
                + tt.switch(means[2]-means[1] < 0, -np.inf, 0)
                + tt.switch(means[0] > 0, -np.inf, 0)
                + tt.switch(means[2] < 0, -np.inf, 0)
            )

            # measurement error
            self.sd = pm.Uniform('sd', lower=0, upper=5)

            # latent cluster of each observation
            self.category = pm.Categorical('category',
                                           p=p,
                                           shape=ndata)

            # likelihood for each observed value
            points = pm.Normal('obs',
                               mu=means[category],
                               sd=sd,
                               observed=data)
    def fit(steps=10000):
        # fit model
        with model:
            step1 = pm.Metropolis(vars=[self.p, self.sd, self.means])
            step2 = pm.ElemwiseCategorical(vars=[self.category], values=[0, 1, 2])
            self.trace = pm.sample(steps, step=[step1, step2])

    def means(burnin=1000):
        return np.median(self.trace.means[burnin:, :], axis=0)

    def p(burnin=1000):
        return np.median(self.trace.p[burnin:, :], axis=0)

    def plot(burnin=1000):
        return pm.plots.traceplot(self.trace[burnin:],
                                  ['p', 'sd', 'means']);
