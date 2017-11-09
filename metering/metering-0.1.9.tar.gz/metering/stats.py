# -*- coding: utf-8 -*-
"""
Created on Mon Oct 05 11:09:02 2015

@author: Ari.Jackson
The Cadmus Group, Inc.

A module for determining sample sizes for EM&V

Sources:

Montgomery, Douglas C., and George C. Runger.
    Appplied Statistics and Probability for Engineers. 5th ed. N.p.:
    John Wiley & Sons, 2011. Print.

Desu, M.m., and D. Raghavarao. "Samples from Finite Populations.
    "Sample Size Methodology (1990): n. pag. Web.

"2.3 Conidence and Precision." Uniform Methods Project Comment Process.
    National Reneable Energy Laboratory, 21 July 2012. Web. 30 Nov. 2015.

(url: http://ump.pnnl.gov/showthread.php/5106-2.3-Confidence-and-Precision)

Regarding the definition of precision:

From UMP-
Precision provides convenient shorthand for expressing the interval believed
to contain the estimator (for example, if the estimate is 530 kWh, and the
relative precision level is 10%, then the interval is 530 \pm  kWh).
(FOOTNOTE 4) In reporting estimates from a sample, it is essential to provide
both the precision and its corresponding confidence level (typically 90% for
energy-efficiency evaluations).

From Montgomery-
The length of a confidence interval is a measure of the precision of
estimation...2E is the length of the resulting confidence interval.
"""

import pandas as pd
import random
import math
from math import floor
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib
from scipy import stats
matplotlib.rcParams.update(matplotlib.rcParamsDefault)


def relative_precision(series, confidence, dist):
    """Calculate precision and confidence interval of a pandas series at
       desired confidence with assumed distribution.

       Arguments:
       series: pd.Series containing dataset
       confidence: desired confidence used to calculate the interval,
                   enered as a decimal
       dist: 't' or 'norm'
    """
    x = series.mean()  # sample mean
    s = series.std()  # sample standard deviation
    n = series.size  # sample size
    k = n - 1  # degrees of freedom
    q = 1 - ((1 - confidence) / 2.0)  # upper tail probability
    if dist == 't':
        ts = stats.t.ppf(q, k)  # t test statistic
    elif dist == 'norm':
        ts = stats.norm.ppf(q)  # z test statistic
    ub = x + ts * s / n ** 0.5  # lower bound
    lb = x - ts * s / n ** 0.5  # upper bound
    # This definition of precision is different than I learned, but is
    # consistent with the uniform methods project.
    # Source:
    #  https://ump.pnnl.gov/showthread.php/5106-2.3-Confidence-and-Precision
    p = (ub - lb) / x * 100.0 / 2.0
    return lb, x, ub, p


def precision(series, confidence, dist):
    """Calculate precision and confidence interval of a pandas series at
       desired confidence with assumed distribution.

       Arguments:
       series: pd.Series containing dataset
       confidence: desired confidence used to calculate the interval,
                   enered as a decimal
       dist: 't' or 'norm'
    """
    x = series.mean()  # sample mean
    s = series.std()  # sample standard deviation
    n = series.size  # sample size
    k = n - 1  # degrees of freedom
    q = 1 - ((1 - confidence) / 2.0)  # upper tail probability
    if dist == 't':
        ts = stats.t.ppf(q, k)  # t test statistic
    elif dist == 'norm':
        ts = stats.norm.ppf(q)  # z test statistic
    ub = x + ts * s / n ** 0.5  # lower bound
    lb = x - ts * s / n ** 0.5  # upper bound
    # This definition of precision is different than I learned, but is
    # consistent with the uniform methods project.
    # Source:
    #  https://ump.pnnl.gov/showthread.php/5106-2.3-Confidence-and-Precision
    p = (ub - lb) / 2.0
    return lb, x, ub, p


