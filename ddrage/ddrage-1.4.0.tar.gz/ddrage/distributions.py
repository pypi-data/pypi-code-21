# -*- coding: utf-8 -*-
"""Module for tailored probability distributions.

Each of these is used for a specific task like:
  - Read coverage at locus.
  - Selection of locus event.

The distributions used for coverage distribution should follow the CoverageGenerator
pattern to be easily replacable.
"""
import math
import sys
import numpy as np

from scipy.special import beta
from scipy.misc import comb


DEFAULT_EVENT_PROBABILITIES = {
    "common": 0.90,
    "dropout": 0.05,
    "mutation": 0.05,
    }

DEBUG_EVENT_PROBABILITIES = {
    "common": 1/3,
    "dropout": 1/3,
    "mutation": 1/3,
    }

# DEFAULT_MUTATION_TYPE_PROBABILITIES = {
#     "snp": 0.8999,
#     "insert": 0.05,
#     "deletion": 0.05,
#     "na": 0.0001,
#     }

DEFAULT_MUTATION_TYPE_PROBABILITIES = {
    "snp": 0.8999,
    "insert": 0.05,
    "deletion": 0.05,
    "p5 na alternative": 0.0001 * 0.001,
    "p7 na alternative": 0.0001 * 0.05,
    "p5 na dropout": 0.0001 * 0.899,
    "p7 na dropout": 0.0001 * 0.05,
    }

# DEBUG_MUTATION_TYPE_PROBABILITIES = {
#     "snp": 1/4,
#     "insert": 1/4,
#     "deletion": 1/4,
#     "na": 1/4,
#     }

DEBUG_MUTATION_TYPE_PROBABILITIES = {
    "snp": 1/7,
    "insert": 1/7,
    "deletion": 1/7,
    "p5 na alternative": 1/7,
    "p7 na alternative": 1/7,
    "p5 na dropout": 1/7,
    "p7 na dropout": 1/7,
    }

# these are set by the initialize_coverage_generators(...) function
normal_coverage_generator = None
hrl_coverage_generator = None
indel_length_generator = None


class CoverageGenerator:
    """This could be an abstract base class (abc)

    All quality generators should implement the following to be easily interchangeable:

        - A `mean method`, returning the mean of the distribution as double.
        - A `variace method`, returning the variance of the distribution as double.
        - A `get method`, returning a value chosen from the distribution as integer.
        - A `get_multiple` method, which takes an integer `n` as input and returns
            `n` values from the distribution as a numpy array of integers.
    """
    def mean(self):
        raise NotImplementedError
    
    def variance(self):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def get_multiple(self):
        raise NotImplementedError


class BetaBinomial(CoverageGenerator):
    """Generator for Beta Binomial (BBD) distributed values.

    To use: create a new generator. The get and get_multiple functions
    return values. The probability mass function is stored in the probs argument.
    """
    def __init__(self, ds, a, b):
        """Create a new BBD generator.

        Arguments:
            ds (int): Target sequencing depth.
            a (double): α parameter for the BBD distribution. Regulates the
                left skew of the function. The bigger (in relation to β) the
                steeper the left tailing.
            b (double): β parameter for the BBD distribution. Regulates the
                right skew of the function. The bigger (in relation to α) the
                steeper the right tailing.

        Note:
            A reasonable range for coverage values seems to be around 
            α ≈ 6, β ≈ 2 to get a sharp dropoff above dₛ and a long 
            tail on the left.

        Raises:
            ValueError: If the value for α is too low. Too low means that n will
            be set to a value more than 5 times bigger than ds.
            This would leave a high probability on low coverage values, skewing the simulation.
        """
        # save parameters for later computations
        self.ds = ds
        self.a = a
        self.b = b
        # compute the n parameter, depending on alpha and beta, in order to move
        # the mean of the BBD to the expected sequencing depth dₛ.
        # Set dₛ = E(BDD(α, β, n)) and solve for n, then
        # it has to be round down, as n is an integer parameter (nr of trials).
        self.n = math.floor((ds * (a + b)) / a)
        if self.n > 5*ds:
            raise ValueError("Value for --BBD-alpha ({}) is too low or --BBD-beta ({}) too big. Please pick a different set of values.".format(a, b))
        # compute probability mass function
        # saved as an array, where probs[i] = P(BBD(x = k | n, a, b))
        self.probs = np.array([self._binom_beta(k, self.n, a, b) for k in range(self.n+1)])
        # compute values corresponding to the pmf entries
        self.values = np.arange(0, self.n+1)

    def _binom_beta(self, k, n, a, b):
        """Compute one probability of the BBD distribution.

        Arguments:
            k (int): index for which the probability will be computed.
                P(BBD(x = k | n, a, b))
            n (int): Number of values (see constructor).
            a (double): α parameter for BBD (see constructor).
            b (double): β parameter for BBD (see constructor).

        Returns:
            double: Probabilizy of choosing k from BBD(n,a,b).
        """
        return comb(n,k) * beta(k+a, n-k+b) / beta(a,b)

    def mean(self):
        """Mean of the BBD distribution with the given parameters as double."""
        return (self.n * self.a) / (self.a + self.b)

    def variance(self):
        """Variance of the BBD distribution with the given parameters as double."""
        return self.n*self.a*self.b*(self.a+self.b+self.n) / ((self.a+self.b)*(self.a+self.b)*(self.a+self.b+1))

    def mu_2sigma(self):
        """Mean + 2 std deviations as double."""
        sigma = math.sqrt(self.variance())
        return self.mean() + 2 * sigma

    def get(self):
        """Get a BBD distributed random variable.

        Returns:
            int: Coverage value following a BBD distribution.
        """
        result = np.random.choice(self.values, p=self.probs)
        return max(result, 2)

    def get_multiple(self, n):
        """Get a BBD distributed random variable.

        Arguments:
            n (int or tuple): Size of the returned array. As this is forwarded
                to np.random.choice the format descried there can be used.

        Returns:
            np.array(int): Coverage values following a BBD distribution.
        """
        return np.random.choice(self.values, p=self.probs, size=n)


