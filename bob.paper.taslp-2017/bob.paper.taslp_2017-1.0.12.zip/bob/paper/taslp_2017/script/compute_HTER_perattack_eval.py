#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Compute the Equal Error Rate on the evaluation set of the ASVspoof database"""

import bob.measure

import sys
import os
import argparse
import logging
import os.path

import numpy
from bob.db.asvspoof.query import Database

# setup logging
logger = logging.getLogger("bob.paper.taslp_2017")


def read_attack_scores(objects, attack_file):
    positives = []
    names = []
    scores = []
    for (client_id, probe_id, filename, score) in bob.measure.load.four_column(attack_file):
        names.append(filename)
        scores.append(score)

    for obj in objects:
        if obj.is_real():
            raise ValueError('The object of the database should be an attack but it is real!')
        sample_name = str(obj.make_path())
        try:
          idx = names.index(sample_name)
          positives.append(scores[idx])
        except ValueError:
          pass

    return numpy.array(positives, numpy.float64)

def load_scores(filename):
  scores = []
    # read four column list line by line
  for (client_id, _, _, score) in bob.measure.load.four_column(filename):
    scores.append(score)

  return numpy.array(scores, numpy.float64)



def main(command_line_parameters=None):

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  OUTPUT_DIR = os.path.join(basedir, 'plots')

  parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter, conflict_handler='resolve')
  parser.add_argument('-d', '--directory', required=True, help="The score file with real accesses scores of the evaluation set.")
  parser.add_argument('-i', '--invert', default='false',choices = ['false', 'true'], help = "Set to True when scores are inverted, i.e., attacks are positives and real negatives. False by default.")
  parser.add_argument('-o', '--output',  default=OUTPUT_DIR,
                        help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")



    # add verbose option
  bob.core.log.add_command_line_option(parser)
  args = parser.parse_args()
    # set verbosity level
  bob.core.log.set_verbosity_level(logger, args.verbose)

  if not os.path.exists(args.output):
    os.makedirs(args.output)

  # First, read the score files
  dev_real=load_scores(os.path.join(args.directory, "scores-dev-real"))
  dev_attack=load_scores(os.path.join(args.directory, "scores-dev-attack"))
  eval_real=load_scores(os.path.join(args.directory, "scores-eval-real"))
  eval_attack_all=load_scores(os.path.join(args.directory, "scores-eval-attack"))

  # Querying the database
  db = Database()
  scores_attack_set = []
  attack_known = db.objects(purposes='attack', support=('S1', 'S2', 'S3', 'S4', 'S5'), groups='eval', protocol='CM')
  attack_unknown = db.objects(purposes='attack', support=('S6', 'S7', 'S8', 'S9', 'S10'), groups='eval', protocol='CM')
  eval_attack_known= read_attack_scores(attack_known, os.path.join(args.directory, "scores-eval-attack"))
  eval_attack_unknown= read_attack_scores(attack_unknown, os.path.join(args.directory, "scores-eval-attack"))
  

  #for i in range(len(dev_attack)):
  #  dev_attack[i] = dev_attack[i][~numpy.isnan(dev_attack[i])]
  #for i in range(len(dev_real)):
  #  dev_real[i] = dev_real[i][~numpy.isnan(dev_real[i])]
  #for i in range(len(eval_attack_known)):
  #  eval_attack_known[i] = eval_attack_known[i][~numpy.isnan(eval_attack_known[i])]
  #for i in range(len(eval_attack_unknown)):
  #  eval_attack_unknown[i] = eval_attack_unknown[i][~numpy.isnan(eval_attack_unknown[i])]
  #for i in range(len(eval_real)):
  #  eval_real[i] = eval_real[i][~numpy.isnan(eval_real[i])]

  if(args.invert=="true"):
    dev_real=[-f for f in dev_real]
    dev_attack=[-f for f in dev_attack]
    eval_real=[-f for f in eval_real]
    eval_attack_known=[-f for f in eval_attack_known]
    eval_attack_unknown=[-f for f in eval_attack_unknown]
  
  threshold = bob.measure.eer_threshold(dev_attack, dev_real)
  print(threshold)
    # apply threshold to development set
  far, frr = bob.measure.farfrr(dev_attack, dev_real, threshold)
  print("The EER of the development set is %2.3f%%" % ((far + frr) * 50.)) # / 2 * 100%
    # apply threshold to evaluation set
  far_known, frr_known = bob.measure.farfrr(eval_attack_known, eval_real, threshold)
  far_unknown, frr_unknown = bob.measure.farfrr(eval_attack_unknown, eval_real, threshold)
  hter_known = (far_known + frr_known) * 50.
  hter_unknown = (far_unknown + frr_unknown) * 50.
  far_all, frr_all = bob.measure.farfrr(eval_attack_all, eval_real, threshold)
  hter_all = (far_all + frr_all) * 50.
  print("Known: The HTER of the evaluation set is " + str(hter_known)) # / 2 * 100%  
  print("Unknown: The HTER of the evaluation set is " + str(hter_unknown)) # / 2 * 100%  
  print("All: The HTER of the evaluation set is " + str(hter_all)) # / 2 * 100%  


  resfile = open(os.path.join(args.output, 'eval_results.txt'), "w")
  resfile.write("Average over known & %2.6f \\\\ \\hline \n" % (hter_known))
  resfile.write("Average over unknown & %2.6f \\\\ \\hline \n" % (hter_unknown))
  resfile.write("Average & %2.6f \\\\ \\hline \n" % (hter_all))
  resfile.close()




if __name__ == '__main__':
    main()