# A class with tools used to determine sample sizes when preforming inference
# on a population mean.
class MeanSam():

    # A text book method for choosing a sample size for specified error on the
    # mean with known variance.
    @staticmethod
    def z_sample(c, p, CV):
        '''inputs: confidence, precision, coefficient of variation.'''
        Z = stats.norm.ppf((1 - c) / float(2))
        E = p / float(2)
        n = ((Z * CV) / E) ** 2
        return int(math.ceil(n))

    # A helper method to calculate sample sizes given a sample size. Part of
    # the reason this function is needed is because a T statistic takes
    # degrees of freedom as an input and so the process of determining a
    # sample size is iterative.
    @staticmethod
    def t_sample(N, n, c, p, cv):
        ''' Inputs: population size, sample size, confidence, precision,
            coefficient of variance. Use when estimating a mean with unknown
            variance and small sample size. '''
        # Area outside confidence interval
        a = float(1 - c)
        # Area outside a single tail of the confidence interval
        a_2 = a / 2.
        # degrees of freedom
        k = n - 1
        # test statistic for a t distriubtion
        t = stats.t.ppf(a_2, k)
        # error is 1/2 precision (precision is the length of the confidence
        # interval)
        e = float(p) / 2
        # sample size
        n_0 = (t * cv / e)**2
        # sample size after applying finite population correction and rounding
        # up. The reason for using int() is for later comparison.
        return int(math.ceil(n_0 / (1 + (n_0 - 1) / N)))

    # A method to iteratively determine a sample size for a t distribution.
    @staticmethod
    def iterative_t_sample(N, c, p, cv):
        ''' Inputs: population size, confidence, precision, coefficient of
            variance '''
        # Initially an assumption is neded about hte sample size so a test
        # statistic can be calculated and in this case we use the population
        # size.
        n_0 = N
        # Under this assumed sample size we calculate a new sample size n_1
        # which is initalized here.
        n_1 = 0
        # While n_0 and n_1 are not equal we'll decrease n_0 and recalculate
        # n_1 under this new assumption. The reason for breaking the while
        # loop when n_0 is equal to 2 (we're decrementing by 1 so it can't be
        # less) is that degrees of freedom that are calculated in t_sample are
        # equal to n - 1 so if n was less than 2 we'd have zero degrees of
        # freedom which doesn't allow for the calculation of a test statistic.
        while (n_1 != n_0) and (n_0 != 2):
            n_1 = MeanSam.t_sample(N, n_0, c, p, cv)
            # We'll only decrement n_0 if it's greater than n_1 because because
            # n_0 is initially larger and we want the two to be equal.
            if n_1 < n_0:
                n_0 -= 1
        # There are cases where we overshoot n_0, which we can test for by
        # calling t_sample, and is corrected by incrementing n_0
        if n_0 < MeanSam.t_sample(N, n_0, c, p, cv):
            n_0 += 1
        return n_0

    # A method to create a random selection of 'line items' to be metered
    @staticmethod
    def random_sample(N, n):
        ''' Inputs: population size, sample size '''
        # Initlaize list to store sample
        sample = []
        # Append random integers to list until the sample size is reached
        while len(sample) < n:
            # Generate a random number that is less than or equal to the
            # population size. Convert to int so output looks nicer and
            # potentially some other reason as well.
            rv = int(math.ceil(random.random() * N))
            # Only append rv if it's not already in the list
            if sample.count(rv) == 0:
                sample.append(rv)
        sample.sort()
        return sample

    # A method to plot sample sizes vs population sizes given a range of
    # assumptions about the coefficient of variation.
    @staticmethod
    def plot_mean_samples():
        matplotlib.style.use('ggplot')
        population_range = np.arange(5, 201, 1)
        # cv_range = np.arange(.25, .55, .05)
        cv = .25
        c = .9
        # According the Uniform Methods Project 10% precision implies +\-.1,
        # this interpretation is different than that presented in statistics
        # textbooks, that precision is the length of the confidence interval.
        # While normally for 10% precision .1 should be used, for energy
        # evaluations .2 is used.
        p = .2
        with PdfPages('E:\\Stats\\Plots\\Mean Sampling.pdf') as pdf:
            t_sample_range = list()
            z_sample_range = list()
            for N in population_range:
                t_sample_range.append(MeanSam.iterative_t_sample(
                                                            N, c, p, cv))
                z_sample_range.append(MeanSam.z_sample(c, p, cv))
            plt.step(population_range, t_sample_range,
                     label='t Sample, ' + r'$CV=$'+str(cv))
            plt.step(population_range, z_sample_range,
                     label='z Sample, ' + r'$CV=$'+str(cv))
            plt.title('Meter Sampling')
            plt.xlabel(r'Population Size')
            plt.ylabel(r'Sample Size')
            plt.legend()
            plt.xticks(np.arange(0, 201, 10))
            plt.yticks(np.arange(0, 25, 10))
            plt.minorticks_on()
            pdf.savefig()
            plt.close()
        df = pd.DataFrame()
        df['Population Size'] = population_range
        df['Sample Size'] = t_sample_range
        df.to_csv('E:\\Stats\\CSVs\\Mean Sampling.csv', index=False)


