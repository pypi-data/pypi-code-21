import os, argparse, logging, glob

CUR_DIR = os.path.dirname( os.path.abspath(__file__))

from stat import *
from contextlib import contextmanager

log = logging.getLogger("symcopy")
@contextmanager
def working_directory(directory):
    owd = os.getcwd()
    try:
        os.chdir(directory)
        yield directory
    finally:
        os.chdir(owd)
        
def mklink(Link, Target):
    assert os.path.exists(Target)
    mode = os.stat(Target)[ST_MODE]
    if os.name == 'nt':
        cmd = 'mklink {} "{}" "{}"'.format(
                            "/D" if S_ISDIR(mode) else "",
                            Link, Target)
    elif os.name == 'posix':
        cmd = 'ln -s "{}" "{}"'.format(Target, Link)
    else:
        raise OSError("Unknown OS: {}".format(os.name))
    log.debug(cmd)
    assert not os.path.exists(Link)
    
    ret = os.system( cmd )
    assert os.path.exists(Link)
    return ret
    
def symcopy(LinkDir, TargetDir):
    if not os.path.exists(LinkDir):
        raise ValueError("Directory not found: {}".format(LinkDir))
    if not os.path.exists(TargetDir):
        raise ValueError("Directory not found: {}".format(TargetDir))

    FullSrc = os.path.abspath(LinkDir)
    FullTar = os.path.abspath(TargetDir)
    ExistingDirectories, TargetDirectories = {},{}
    
    with working_directory(FullSrc):
        for ed in glob.glob( '*' ):
            ExistingDirectories[ed.lower()] = ed
    with working_directory(FullTar):
        for td in glob.glob( '*' ):
            TargetDirectories[td.lower()] = td
    
    for tld in TargetDirectories:
        if not tld in ExistingDirectories:
            Target = os.path.join(FullTar, TargetDirectories[tld])
            Link = os.path.join(FullSrc, TargetDirectories[tld])
            logging.debug( "{} => {}".format(Link, Target ) )
            try:
                mklink( Link, Target )
            except AssertionError:
                logging.exception("Failed to link {} => {}".format(Link, Target ) )
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('SrcDir')
    parser.add_argument('TarDir')
    parser.add_argument('--verbose', '-v', action='count')
    
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        
    symcopy( args.SrcDir, args.TarDir )
    
    