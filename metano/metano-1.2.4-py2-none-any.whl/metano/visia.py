#!/usr/bin/env python

from metabolicmap import MetabolicMap
import re
import MySQLdb
import optparse
import sys

sys.path.append("/opt/metano/src")
try:
    from metabolicmodel import MetabolicModel
except ImportError:
    from metano.metabolicmodel import MetabolicModel

ecRegex = re.compile("-[0-9]+\.[0-9|-]+\.[0-9|-]+\.[0-9|-]+(_NADP?)?$")

class OptionParser(optparse.OptionParser):
    """ Extension of OptionParser with function for checking required arguments
    """

    def check_required(self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)

def main(argv=None):

#    server = "fileserver.bioinfo.nat.tu-bs.de"
#    user = "praktikant"
#    pw = "praktikant"
#    database = "metabolic_pathways"
    
    server = "134.169.105.249"
    user = "student"
    pw = "student"
    database = "sysbio"

    # command line options: for the selection of the model, 
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-r","--reaction-file", dest="reactionFile",
                      help="File containing reactions in the metano format. EC numbers contained in the reaction names will be highlighted on the metabolic map", metavar="FILE")
    parser.add_option("-o","--output-file", dest="outputFile",
                      help="Name of the output file. Defaults to metabolicmap.gml", metavar="FILE", default="metabolicmap.gml")
    parser.add_option("-f","--font-size", dest="fontSize",
                      help="Font size of the labels in the metabolic map", metavar="FILE")
    parser.add_option("-v","--verbosity", dest="verbosityLevel", default=0,
                      help="Sets the verbosity level to 0 (no output), 1 (print status messages) or 2 (debug output)", metavar = "LEVEL")
    
    options, _ = parser.parse_args()
    parser.check_required("-r")
    
    if options.verbosityLevel:
        # TODO catch ValueError
        options.verbosityLevel=int(options.verbosityLevel)
    
    # read the metabolic model from file
    model = MetabolicModel()
    model.addReactionsFromFile(options.reactionFile)

    # parse EC numbers from reaction names
    ecList=[]
    for reaction in model:
        ecMatch = re.search(ecRegex, reaction.name)
        
        if ecMatch:
            ecNo = reaction.name[ecMatch.start():ecMatch.end()][1:]
            ecNo = re.sub("_NADP?","",ecNo)
            ecList.append(ecNo)

    # create the metabolic map
    theMap = MetabolicMap(server, user, pw, database, options.verbosityLevel)
    if options.fontSize:
        theMap.fontSize=options.fontSize
    
    theMap.drawEnzymes(ecList)
    theMap.drawRemainingReactions()
    theMap.drawPathwayLabels()
    theMap.writeToGML(options.outputFile)

if __name__ == "__main__":
    main()
