""" This script calculates the entropy of fingervein patterns based on Hamming distance distributions between unrelated feature vectors """

import bob.measure
import numpy
import scipy
import scipy.stats
from matplotlib import pyplot as plt
plt.switch_backend('pdf')  # switch to non-X backend
from matplotlib.backends.backend_pdf import PdfPages
import argparse


def calc_stats(HDs, db, extractor):
	""" Calculates the mean, standard deviation, degrees of freedom, and entropy for the input Hamming Distances (HDs).

	**Parameters:** 

	HDs (list): A list of Hamming distances between the fingervein patterns of every pair of different fingers
	db (str): Name of the fingervein database for which we wish to calculate the statistics
	extractor (str): The feature extractor used to extract the fingervein patterns on which the input HDs have been calculated

	**Returns:**

	p (float): The mean of the HD distribution and the fitted binomial distribution
	sigma (float): The standard deviation of the HD distribution and the fitted binomial distribution
	N (float): The number of degrees of freedom (approx. number of independent bits in the underlying fingervein feature vectors) for the fitted binomial distribution 
	H (float): The estimated entropy per independent bit for the underlying fingervein feature vectors
	H_T (float): The estimated total entropy across all independent bits in the underlying fingervein feature vectors
	statistics.txt (textfile): Contains the calculated statistics

	"""

	# Calculate the various statistics:
	p = numpy.mean(HDs)
	sigma = numpy.std(HDs)
	N = (p * (1 - p)) / (sigma ** 2)
	H = -p*scipy.log2(p) - (1 - p)*scipy.log2(1 - p)
	H_T = H * N

	# Write the statistics to a textfile:
	filename = 'results/' + db + '/' + extractor + '/statistics.txt'
	f = open(filename, "w")
	f.write("Results from Table 2, for the %s extractor on the %s database:\n\n" % (extractor.upper(), db.upper()))
	f.write("p = %.2f\n" % (p))
	sigma_str = u'\N{GREEK SMALL LETTER SIGMA}'
	f.write("%s = %.3f\n" % (sigma_str.encode('utf-8'), sigma))
	f.write("N = %s\n" % (int(round(N))))
	f.write("H = %.2f\n" % (H))
	f.write("H_T = %s" % (int(round(H_T))))
	f.close()

	return p, sigma, N, H, H_T


def plot_distributions(HDs, db, extractor, p, sigma, N):
	""" Plots the histogram of the input Hamming Distances (HDs) and fits a binomial to the distribution.

	**Parameters:** 

	HDs (list): A list of Hamming distances between the fingervein patterns of every pair of different fingers
	db (str): Name of the fingervein database for which we wish to calculate the statistics
	extractor (str): The feature extractor used to extract the fingervein patterns on which the input HDs have been calculated
	p (float): The mean of the HD distribution and the fitted binomial distribution
	sigma (float): The standard deviation of the HD distribution and the fitted binomial distribution
	N (float): The number of degrees of freedom (approx. number of independent bits in the underlying fingervein feature vectors) for the fitted binomial distribution 

	**Returns:**

	HD_distribution.pdf (saved image): Plot of the HD distribution with the corresponding binomial distribution overlaid

	"""

	# Calculate the histogram of the Hamming distance (HD) distribution:
	fig = plt.figure()
	plt.xlim([0, 1])
	plt.xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
	plt.title('%s Extractor on %s Database' % (extractor.upper(), db.upper()))
	plt.xlabel('HD')
	plt.ylabel('Probability')
	counts, bin_edges = numpy.histogram(HDs, bins=numpy.arange(0.000, 1.001, 0.001))  # bin the HD values
	bin_probs = counts/float(len(HDs))  # normalise the bin counts so that every bin value gives the probability of that bin
	bin_middles = (bin_edges[1:]+bin_edges[:-1])/float(2)  # get the mid point of each bin
	bin_width = bin_edges[1]-bin_edges[0]  # compute the bin width
	# Calculate the binomial distribution corresponding to the HD histogram, and plot the HD histogram overlaid with the binomial distribution:
	N = int(round(N))  # degrees of freedom for the binomial distribution = degrees of freedom of HD distribution
	x_temp = range(0, N+1)
	x = [i/float(N) for i in x_temp] # fractional Hamming distances from 1/N to N/N (liken to probability of getting H = x * N heads from N coin tosses)
	plt.plot(x, scipy.stats.binom.pmf(x_temp, N, p), '-k')
	plt.ylim([0.0, 0.10])
	plt.yticks([0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10])
	# Normalize the histogram so it is easier to visualise the binomial distribution fit:
	norm_scale = max(scipy.stats.binom.pmf(x_temp, N, p))/max(bin_probs)
	normed_bin_probs = bin_probs * norm_scale
	plt.bar(bin_middles, normed_bin_probs, width=bin_width, color='lightgrey')
	# Save the figure:
	fig_path = 'results/' + db + '/' + extractor + '/HD_distribution.pdf'
	pdf = PdfPages(fig_path)
	fig.savefig(fig_path, format='pdf', bbox_inches='tight')
	plt.close()


def main():
	""" Calculates the entropy of fingervein patterns.

	This function calculates the mean, standard deviation, degrees of freedom, and entropy for the Hamming Distances (HDs) between fingervein feature vectors of different fingers.  
	It also plots the histogram of the HDs and fits a binomial to the distribution.

	**Parameters (from the command line):** 

	database (str): Name of the fingervein database for which we wish to calculate the entropy
	extractor (str): The feature extractor used to extract the fingervein patterns 

	**Returns:**

	statistics.txt (textfile): Contains the calculated statistics
	HD_distribution.pdf (saved image): Plot of the HD distribution with the corresponding binomial distribution overlaid

	"""

	# Parse the command line arguments:
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--database', required=True, choices = ('vera', 'utfvp'), help = "The fingervein database name.")
	parser.add_argument('-e', '--extractor', required=True, choices = ('wld', 'rlt', 'mc'), help = "The fingervein feature extractor.")
	args = parser.parse_args()
	# Extract the previously-generated HDs for the specified database and feature extractor:
	if args.database == 'vera':
		scores_path = 'results/' + args.database + '/' + args.extractor + '/Full/nonorm/scores-dev'
	elif args.database == 'utfvp':
		scores_path = 'results/' + args.database + '/' + args.extractor + '/full/nonorm/scores-dev'
	scores = bob.measure.load.split(scores_path)
	HDs = scores[0]
	print '================================================================='
	print 'Database: %s, Extractor: %s' % (args.database.upper(), args.extractor.upper())
	print 'Total number of scores used in entropy estimation = %s' % (len(HDs))
	# Calculate the mean, standard deviation, degrees of freedom, and entropy for the HDs:
	print 'Calculating statistics ...'
	[p, sigma, N, H, H_T] = calc_stats(HDs, args.database, args.extractor)
	# Plot the histogram of the HDs and fit a binomial to the distribution:
	print 'Plotting distributions ...'
	plot_distributions(HDs, args.database, args.extractor, p, sigma, N)
	print '================================================================='