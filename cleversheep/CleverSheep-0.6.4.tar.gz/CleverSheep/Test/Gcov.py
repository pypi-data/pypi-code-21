#!/usr/bin/env python
"""Support for coverage analysis using *gcov*.

This largely provides a wrapper around the *gcov* command, which makes it
relatively easy to collect and collate statistics about coverage for one or
more C/C++ source files.

It also provides support for special 'pragma' comments in the source to
indicate code that is considered unreachable. This allows a more more pragmatic
definition of 100% code coverage, where appropriate. (And I mean where
appropriate. Where desirable and possible, I believe that you should generally
aim for proper 100%, by stubbing as appropriate. However, sometime constraints
(financial, lack of time, etc.) make this ideal inpracticable.)

The functions in here assume a number of things:

    - We want the (modified) ``source.c.gcov`` file to go in  the same
      directory as the source.

"""


import warnings
import os
import sys
import commands
import shutil
import re
from cStringIO import StringIO

from CleverSheep.Prog import Iter, Aspects, Files
from CleverSheep.Test import ImpUtils

warnings.warn("""
The 'CleverSheep.Test.Gcov' module is deprecated. Please use the official gcov
version.

It will no longer be supported from version 0.6 onwards and will be removed in
version 0.7.

----------------------------------------------------------------------
""", PendingDeprecationWarning, stacklevel=2)


# Lines that gcov consider uninteresting, such as blank lines and comments.
rIgnored = re.compile(r'^ {8}-: *\d+:')

# Lines that gconv has marked as being covered.
rCovered = re.compile(r'^ *\d+: *\d+:')

# Lines that gconv has marked as not covered.
rNotCovered = re.compile(r'^ {4}#####: *\d+:')

# This should match any line in a gcov annotated file.
rAnyLine = re.compile(r'^.{9}:( *\d+):(.*)')

# This matches the lines that are not from the original source.
rZeroLine = re.compile(r'^.{9}:    0:(.*)')


class Skipper(object):
    def __init__(self):
        self.strict = True

    def isStart(self, line):
        return False

    def isEnd(self, line):
        return False


class BlockPragmaSkipper(Skipper):
    def __init__(self, name, strict=True):
        Skipper.__init__(self)
        self.rStart = re.compile(r'^.{9}: *\d+:(.*)//pragma: %s *\r?$' % name)
        self.strict = strict

    def isStart(self, line):
        m = self.m = self.rStart.match(line)
        if not m:
            return
        code = m.group(1)
        self.endMark = None
        if code.strip().startswith("{"):
            ind = len(code) - len(code.lstrip())
            self.endMark = (" " * ind) + "}"

        return self.m

    def isEnd(self, line):
        if not self.endMark:
            return True
        m = rAnyLine.match(line)
        if m.group(2).startswith(self.endMark):
            return True


# ============================================================================
# The configurable bits of the Gcov module.
#
# The skips tuple contains tupls of (statName, skipper). The statName is a
# symbolic statName for the type of thing being skipped. The skipper is an
# instance of a Skipper. This can be pretty much anything, except for the
# predefined ones, namely::
#
#     "lCount" "executable" "reachable" "slack" "covered" "notCovered"
#     "percent" "FILE"
#
# The headingSpec defines what the colums of the report will be. Each enty is a
# tuple of (headingName, statName). The statName can be any of the predefined
# names (above) or a name in the skips tuple. The length of each headingName
# defines the column's width; any dots in a headingName are replaced with
# spaces.
# ============================================================================
skips = (
    ("unreachable", BlockPragmaSkipper("unreachable")),
    ("debug",       BlockPragmaSkipper("debug", strict=False)),
    ("untested",    BlockPragmaSkipper("untested", strict=False)),
)

headingSpec = (
    (".Lines",    "lCount"),
    ("Unreach",   "unreachable"),
    ("Debug",     "debug"),
    ("Untest",    "untested"),
    (".Slack",    "slack"),
    ("..Exec",    "executable"),
    (".Reach",    "reachable"),
    ("..Cov",     "covered"),
    ("..N/C",     "notCovered"),
    ("Percent",   "percent"),
    ("File",      "FILE"),
)


