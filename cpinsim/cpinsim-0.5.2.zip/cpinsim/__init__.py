# -*- coding: utf-8 -*-

import argparse

import cpinsim.annotate_constraints as annotate_constraints
import cpinsim.proteinparser as proteinparser
import cpinsim.protein_type as protein_type
from cpinsim.infinite_simulation import InfiniteSimulation


def get_argument_parser():
    """ Return an argument parser.
    """

    parser = argparse.ArgumentParser(prog="cpinsim", description="CPINSim - Constrained Protein Interaction Networks Simulator\nPackage for the simulation of constrained protein interaction networks. Beside simulation there are methods for data preprocessing provided:  Annotation of interactions and constraints with domains; A parser to provide the needed protein input format.")

    subparsers = parser.add_subparsers(help="Choose one of the following functions from the cpinsim package.")


    #---------- parser for annotating constraints ----------#
    parser_ann = subparsers.add_parser("annotate", help="Annotate constraints and interactions without constraints with domains.")

    parser_ann.add_argument("--interactions_without_constraints", "-i", nargs="+", metavar="PATH", help="Files containing the underlying network: pairwise interactions without constraints. Two columns InteractorA | InteractorB")

    parser_ann.add_argument("--competitions", "-c", nargs="+", metavar="PATH", help="Files containing the competitions. Two columns: Host | Competitors (comma separated)")

    parser_ann.add_argument("--allosteric_effects", "-a", nargs="+", metavar="PATH", help="Files containing the allosteric effects. Four columns: Host | Interactor | Activator | Inhibitor")

    parser_ann.add_argument("--extended_inference", "-e", action='store_true', help="Extended inference for missing domains in competitions.")

    parser_ann.add_argument("--output_interactions", "-oi", metavar="PATH", help="One output file containing all annotated pairwise interactions.")
    parser_ann.add_argument("--output_competitions", "-oc", metavar="PATH", help="One output file containing all annotated competitions.")
    parser_ann.add_argument("--output_allosterics", "-oa", metavar="PATH", help="One output file containing all annotated allosteric effects.")

    parser_ann.set_defaults(func=annotate)


    #---------- parser for the proteinparser ----------#
    parser_proteins = subparsers.add_parser("parse", help="Parse proteins from annotated constraints and interactions into defined text format.")

    parser_proteins.add_argument("--interactions_without_constraints", "-i", nargs="+", help="Files containing the annotated pairwise interactions.")

    parser_proteins.add_argument("--competitions", "-c", nargs="+", help="Files containing the annotated competitions.")

    parser_proteins.add_argument("--allosteric_effects", "-a", nargs="+", help="Files containing the annotated allosteric effects.")

    parser_proteins.add_argument("--output", "-o", help="Output file containing the parsed proteins.")

    parser_proteins.set_defaults(func=parse_proteins)


    #---------- parser for the simulation ----------#
    parser_sim = subparsers.add_parser("simulate", help="Simulate the complex formation in a cell with given proteins. The proteins either have a fixed number of copies, or are chosen according to protein concentrations. Proteins associate or dissociate according to the association- and dissociation-probability. It is possible to perturb proteins and modify their concentration to simulate knockout or overexpression.")

    parser_sim.add_argument("proteins", help="Path to a csv-file containing the parsed proteins.")

    group_protein_sampling = parser_sim.add_mutually_exclusive_group()
    group_protein_sampling.add_argument("--concentrations", "-c", nargs=2, metavar=("MAX-PROTEIN-INSTANCES", "PATH/TO/CONCENTRATIONS"), help="Maximum number of protein instances and path to a csv-file containing a concentration for each protein.")
    group_protein_sampling.add_argument("--number-of-copies", "-n", metavar="N", type=int, help="Number of copies for each protein type.")

    parser_sim.add_argument("--association-probability", "-ap", metavar="P", type=float, help="The probability for a new association between two proteins (default: %(default)s).", default=0.005)

    parser_sim.add_argument("--dissociation-probability", "-dp", metavar="P", type=float, help="The probability for a dissociation of a pairwise interaction (default: %(default)s).", default=0.0125)

    parser_sim.add_argument("--max-steps", "-m", type=int, help="Maximum number of simulation steps if convergence is not reached until then (default: %(default)s).", default=1000)

    parser_sim.add_argument("--perturbation", "-p", nargs=2, action='append', metavar=("PROTEIN", "FACTOR"), help="Protein that should be overexpressed or down regulated by factor FACTOR for perturbation analysis.")

    parser_sim.add_argument("--output-graph", "-og", metavar="PATH", required=True, help="Pickle the complete graph at the end of simulation (after last dissociation step) and write it to the given path.")

    parser_sim.add_argument("--output-log", "-ol", metavar="PATH", help="Write some log information of each simulation stept to the given path. If not specified, std-out is used.")

    parser_sim.set_defaults(func=simulate)

    return parser


def annotate(args):
    """ Annotate constraints with domains.
    """
    if args.competitions is not None:
        annotate_constraints.read_competitions(args.competitions)

    if args.allosteric_effects is not None:
        annotate_constraints.read_allosteric_effects(args.allosteric_effects)

    if args.interactions_without_constraints is not None:
        annotate_constraints.read_interactions_without_constraints(args.interactions_without_constraints)

    annotate_constraints.normalize()
    annotate_constraints.remove_redundant_nones()
    if args.extended_inference:
        annotate_constraints.domain_inference_competition_host()
        annotate_constraints.domain_inference_competitors()
    annotate_constraints.apply_artificial_domains()
    annotate_constraints.write_annotated_files(args.output_interactions, args.output_competitions, args.output_allosterics)


def parse_proteins(args):
    """ Parse proteins from annotated interactions and constraints.
    """
    pp = proteinparser.Proteinparser()

    if args.interactions_without_constraints is not None:
        pp.parse_interactions_without_constraints(args.interactions_without_constraints)

    if args.competitions is not None:
        pp.parse_competitions(args.competitions)

    if args.allosteric_effects is not None:
        pp.parse_allosteric_effects(args.allosteric_effects)

    pp.write_proteins_in_file(args.output)


def simulate(args):
    """  Simulation
    """
    proteins = protein_type.read_proteins(args.proteins)
    sim = InfiniteSimulation(proteins, args.concentrations, args.number_of_copies, args.perturbation, args.output_log, args.output_graph)
    sim.simulate_network(args.max_steps, args.association_probability, args.dissociation_probability)


def main(pargs=None):
    """ Mainfunction
    """
    parser = get_argument_parser()

    args = parser.parse_args() if pargs is None else parser.parse_args(pargs)

    # case if no arguments are given
    if "func" not in args:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":

    main()