class PoissonCentered(CoverageGenerator):
    """Generator for coverage values following a Poisson Distribution (PD)."""

    def __init__(self, target_depth, min_cov=None, max_cov=None):
        """Create a new generator.

        Note:
            The expected coverage is modified by a poisson distribution as follows::
    
                result = expected_coverage - (PD(lambda_p) - mean(PD(lambda_p)))
                if result < min_cov:
                    return min_cov
                if result > max_cov:
                    return max_cov
                return result

            This centeres the mean of the resulting distribution on the expected value.
    
            The check against max_cov is not strictly necessary for this, but
            has been added to prevent results leaving the bounderies if other
            distributions are used.

        Arguments:
            expected_coverage (int): Expected number of reads.
            min_cov (int): Minimum result. If ``None``, a sensible value like 2 is assumed.
            max_cov (int): Maximum result. If ``None``, no truncation will take place.
        """
        self.target_depth = target_depth
        self._lambda(target_depth)
        if not min_cov:
            self.min_cov = 2
        else:
            self.min_cov = min_cov
        self.max_cov = max_cov # the none default parameter is handled in the get function

    def _lambda(self, target_depth):
        """Compute the lambda value for the given target depth.

        The lambda parameter for the distribution is calculated as::
        
            lambda_p = 2.0 if exp_cov <= 10 else exp_cov / 2.0
        
        This guarantees reasonable coverages for low coverage situations and
        also provides a lot of scatter for larger coverages.

        Arguments: 
            target_depth (int): Target sequenceing depth for which
                coverages will be simulated.

        Returns:
            None: Sets the lambda_p parameter.
        """
        if target_depth <= 10:
            self.lambda_p = 2 * (1 - (target_depth / 10)) + (target_depth) # for a smoother transition between the low and higher lambda values
        else:
            self.lambda_p = target_depth

    def mean(self):
        """Mean of the PD as double."""
        return self.lambda_p

    def variance(self):
        """Variance of the PD as double."""
        return self.lambda_p

    def mu_2sigma(self):
        """Mean + 2 std deviations as double."""
        sigma = math.sqrt(self.variance())
        return self.mean() + 2 * sigma

    def get(self):
        """Get a coverage value following a PD.

        Returns:
            int: Coverage value, that is at least min_cov, at most max_cov and
            follows a PD.
        """
        # Move the mode of the poisson distribution (which is lambda)
        # to the expected coverage. Values below E(PD(lambda)) = lambda 
        # will be subtracted from d_s, values above will be added.
        cov = self.target_depth - (np.random.poisson(self.lambda_p) - int(self.mean()))

        # Make sure the bounds are respected.
        if cov < self.min_cov:
            return self.min_cov
        elif self.max_cov and (cov > self.max_cov):
            return self.max_cov
        else:
            return cov

    def get_multiple(self, n):
        """Get multiple coverage values following a PD.

        Arguments:
            n (int or tuple): Size of the returned array. As this is forwarded
                to np.random.choice the format descried there can be used.

        Returns:
            np.array(int): Coverage values following a PD.
        """
        return np.array([self.get() for _ in range(n)])


