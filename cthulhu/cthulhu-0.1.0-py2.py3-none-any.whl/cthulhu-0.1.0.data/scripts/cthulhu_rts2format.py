#!python

import copy
import glob
import logging
import argparse
import multiprocessing as mp
import cthulhu.rts_log_tools as crlt

# Import tqdm without enforcing it as a dependency
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(*args, **kwargs):
        if args:
            return args[0]
        return kwargs.get("iterable", None)


def wrapper(log):
    out = args.format.lower()
    if out == "yaml":
        crlt.rts2yaml(log)
    elif out == "json":
        crlt.rts2json(log)
    elif out == "pickle":
        crlt.rts2pickle(log)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--format", required=True, type=str,
                        help="Specify the format to convert the RTS log to. "
                        "Supported formats: yaml, json, pickle.")
    parser.add_argument("-o", "--overwrite", action="store_true",
                        help="Overwrite existing files. Default: %(default)s")
    parser.add_argument("--filtering", action="store_false",
                        help="Filter the RTS logs before converting. "
                        "Avoids processing multiple logs from the same observation. "
                        "Default: %(default)s")
    parser.add_argument("logs", nargs='*', help="Paths to log files, and/or text "
                        "files with paths to log files (must end with \".txt\").")
    args = parser.parse_args()

    logger = logging.getLogger(__file__)

    # Input is either a text file specifying log files (suffix .txt), or log files.
    if len(args.logs) == 0:
        logger.error("Aborting: Need log files to process.")
        exit(1)

    # Check that the output format is supported.
    if args.format.lower() not in ["yaml", "json", "pickle"]:
        logging.error("Unknown format specified (%s)." % args.format)
        exit(1)

    # Loop over the input files, appending them into a list.
    # If we're not overwriting, then grab the obsids from the logs too.
    logs = {}
    for f in args.logs:
        if isinstance(f, str) and f.endswith(".txt"):
            with open(f) as f2:
                for l in f2.readlines():
                    log = l.strip()
                    logs[log] = ""
                    if not args.overwrite:
                        with open(log, 'r') as f3:
                            contents = f3.read(8000)
                            logs[log] = "%s.%s" % (crlt.extract_obsid(log, contents),
                                                   args.format.lower())
        else:
            logs[f] = ""
            if not args.overwrite:
                with open(f, 'r') as f2:
                    contents = f2.read(8000)
                    logs[f] = "%s.%s" % (crlt.extract_obsid(f, contents), args.format.lower())

    # If we're not overwriting, then check what logs have already been converted.
    if not args.overwrite:
        converted_logs = glob.glob("*.%s" % args.format.lower())
        logs_copy = copy.copy(logs)
        for l in logs_copy:
            if logs_copy[l] in converted_logs:
                del(logs[l])

    # Filter the logs, if necessary.
    if args.filtering:
        logs = crlt.filter_logs(logs.keys())
    else:
        logs = logs.keys()

    # If there's more than one log, process in parallel with a progress bar.
    if len(logs) == 0:
        pass
    if len(logs) == 1:
        wrapper(logs[0])
    else:
        p = mp.Pool(processes=mp.cpu_count())
        with tqdm(total=len(logs)) as pbar:
            for i, _ in tqdm(enumerate(p.imap(wrapper, logs))):
                pbar.update()
        pbar.close()
        p.close()
        p.join()