# A class with tools used to determine sample sizes when preforming inference
# on a population proportion.
class ProSam():

    # The text book method for determining a sample size for a specified error
    # on a binomial proportion
    @staticmethod
    def trad_sample(c, p, p_hat):
        '''inputs: confidence, precision, estimate of proportion.'''
        # Calculate test statistic assuming two tailed distribution.
        Z = stats.norm.ppf((1-c)/float(2))
        # Error is 1/2 the precision
        E = float(p) / 2
        n = (Z / E)**2 * p_hat*(1 - p_hat)
        return int(math.ceil(n))

    # A static method to calculate the binomial coefficient 'n' choose 'k', or
    # the number of ways 'n' can be choosen from 'k'.
    @staticmethod
    def nCk(n, k):
        ''' inputs: population size, sample size '''
        f = math.factorial
        return float(f(n) / (f(n - k) * f(k)))

    # A static method to calculate the probability of 'n' successes in 'N'
    # given probability 'p' of success and assuming a binomial distribution.
    @staticmethod
    def binomial(N, n, p):
        ''' inputs: sample size, sample successes, probability of success '''
        return ProSam.nCk(N, n) * p**n * (1 - p)**(N - n)

    # A static method to calcualte the probability of 'i' successes given 'n'
    # ways for a good selection, 'm' ways for a bad selection and 'N' samples
    # without replacement.
    @staticmethod
    def hypergeometric(n, m, N, i):
        ''' inputs: ways for a good selection, ways for a bad selection,
            samples, successful selections '''
        return float(
            ProSam.nCk(n, i) * ProSam.nCk(m, (N - i)) / ProSam.nCk((m + n), N))

    # A static method to iteratively determing the sample size for a population
    # proportion with a true proportion expected to be close to 1.
    @staticmethod
    def sample(c, p, P, e, D):
        ''' inputs: confidence, precision, population size,
            estimate of proportion, distribution ('h' for hypergeometric and
            'b' for binomial) '''
        # Re-assign the user inputted prcision to distinguish from the current
        # precision inside of the while loop. Use 'p_des' as the label for the
        # desired precision and 'p_cur' for the current precision, which is
        # instantiated as 1.
        p_des = float(p)
        p_cur = 1.0
        # 'N' is the sample size the yeilds the desired precision and is
        # incremented inside of the while loop. Once 'p_des' is achieved 'N'
        # is returned. Initially a value of 1 is used because it is the
        # smallest possible sample size.
        N = 1.0
        P = float(P)
        while p_cur > p_des:
            # For each sample size 'N' the hypergeometric probability of 'i'
            # successes given 'n' ways for a good selection, 'm' ways for a bad
            # selection and 'N' samples needs to be calculated. By plotting
            # this probability for a range of 'n' values a distribution is
            # created that can be normalized and integrated to find the bounds
            # of the desired confidence.
            # The number of successes 'i' is unknown but given the sample size
            # 'N' and that it's expected to be close to 1 the user can input
            # the their estimate of the proportion using the argument 'e'.
            i = float(floor(N * e))
            # There are bounds on the domain of 'n', specifically 'n' cannot be
            # smaller than i (can't have more successes than ways for sucessful
            # selections) and cannot be larger than 'P' minus 'N' plus 'i' (
            # can't have more ways for successful selection than the population
            # minus the number of uncessful selections from the sample)
            # To generate the distribution iterate from 'n' = 'i' to
            # 'n' = 'P' - ('N' - 'i'), store 'n' values and corresponding
            # probabilities in 'x' and 'y'.
            x = list()
            y = list()
            n = float(i)
            n_max = float(P - (N - i))
            while n <= n_max:
                # Generate the distribution inputted by the user, 'h' for
                # hypergeometric and 'b' for binomial. Both distributions use
                # the number of ways for uncessful selections 'm'
                m = float(P - n)
                if D == 'h':
                    x.append(n)
                    y.append(ProSam.hypergeometric(n, m, N, i))
                elif D == 'b':
                    x.append(n)
                    y.append(ProSam.binomial(N, i, float(n) / float(n + m)))
                else:
                    print 'Input either "h" or "b".'
                    return N
                n += 1
            n -= 1
            # Once a distribution has been created a we can find the values
            # that bound the desired confidence by taking the center value
            # (not actually the center because the distributino isn't always
            # going to be symmetric just the most probable value) and
            # incrementing the bounds by j and finding the area between them.
            peak = x[y.index(max(y))]
            area = float()
            j = int()
            # 'j' can't be incremented by 1 because the maximum bounds of the
            # distribution are 0 and 1. Since both hypergeometric and binomial
            # distributions are discrete the increment will be a function of
            # the distribution.
            del_j = x[1] - x[0]
            # 'c' is the confidence desired by the user.
            while area < c:
                lower_bound = peak - j
                upper_bound = peak + j
                # There are maximum values on the lower and upper bounds, which
                # are the same as the bo bounds on the distribution. If either
                # bound is incremented beyond the bounds of the distribution
                # the are individually re-assigined.
                if upper_bound > n_max:
                    upper_bound = n_max
                if lower_bound < i:
                    lower_bound = i
                area = (float(
                        sum(y[x.index(lower_bound) + 1:x.index(
                            upper_bound) + 1])) / float(sum(y[1:])))
                j += del_j
            # After establishing the values that bound the desired area are
            # equal to the desired confidence the current precision can be
            # calculated.
            # The precision of a proportion is equal to the lower bound
            # subtracted from the upper bound and for the bounds to be less
            # than 1 they need to be divided by the populaiton size.
            p_cur = float(upper_bound - lower_bound) / float(P)
            # Because the distribution is discrete it's possible that bounds
            # bounding the drsired area can't be established, this will occur
            # when the inputted population 'P' is small. To avoide an infinite
            # loop the conditions below are used.
            if (upper_bound == n_max) and (lower_bound == i):
                print 'Maximum lower and upper bounds reached.'
                # For degubbing purposes it can be useful to return
                # the variables: x, y, N, lower_bound, upper_bound
                return P
            N += 1
        # Exiting the outer while loop above the precision calculated will
        # correspond to a value of N that is then incremented before the next
        # check of p_curr > p_des, this means the actual N the returns the
        # desired confidence is N-1
        N -= 1
        # Exiting the outer while loop above ploting 'x' and 'y' will display
        # the distribution which will not be a pdf until it's normalized.
        # It's not always necessary to plot the distribution.