class DiscreteUniform(CoverageGenerator):
    """Generator for coverage values following a Discrete Uniform Distribution (DUD)."""

    def __init__(self, min_cov, max_cov):
        """Create a new generator.

        Arguments:
            expected_coverage (int): Expected number of reads.
            min_cov (int): Minimum result. This should be > mu + 2 sigma of the main coverage generator
            max_cov (int): Maximum result.
        """
        self.min_cov = min_cov
        self.max_cov = max_cov

    @classmethod
    def from_coverage_generator(cls, cov_gen, max_cov=2000):
        """Create a discrete uniform coverage generator creating values
        that are at least μ + 2σ of the provided generator.
        """
        min_cov = cov_gen.mu_2sigma()
        return cls(min_cov=min_cov, max_cov=max_cov)

    def mean(self):
        """Mean of the DUD as double."""
        return (self.min_cov + self.max_cov) / 2

    def variance(self):
        """Variance of the DUD as double."""
        return (math.pow((self.max_cov - self.min_cov + 1), 2) - 1) / 12

    def get(self):
        """Get a coverage value following a DUD.

        Returns:
            int: Coverage value, that is at least min_cov, at most max_cov and
            follows a DUD.
        """
        return np.random.randint(self.min_cov, self.max_cov)

    def get_multiple(self, n):
        """Get multiple coverage values following a DUD.

        Arguments:
            n (int or tuple): Size of the returned array. As this is forwarded
                to np.random.randint the format descried there can be used.

        Returns:
            np.array(int): Coverage values following a DUD.
        """
        return np.random.randint(self.min_cov, self.max_cov, size=n)


class IndelLengthGenerator:
    """Generator for indel lengths. Yields 1 or multiples of three."""

    def __init__(self):
        """Initialize generator with a static probability distribution of indel lengths."""
        # counts from nature paper
        coding_del_length_counts = np.array([957, 457, 827, 179, 66, 94, 20, 15, 63, 23, 12, 42, 10, 8, 27, 9, 10, 15, 5, 6, 17, 1, 2, 6, 2, 2, 9, 1, 1, 2, 0, 1, 0, 0, 2, 2, 0, 0, 1, 0, 0, 0, 0, 0, 1])
        coding_ins_length_counts = np.array([585, 82, 186, 71, 24, 56, 10, 14, 17, 9, 1, 19, 1, 3, 5, 4, 0, 7, 1, 1, 5, 2, 1, 1, 0, 0, 1])
        noncoding_del_length_counts = np.array([377799, 164392, 108921, 126992, 45513, 21662, 10974, 10515, 7986, 7453, 5955, 5555, 4218, 3753, 2909, 2753, 2067, 1870, 1607, 1354, 1180, 1121, 900, 913, 770, 685, 537, 481, 364, 358, 304, 285, 211, 221, 155, 161, 150, 146, 105, 93, 88, 89, 79, 93, 63, 38, 54, 47, 37, 45, 39, 29, 31, 32, 18, 29, 24, 16, 14, 13, 15, 5, 6, 14, 8, 6, 4, 1, 1])
        noncoding_ins_length_counts = np.array([308509, 67728, 33532, 44823, 15662, 9074, 5101, 6906, 3610, 2845, 1785, 2324, 1249, 1265, 1114, 1319, 880, 871, 684, 856, 523, 467, 365, 490, 275, 217, 153, 156, 69, 94, 61, 55, 37, 33, 30, 26, 19, 12, 12, 6, 4, 4])
        # compute relative abundance
        self.coding_del_probs = coding_del_length_counts / np.sum(coding_del_length_counts)
        self.coding_ins_probs = coding_ins_length_counts / np.sum(coding_ins_length_counts)
        self.noncoding_del_probs = noncoding_del_length_counts / np.sum(noncoding_del_length_counts)
        self.noncoding_ins_probs = noncoding_ins_length_counts / np.sum(noncoding_ins_length_counts)
        # assemble arrays to choose from
        self.coding_ins_lengths = np.arange(1, len(self.coding_ins_probs)+1)
        self.coding_del_lengths = np.arange(1, len(self.coding_del_probs)+1)
        self.noncoding_ins_lengths = np.arange(1, len(self.noncoding_ins_probs)+1)
        self.noncoding_del_lengths = np.arange(1, len(self.noncoding_del_probs)+1)
        # relative size of codinf vs noncoding
        self.prob_ins_coding = np.sum(coding_ins_length_counts) / (np.sum(coding_ins_length_counts) + np.sum(noncoding_ins_length_counts))
        self.prob_del_coding = np.sum(coding_del_length_counts) / (np.sum(coding_del_length_counts) + np.sum(noncoding_del_length_counts))
    
    def get_insert_length(self):
        """Pick an insertion length."""
        if np.random.random() <= self.prob_ins_coding:
            return np.random.choice(self.coding_ins_lengths, p=self.coding_ins_probs)
        else:
            return np.random.choice(self.noncoding_ins_lengths, p=self.noncoding_ins_probs)

    def get_deletion_length(self):
        """Pick a deletion length."""
        if np.random.random() <= self.prob_del_coding:
            return np.random.choice(self.coding_del_lengths, p=self.coding_del_probs)
        else:
            return np.random.choice(self.noncoding_del_lengths, p=self.noncoding_del_probs)

    def longest_possible_deletion(self):
        return max(len(self.coding_del_lengths), len(self.noncoding_del_lengths))