skipNames = [name for name, p in skips]
def setSkips(newSkips):
    global skipNames, skips
    skips = newSkips
    skipNames = [name for name, p in skips]



def zeroStats():
    """Return a dictionary holding initialised coverage stats.

    One of these gets created for each source files processed and we also have
    one to hold the totals for all files. Using a dictionary for this makes
    much of the remaining code cleaner and more generic.
    """
    counts = {"ignored": 0, "covered": 0, "notCovered": 0,
            "others": 0, "lCount": 0,
            "slack": 0,
            "executable": 0, "reachable": 0, }
    for name in skipNames:
        counts[name] = 0
    return counts


def doSkippedLineCounts(counts, line, outF, skipper):
    skipCount = 0
    if rCovered.match(line) and not skipper.strict:
        counts["executable"] += 1
        counts["covered"] += 1
        outF.write("!!" + line[2:])
        counts["slack"] += 1

    elif rIgnored.match(line):
        counts["ignored"] += 1
        outF.write(line)

    else:
        if rNotCovered.match(line):
            counts["executable"] += 1
        skipCount += 1
        m = rAnyLine.match(line)
        outF.write(".........:%s:%s\n" % m.groups())

    return skipCount


def skipBlock(counts, f, outF, skipper):
    """Skip a block of code, ignoring all lines within it.

    This is used to ignore marked sections of code for the purposes of counting
    whether lines have been covered or not.
    """
    skipCount = doSkippedLineCounts(counts, f.next(), outF, skipper)
    slackCount = 0
    for line in f:
        m = rAnyLine.match(line)
        if not m:
            f.unget(line)
            break

        if skipper.isEnd(line):
            f.unget(line)
            break

        if doSkippedLineCounts(counts, line, outF, skipper):
            skipCount += 1
        if not rZeroLine.match(line):
            counts["lCount"] += 1
    return skipCount


def matchesSkipStart(line):
    """Check whether `line` is the start of a block to be skipped.

    :Param line:
        The text of the line to check.
    """
    for name, skipper in skips:
        if skipper.isStart(line):
            return name, skipper
    return None, None


def getStats(inCovPath, outCovPath):
    counts = zeroStats()
    counts["FILE"] = outCovPath

    source_file = open(inCovPath)
    try:
        f = Iter.PushBackIterator(StringIO(source_file.read()))
    finally:
        source_file.close()
    outF = open(outCovPath, "w")
    for line in f:
        if not rZeroLine.match(line):
            counts["lCount"] += 1
        skipName, skipper = matchesSkipStart(line)
        if not incAll and skipName is not None:
            f.unget(line)
            skipCount = skipBlock(counts, f, outF, skipper)
            counts[skipName] += skipCount
            continue

        if rNotCovered.match(line):
            counts["executable"] += 1
            counts["notCovered"] += 1
        elif rCovered.match(line):
            counts["executable"] += 1
            counts["covered"] += 1
        elif rIgnored.match(line):
            counts["ignored"] += 1
        else:
            counts["others"] += 1
        outF.write(line)

    return counts


def mungeArgs(args):
    for path in args:
        if ":" in path:
            path, subDir = path.split(":", 1)
        else:
            subDir = ""
        path = os.path.abspath(path)
        dirname = os.path.dirname(path) or "."
        subDirname = dirname
        if subDir:
            subDirname = os.path.join(dirname, subDir)
            if not os.path.exists(subDirname):
                subDirname = dirname

        base, ext = os.path.splitext(os.path.basename(path))

        yield path, dirname, subDirname, base


def erase(args):
    """Reset coverage - removes the data files.

    """
    for path, dirname, subDirname, base in mungeArgs(args):
        dataFile = "%s.da" % os.path.join(subDirname, base)
        try:
            os.unlink(dataFile)
        except OSError:
            sys.write(tderr, "Unable to remove %r" % dataFile)
            sys.write("\n")


def grokHdr(spec):
    fmt = ""
    lines = ""
    hdr = ""
    for i, (hdrName, statName) in enumerate(spec):
        if i:
            fmt += " "
            lines += " "
            hdr += " "
        fmt += "%%(%s)%ds" % (statName, len(hdrName))
        lines += "-" * len(hdrName)
        hdr += hdrName.replace(".", " ")

    return fmt, lines, hdr


