# -*- coding: utf-8 -*-

"""Console script for tessellate."""

import click


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--project',prompt='What is your project called?', help="Name of Project")
@click.argument('input-dir',
                type=click.Path(exists=True),
                nargs=-1,
                required=True
                # help = "Directory containing input files"
                )
@click.option('--input-format',
              type=click.Choice(['builtin', 'pdb', 'pdblist']),
              default="pdblist",
              help="Input format: builtin, pdb, pdblist"
              )
@click.option('--output-dir',
              default="",
              help="Output directory"
              )
@click.option('--output-format',
              type=click.Choice(['txt', 'json', 'bson']),
              default="json",
              help="Output format: txt, json, bson"
              )
@click.option('--ignore/--no-ignore', default=True,
              help="Choose to ignore amino acids/water in PDB data when looking for cycles")
@click.option('--ignore-append', 'ignore_behaviour', flag_value="append", default=True,
              help="Append residues in ignore file to existing ignore dictionary")
@click.option('--ignore-overwrite', 'ignore_behaviour', flag_value="overwrite",
              help="Use residues in ignore file and exclude existing ignore dictionary")
@click.option('--ignore-file', default="ignorenames", help="Use this ignore file")
@click.option('--ligand/--no-ligand', default=True, help="Use builtin ligand dictionary when choosing cycle ordering")
@click.option('--ligand-append', 'ligand_behaviour', flag_value="append", default=True,
              help="Append ligands in ligand file to existing dictionary")
@click.option('--ligand-overwrite', 'ligand_behaviour', flag_value="overwrite",
              help="Use ligand file and exclude existing dictionary")
@click.option('--ligand-file', default=None, help="Use this ligand file")
@click.option('-v', '--verbose',
              count=True,
              default=0,
              help="Increase output verbosity."
              )
@click.option('-q', '--quiet',
              is_flag=True,
              help="Only show log warnings"
              )

def main(input_dir, input_format, output_dir, output_format, ignore, ignore_behaviour, ignore_file, ligand, ligand_behaviour,
         ligand_file, verbose, quiet):
    """Console script for tessellate."""
    import tessellate.tessellate as tt
    from pathlib import Path
    import os
    import logging
    logger = logging.getLogger(__name__)
    
    # . making logging changes here only affects this function - all other modules read the init.
    if quiet:
        logger.critical("Changing to ERROR level, doesn't propagate")
        logger.setLevel(level=logging.ERROR)  # . only show errors and above

    if verbose > 0:  # https://docs.python.org/3/library/logging.html#levels
        logger.critical("Changing to DEBUG level, doesn't propagate")
        logger.setLevel(level=logging.DEBUG)  # show debug and worse

    # debug all inputs
    logger.debug(input_dir)
    logger.debug(input_format)
    logger.debug(output_format)
    logger.debug(ignore)
    logger.debug(ignore_behaviour)
    logger.debug(ignore_file)
    logger.debug(ligand)
    logger.debug(ligand_behaviour)
    logger.debug(ligand_file)
    logger.debug(verbose)
    logger.debug(quiet)

    from sys import version_info
    pathlib_unsupported=False
    if version_info.minor < 6:
        logger.debug("Python 3.4/5 tweaks required for PathLib")
        pathlib_unsupported=True

    # . Check input dir exists
    if input_dir == "" or input_dir == None or len(input_dir)==0:
        logger.critical("No input_dir defined")
        exit(1)

    #. Check if output dir exists and create
    if output_dir == "" or output_dir == None or len(output_dir)==0:
        pass
    else:
        try:
            os.makedirs(output_dir, exist_ok=True)
        except:
            raise
    
    for dirs in input_dir:
        if os.path.isdir(dirs):
            logger.debug("input_dir is a directory")
            pathlist = Path (dirs).glob('*')
        else:
            logger.debug("input_dir is a file")
            pathlist = Path ('.').glob(dirs)
        # pathlist=[input_dir[0]]
    # . If builtin format call the appropriate function
        if input_format == "builtin":
            for path in pathlist:
                try:
                    tail=path.name
                    if pathlib_unsupported:
                        path=str(path)
                    tt.analyse_pucker(path, output_dir=output_dir, outputfile="tessellate_report_"+str(tail), output_format=output_format)
                except:
                    raise
        elif input_format == "pdb":
            for path in pathlist:
                try:
                    tail=path.name
                    logger.critical("PDB standalone, development in progress")
                    exit(1)
                    if pathlib_unsupported:
                        path=str(path)
                    tt.analyse_pucker_from_pdbs(path, output_dir=output_dir, outputfile="tessellate_report_"+str(tail), output_format=output_format, ligandinputfilename=ligand_file)
                except:
                    raise
    
        elif input_format == "pdblist":
            for path in pathlist:
                try:
                    tail=path.name
                    if pathlib_unsupported:
                        path=str(path)
                    tt.analyse_pucker_from_pdbs(path, output_dir=output_dir, outputfile="tessellate_report_"+str(tail), output_format=output_format, ligandinputfilename=ligand_file)
                except:
                    raise
    
        else:
            logger.critical("Code not yet developed for this function")
            exit(1)


if __name__ == "__main__":
    from sys import version_info
    if version_info.major < 3:
        log.critical("Python 2 not supported")
        exit(1)
    main()