#        x_norm = np.array(x)/float(P)
#        del_x = np.gradient(x_norm)[0]
#        y_norm = np.array(y) / (sum(y)*del_x)
#        lb_norm = lower_bound / float(P)
#        ub_norm = upper_bound / float(P)
#        plt.step(x_norm, y_norm)
#        plt.vlines(lb_norm, 0, y_norm[np.where(x_norm==lb_norm)])
#        plt.vlines(ub_norm, 0, y_norm[np.where(x_norm==ub_norm)])
        # For degubbing purposes it can be useful to return the variables:
        # x_norm, y_norm, N, lb_norm, ub_nom
#        return n, m, N, i, area, p_cur
        return N

    # A method to randomly select without replacement 'N' numbers
    # less than 'P'.
    @staticmethod
    def random_sample(P, N):
        ''' inputs: population size, sample size '''
        items = []
        # populate until determined sample size is reached
        while len(items) < N:
            rv = int(math.ceil(random.random() * P))
            # only append values not in sample (without replacement)
            if items.count(rv) == 0:
                items.append(rv)
        items.sort()
        return items

    # A method to plot sample sizes vs population sizes given a range of
    # assumptions.
    @staticmethod
    def plot_proportion_samples():
        matplotlib.style.use('ggplot')
        sample_range = []
        population_range = np.arange(2, 201, 1)
        # Function doesn't actually vary with the estimate of the
        # true proportion.
        e = .95
        c = .9
        # According the Uniform Methods Project 10% precision implies +\-.1,
        # this interpretation is different than that presented in statistics
        # textbooks, that precision is the length of the confidence interval.
        # While normally for 10% precision .1 should be used, for energy
        # evaluations .2 is used.
        p = .2
        with PdfPages('E:\\Stats\\Plots\\Proportion Sampling.pdf') as pdf:
            sample_range = list()
            for P in population_range:
                curr = ProSam.sample(c, p, P, .95, 'h')
                # adjust curr to be at least as large as the prevoius element
                if (len(sample_range) > 0) and (curr < sample_range[-1]):
                    curr = sample_range[-1]
                sample_range.append(curr)
            plt.step(population_range, sample_range, color='k',
                     label=r'Estimate of Proportion=' + str(e))
            plt.title('Verification Sampling')
            plt.xlabel(r'Population Size')
            plt.ylabel(r'Sample Size')
            plt.legend()
            plt.xticks(np.arange(0, 201, 1))
            plt.yticks(np.arange(0, 20, 1))
            plt.minorticks_on()
            pdf.savefig()
        df = pd.DataFrame()
        df['Population Size'] = population_range
        df['Sample Size'] = sample_range
        df.to_csv('E:\\Stats\\CSVs\\Proportion Sampling.csv', index=False)

    # TODO: Test hypergeometric sampling method against known methods for
    # producing condifence intervals for binomial proportions with zero
    # frequency. See verify.py (in same directory).
    def wald():
        pass

    @staticmethod
    def agresti_coull(c, p, e):
        Z = abs(stats.norm.ppf((1 - c) / float(2)))
        p_curr = 1
        n = 1
        while p_curr > p:
            n1 = floor(n * e)
            n1_t = n1 + Z / 2
            n_t = n + Z**2
            p_t = n1_t / float(n_t)
            lb = p_t - Z * ((p_t * (1 - p_t)) / float(n))**.5
            ub = p_t + Z * ((p_t * (1 - p_t)) / float(n))**.5
            p_curr = ub - lb
            n += 1
        n -= 1
        return n

    def jefferys():
        pass

    def clopper_pearson():
        pass

    def wilson():
        pass