def initialize_coverage_generators(args):
    """Pick and initialize a coverage generator object.

    Arguments:
        args (argparse.Namespace): Containing coverage and all
            necessary parameters for the specified distribution.

    Returns:
        None: Sets the normal_coverage_generator and hrl_coverage_generator
        varibales.

    Raises:
        ValueError: If an invalid distribution name is passed.

    This problem arises, when alpha is picked to be small (<= 0.1).
    This will result in a high probability for very low coverage values.
    """
    global normal_coverage_generator
    global hrl_coverage_generator
    global indel_length_generator

    indel_length_generator = IndelLengthGenerator()
    # this might be better solved by a dictionary
    if args.coverage_model.lower() in ("poisson", "pd"):
        normal_coverage_generator = PoissonCentered(args.cov)
        hrl_coverage_generator = DiscreteUniform(normal_coverage_generator.mu_2sigma(), args.hrl_max_cov)
        args.coverage_model = "Poisson"
    elif args.coverage_model.lower() in ("betabinomial", "beb", "bbd"):
        normal_coverage_generator = BetaBinomial(args.cov, args.bbd_alpha, args.bbd_beta)
        hrl_coverage_generator = DiscreteUniform(normal_coverage_generator.mu_2sigma(), args.hrl_max_cov)
        args.coverage_model = "BetaBinomial"
    else:
        raise ValueError("Invalid distribution {}. Should be 'poisson', 'pd', 'betabinomial', or 'bbd'.")


def is_equation(t):
    """Check if a text is an equation and only consists of math characters.
    """
    for c in t:
        if c not in "01234567890.+-/*%() ":
            return False
    return True


def interpret_probabilities(probs, prob_type="event_types"):
    """Translate a probability profile as text to a dict that can be used by distributed_events.

    This should be used for debugging purposes only.

    Arguments:
        probs: String or iterable of floats (three or four, depending on prob_type)
            that sum up to 1.0
        prob_type (str): The events the probabilities are associated with.
            Can be either 'event_types' for individuals locus event types (common, mutation,
            dropout) or 'mutation_types' for the relative probabilities of different kinds
            of mutations (snp, insert, deletion, na)

    Returns:
        dict: Mapping events ("common", "dropout", "mutation") or ("snp", "insert",
        "deletion", "na") to probabilities. The probabilities are guaranteed to
        sum up to 1.0
    """
    # determine the type of probabilities to interpret.
    # evets types or mutation types
    if prob_type == "event_types":
        events = ("common", "dropout", "mutation")
    elif prob_type == "mutation_types":
        events = ("snp", "insert", "deletion", "p5 na alternative", "p7 na alternative", "p5 na dropout", "p7 na dropout")
    # handle strings and iterables
    if isinstance(probs, str):
        event_probs = {}
        for event, prob in zip(events, probs.split(" ")):
            try:
                e_prob = float(prob)
            except ValueError:
                if is_equation(prob):
                    e_prob = float(eval(prob))
                else:
                    raise ValueError("Could not parse equation '{}'".format(prob))
            event_probs[event] = e_prob
    else:
        event_probs = {}
        for event, prob in zip(events, probs):
            try:
                e_prob = float(prob)
            except ValueError:
                if is_equation(prob):
                    e_prob = float(eval(prob))
                else:
                    raise ValueError("Could not parse equation '{}'".format(prob))
            event_probs[event] = e_prob
    # assert that the given probability vector
    # sums up to 1, compensating for floating point 
    # rounding errors
    if np.isclose(sum(event_probs.values()), 1.0):
        return event_probs
    else:
        # compile error message
        summands = event_probs.values()
        sum_as_text = " + ".join([str(p) for p in summands])
        raise ValueError("The {} probabilities {} = {} do not add up to 1.0".format(prob_type, sum_as_text, sum(summands)))