def workPercent(counts):
    if counts["reachable"] > 0:
        counts["percent"] = "%7.2f" % (
                float(counts["covered"]) / counts["reachable"] * 100.0)
    else:
        counts["percent"] = "----"

    # Ensure that we do not accidently report 100% due to rounding errors.
    if counts["percent"] == "100.00" and counts["covered"] < counts["reachable"]:
        counts["percent"] = "99.99"


def addTotals(totals, counts):
    names = ["lCount", "executable", "reachable", "covered", "notCovered",
            "slack"]
    for name in names + skipNames:
        totals[name] += counts[name]


def sum(counts, names):
    t = 0
    for name in names:
        t += counts[name]
    return t


def workStats(counts):
    counts["reachable"] = counts["executable"] - sum(counts, skipNames)
    workPercent(counts)


@Aspects.protectCwd
def main(args, truePaths=False, out=sys.stdout):
    """The main for this module.

    :Params args:
        A list of C/C++ sources to analyse for coverage information.
    :Param truePaths:
        IF set then the list of sources is taken to be true paths, relative to
        the CWD, rather than (the default) paths relative to the project root.
    """
    projectRoot = ImpUtils.findRoot()
    if truePaths:
        realArgs = list(mungeArgs(args))
    if projectRoot:
        os.chdir(projectRoot)
    if not truePaths:
        realArgs = list(mungeArgs(args))
    perFileStats = {}
    coverPaths = []

    for path, dirname, subDirname, base in realArgs:
        subDirname = os.path.abspath(subDirname)
        base_name = os.path.basename(path)
        cmd = "gcov -p -o %s %s" % (subDirname, base_name)
        #print("CMD", cmd)
        here = os.getcwd()
        try:
            os.chdir(dirname)
        except OSError:
            stat = 1
            text = "Could not chdir to %r" % dirname
        else:
            try:
                stat, text = commands.getstatusoutput(cmd)
            finally:
                os.chdir(here)
        if stat != 0:
            if text.startswith("Could not open basic block file"):
                continue
            if text.startswith("Could not open data file"):
                continue
            out.write("GCOV: Error for %s" % path)
            out.write("\n")
            out.write(text)
            out.write("\n")
            continue

        found = 0
        root, ext = os.path.splitext(os.path.basename(path))
        covPath = None
        for line in text.splitlines():
            # Gcov's output is a moveable feast. The following code handles the
            # formats I have seen.
            if line.startswith("Creating "):
                covPath = line.split(None, 1)[1][:-1]
            elif ":creating `" in line:
                covPath = line.split('`')[-1][:-1]
            elif ":creating '" in line:
                covPath = line.split("'")[-2]
            if covPath:
                coveredPath = covPath[:-5] # Lose '.gcov'
                cRoot, cExt = os.path.splitext(coveredPath)
                if cRoot == root:
                    found = 1
                    coverPaths.append(os.path.join(dirname, covPath))

        if not found:
            # No coverage file(s) got created, apparently
            # out.write("NO COV FILE", path)
            # out.write("\n")
            continue

    # Now generate per-file stats and update the annotation of the
    # C/C++ sources.
    for covPath in coverPaths:
        outCovPath = os.path.join(dirname, covPath)
        perFileStats[os.path.join(dirname, covPath)] = getStats(
                covPath, outCovPath)

        # shutil.copy(covPath, dirname)
        if os.path.abspath(covPath) != os.path.abspath(outCovPath):
            os.unlink(covPath)

    fmt, lines, hdr = grokHdr(headingSpec)
    out.write(hdr)
    out.write("\n")
    out.write(lines)
    out.write("\n")

    totals = zeroStats()
    totals["FILE"] = "OVER ALL"

    for name in sorted(perFileStats.keys()):
        counts = perFileStats[name]
        counts["FILE"] = Files.relName(counts["FILE"])
        workStats(counts)
        addTotals(totals, counts)
        out.write(fmt % counts)
        out.write("\n")

    workPercent(totals)
    out.write(fmt % totals)
    out.write("\n")


incAll = False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('sources',
                        nargs='+',
                        help='The source file or files to generate'
                             ' coverage for')

    args = parser.parse_args()
    main(args.sources)

