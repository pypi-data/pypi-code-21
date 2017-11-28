#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from __future__ import print_function

"""This script evaluates the given score files and computes the EER on the development set and HTER on the evaluation set."""

import bob.measure

import argparse
import numpy
import os

# matplotlib stuff
import matplotlib; matplotlib.use('pdf')  #avoids TkInter threaded start
from matplotlib import pyplot as mpl

import logging
logger = logging.getLogger("bob.paper.taslp_2017")


def command_line_arguments(command_line_parameters):
  """Parse the program options"""

  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-d', '--directory', required=True, nargs='+', help="Folder containing the score files of the development and evaluation sets.")
  parser.add_argument('-l', '--legends', nargs='+', help="A list of legend strings used for ROC, CMC and DET plots; if given, must be the same number than --directory.")
  parser.add_argument('-list', '--list', default='false', choices=['false', 'true'], help="Show list of misclassified files if set to true")
  parser.add_argument('-i', '--invert', default='false', choices=['false', 'true'], help="Set to True when scores are inverted, i.e., attacks are positives and real negatives. False by default.")

  # parse arguments
  args = parser.parse_args(command_line_parameters)

  # update legends when they are not specified on command line
  if args.legends is None:
    args.legends = [f.replace('_', '-') for f in args.directory]
    logger.warn("Legends are not specified; using legends estimated from --dev-files: %s", args.legends)

  return args


def load_scores(filename):
  scores = []
  # read four columns file line by line
  for (client_id, _, label, score) in bob.measure.load.four_column(filename):
    #if (remove_free and 'free' in label):
    #  continue
    scores.append(score)

  return numpy.array(scores, numpy.float64)


def main(command_line_parameters=None):
  """Reads score files, computes error measures and plots curves."""

  args = command_line_arguments(command_line_parameters)

  # First, read the score files
  logger.info("Loading %d score files of the development set", len(args.directory))
  dev_real = [load_scores(os.path.join(f, "scores-dev-real")) for f in args.directory]
  dev_attack = [load_scores(os.path.join(f, "scores-dev-attack")) for f in args.directory]
  eval_attack = [load_scores(os.path.join(f, "scores-eval-attack")) for f in args.directory]
  eval_real = [load_scores(os.path.join(f, "scores-eval-real")) for f in args.directory]

  # remove nan from score files
  for i in range(len(dev_attack)):
    dev_attack[i] = dev_attack[i][~numpy.isnan(dev_attack[i])]
  for i in range(len(dev_real)):
    dev_real[i] = dev_real[i][~numpy.isnan(dev_real[i])]
  for i in range(len(eval_attack)):
    eval_attack[i] = eval_attack[i][~numpy.isnan(eval_attack[i])]
  for i in range(len(eval_real)):
    eval_real[i] = eval_real[i][~numpy.isnan(eval_real[i])]

  # inverse sign of scores if needed
  if (args.invert == "true"):
    dev_real = [-f for f in dev_real]
    dev_attack = [-f for f in dev_attack]
    eval_real = [-f for f in eval_real]
    eval_attack = [-f for f in eval_attack]

  for i in range(len(args.directory)):
    threshold = bob.measure.eer_threshold(dev_attack[i], dev_real[i])
    print(threshold)
    # apply threshold to development set
    far, frr = bob.measure.farfrr(dev_attack[i], dev_real[i], threshold)
    print("The EER of the development set of '%s' is %2.3f%%" % (args.legends[i], (far + frr) * 50.))  # / 2 * 100%

    # apply threshold to evaluation set
    far, frr = bob.measure.farfrr(eval_attack[i], eval_real[i], threshold)
    print("The HTER of the evaluation set of '%s' is %2.3f%%" % (args.legends[i], (far + frr) * 50.))  # / 2 * 100%
    print("Number of wrongly classified attacks : " + str(len(numpy.argwhere(eval_attack[i] > threshold))) + " over " + str(len(eval_attack[i])))
    print("Number of wrongly classified real accesses : " + str(len(numpy.argwhere(eval_real[i] < threshold))) + " over " + str(len(eval_real[i])))

    # show list of misclassified samples
    if args.list == 'true':
      idx_real = numpy.argwhere(eval_real[i] < threshold)
      idx_attack = numpy.argwhere(eval_attack[i] > threshold)
      print("Wrongly classified attacks:")
      file_eval_attack = open(os.path.join(args.directory[0], "scores-eval-attack"))
      s = file_eval_attack.readlines()
      for idx in idx_attack:
        print(s[idx[0]])
      print("Wrongly classified real accesses:")
      file_eval_real = open(os.path.join(args.directory[0], "scores-eval-real"))
      s = file_eval_real.readlines()
      for idx in idx_real:
        print(s[idx[0]])