def validate_probability_parameters(args):
    """If probability vectors were given as a parameter, i.e. a list of probabilities for
    locus event types or mutation types, make sure they sum up to one and are dicts.

    Arguments:
        args (Argparse namespace): User parameters from argpgarse.

    Returns:
        None: The value is changed in place.
    """
    # determine which event probability types are to be used.
    # they can be user-defined (and need to be interpreted),
    # default values (see top of the file for the constant values),
    # or debug values, which make all events visible
    if args.event_prob_profile is not None:
        args.event_prob_profile = interpret_probabilities(args.event_prob_profile, prob_type="event_types")
    elif args.debug_run:
        args.event_prob_profile = DEBUG_EVENT_PROBABILITIES
    else:
        args.event_prob_profile = DEFAULT_EVENT_PROBABILITIES
    # determine which mutation probability types are to be used.
    # they can be user-defined (and need to be interpreted),
    # default values (see top of the file for the constant values),
    # or debug values, which make all events visible
    if args.mutation_type_prob_profile is not None:
        args.mutation_type_prob_profile = interpret_probabilities(args.mutation_type_prob_profile, prob_type="mutation_types")
    elif args.debug_run:
        args.mutation_type_prob_profile = DEBUG_MUTATION_TYPE_PROBABILITIES
    else:
        args.mutation_type_prob_profile = DEFAULT_MUTATION_TYPE_PROBABILITIES

    if args.diversity <= 0:
        raise ValueError("Please choose a diversity parameter >0.")


def distributed_events(n, event_probs):
    """Pick n events from dict according to probability of occurence.

    Arguments:
        n (int): Number of events to pick.
        event_probs (dict): Mapping of event name as string to probability as float.

    Returns:
        list: Containing picked events as strings.
    """
    events, probabilities = zip(*event_probs.items())
    return np.random.choice(events, size=n, p=probabilities).tolist()


def distributed_mutation_type(mutation_probs, prohibited_mutations=None):
    """Pick an allele type from a dict according to probability of occurence.

    Arguments:
        mutation_probs (dict): Mapping of event name as string to probability as float.

    Returns:
        list: Containing picked events as strings.
    """
    mutations, probabilities = zip(*mutation_probs.items())
    if prohibited_mutations:
        chosen_mutation = np.random.choice(mutations, p=probabilities)
        while chosen_mutation in prohibited_mutations:
            chosen_mutation = np.random.choice(mutations, p=probabilities)
        return chosen_mutation
    else:
        return np.random.choice(mutations, p=probabilities)


def incomplete_digestion_coverage(coverage, rate):
    """Determine a low number of ID reads for a given coverage.

    Arguments:
        coverage (int): Total coverage to be distributed.

    Returns:
        tuple(int, int): Normal coverage and Null Allele coverage.
    """
    # Note: This is not handled by a coverage generator, as coverage
    # is distributed between two events (affected by ID and not affected by ID)
    cov_ID = np.random.binomial(coverage, rate)
    cov_normal = coverage - cov_ID
    return (cov_normal, cov_ID)


def heterozygous_mutation_distribution(coverage):
    """Distribute reads somewhat equally between alleles.

    Uses a binomial distribution with p = 0.5 and n = coverage

    Arguments:
        coverage (int): Total coverage to be distributed.

    Returns:
        tuple(int, int): Allele one coverage and Allele two coverage.
    """
    # make sure at least one read exists for each allele
    cov_allele_1 = np.random.binomial(coverage, 0.5)
    cov_allele_2 = coverage - cov_allele_1
    return (cov_allele_1, cov_allele_2)


def ztpd(l=1.0, size=None):
    """Return one or more poisson distributed integers >0.

    Arguments:
        l (double): Lambda parameter (> 0) for the poisson distribution. Default: 1.0
        size (int): Number of values to be generated. Returned as list
            or as a single int value (for size=None, Default).

    Returns:
        int or list: An integer value if size was None (or evaluated to
        False), or a list with size values.
        
    """
    if l <= 0:
        raise ValueError("Please choose a diversity parameter >0.")

    if not size:
        result = np.random.poisson(l)
        while (result == 0):
            result = np.random.poisson(l)
        return result
    else:
        # this is only defined if it is needed multiple times.
        def non_zero_poisson(l):
            result = np.random.poisson(l)
            while (result == 0):
                result = np.random.poisson(l)
            return result

        return [non_zero_poisson(l) for _ in range(size)]
