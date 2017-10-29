import os
import re

from CleverSheep.Prog import Files
from CleverSheep.Test.Tester import options, execDir

ulChars = "==-~.@:_#"


class TrimmedFile(object):
    """File like object that trims leading and trailing lines.

    It also suport the context protocol.

    """
    trunc = {}

    def __init__(self, path, mode):
        """Initialisation.

        This behaves much like a standard Python file, but it trims leading and trailing
        white space for a given file.

        It is a slightly complicated solution for a not very important problem, but does
        maintain very clean output and helps testing.

        :Parameters:
          path, mode
            As for the built-in ``open/file`` functions.

        """
        self.path = os.path.normpath(path)
        if "a" not in mode:
            self.buf = None
        else:
            if self.path in self.trunc:
                self.buf = self.trunc[self.path]
            else:
                self.buf = []
        self.partialLine = False
        self.f = open(self.path, mode)

    def write(self, s):
        lines = s.splitlines(True)
        if self.buf is None:
            while lines and not lines[0].strip():
                lines.pop(0)
            if not lines:
                return
            self.buf = []

        hasNewLine = s.endswith("\n")
        for i, line in enumerate(lines):
            if i == 0 and self.partialLine and self.buf:
                self.buf[-1] += line
            else:
                self.buf.append(line)
        self.partialLine = not hasNewLine

    def flush(self):
        if self.buf is None:
            return

        # Keep any trailing blank and partial lines.
        keep = []
        if self.buf and self.partialLine:
            keep.append(self.buf.pop())
        while self.buf and not self.buf[-1].strip():
            keep.append(self.buf.pop())
        self.f.write("".join(self.buf))
        self.f.flush()
        self.buf = list(reversed(keep))

    def close(self):
        self.flush()
        self.f.close()
        self.trunc[self.path] = self.buf

    #{ Context management protocol
    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_val, exc_b):
        self.close()

    #}


class SphinxNode(object):
    def __init__(self):
        self._children = []
        self.parent = None


def commSubPath(a, b):
    aa = a.split(os.path.sep)
    bb = b.split(os.path.sep)
    while aa and bb and aa[0] == bb[0]:
        aa.pop(0)
        bb.pop(0)
    return os.path.sep.join(bb)


class SphinxSuite(SphinxNode):
    def __init__(self, lev, suite, rootDir, parent=None):
        from CleverSheep.Test import Tester

        pathParts, klass, _ = suite.uid
        path = os.path.join(*pathParts)
        if not os.path.isabs(path):
            path = os.path.join(Tester.treeRoot, path)
        path = Files.relName(path, cwd=rootDir)
        self.children = []
        self.tests = []
        self.known = {}
        self.lev = lev
        self.uid = suite.uid
        self.suitePath = path
        self.suite = suite
        self.parent = parent
        self.toc = []
        if klass is None:
            self.parent.addToc(self)

        self.contents = []
        self.contents.append("%s" % suite.summary)
        self.contents.append("")
        for line in suite.details:
            self.contents.append(line)
        self.contents.append("")
        self.contents.append("")
        if klass:
            self.title = klass
        else:
            if path.endswith("all_tests.py"):
                path = os.path.basename(path)
            path = path.replace(".py", "")
            path = path.replace(".pyc", "")
            self.title = path
        self.label = None

    def addToc(self, suite):
        #print "ADD TOC", self.path, suite.path
        self.toc.append(commSubPath(self.path, suite.path))

    @property
    def path(self):
        return self.suitePath.replace(".pyc", "").replace(".py", "") + ".rst"

    def addSubSuites(self, suites, rootDir):
        if not suites:
            return []
        lev, suite = suites[0]
        ret = []
        rest = suites
        if lev == self.lev + 1 and suite.uid not in self.known:
            #print "TRY: ", lev, self.lev, (self.suite.uid, suite.parentUid)
            if self.suite.uid == suite.parentUid:
                #print "ADD: ", lev, self.lev, (self.suite.uid, suite.parentUid)
                #print lev, suite.uid
                ss = SphinxSuite(lev, suite, rootDir, self)
                self.known[suite.uid] = ss
                self.children.append(ss)
                ret = [ss]
                rest = suites[1:]

        for child in self.children:
            for s in child.addSubSuites(rest, rootDir):
                ret.append(s)
        return ret

    def generate(self):
        pathParts, klass, _ = self.suite.uid
        if not os.path.isabs(options.get_option_value("sphinx")):
            path = os.path.join(execDir, options.get_option_value("sphinx"), self.path)
        else:
            path = os.path.join(options.get_option_value("sphinx"), self.path)
        if klass is None:
            Files.mkParentDir(path)
            f = TrimmedFile(path, "w")
        else:
            f = TrimmedFile(path, "a")

        with f:
            self.write(f)
            for test in self.tests:
                test.write(f)

        for suite in self.children:
            suite.generate()

    def relLevel(self):
        pathParts, klass, _ = self.suite.uid
        if klass is None:
            return 0
        return 1 + self.parent.relLevel()

    def write(self, f):
        suite = self.suite
        pathParts, klass, _ = suite.uid
        lev = self.relLevel()
        ulc = ulChars[lev]

        # Write out the suite class/path for the title
        if klass:
            title = klass
        else:
            path = self.suitePath
            #if path.endswith("all_tests.py"):
            #    path = os.path.basename(path)
            path = path.replace(".py", "")
            path = path.replace(".pyc", "")
            title = path
        title = "Suite: %s" % (title, )
        uLine = ulc * len(title)
        if lev == 0:
            f.write("%s\n" % uLine)
        else:
            f.write("\n\n")
        f.write("%s\n" % title)
        f.write("%s\n\n" % uLine)

        # Add TOC for child files.
        toc = self.toc
        if toc:
            f.write(".. toctree::\n")
            f.write("   :maxdepth: 2\n\n")
            for line in toc:
                f.write("   %s\n" % line)
            f.write("\n\n")

        f.write("%s\n" % suite.summary)
        if suite.details:
            f.write("\n")
            for line in suite.details:
                f.write("%s\n" % line)

    def addTest(self, test):
        self.tests.append(SphinxTest(test, self))


class SphinxTest(object):
    def __init__(self, test, parent):
        self.test = test
        self.parent = parent

    def write(self, f):
        test = self.test
        path, klass, func = test.uid
        title = test.testID
        if title is None:
            title = func
        title = "Test: %s" % title
        lev = 1 + self.parent.relLevel()
        ulc = ulChars[lev]
        uLine = ulc * len(title)
        f.write("\n\n%s\n" % title)
        f.write("%s\n\n" % uLine)
        f.write(":file: %s/%s\n" % test.uid[0])
        f.write(":class: %s\n" % test.uid[1])
        f.write(":method: %s\n\n" % test.uid[2])
        f.write("%s\n\n" % test.summary)
        for line in test.details:
            f.write("%s\n" % line)
        #f.write("\n")

        if test.testID is not None:
            f.write("\n.. <desc-end:%s>\n" % test.testID)

        setUp = self.parent.suite.setUp
        if getattr(setUp, "_cs_useForDocs", False):
            self.writeBlockOfSteps(f, self.parent.suite.getSpecFor("setUp"),
                                   ".. rubric:: Set up")

        n = self.writeBlockOfSteps(f, test.getTestProcedure(),
                               ".. rubric:: Procedure")

        postCheck = self.parent.suite.postCheck
        if getattr(postCheck, "_cs_useForDocs", False):
            self.writeBlockOfSteps(f, self.parent.suite.getSpecFor("postCheck"),
                                   nOffset=n)

        tearDown = self.parent.suite.tearDown
        if getattr(tearDown, "_cs_useForDocs", False):
            self.writeBlockOfSteps(f, self.parent.suite.getSpecFor("tearDown"),
                                   ".. rubric:: Tear down")

    def writeBlockOfSteps(self, f, spec, heading=None, nOffset=0):
        numberMode = 0
        prefixLens = [0] * 30
        for i, (n, block, boundArgs) in enumerate(spec.walkSteps()):
            if i == 0:
                n[0] += nOffset
            if numberMode == 0:
                num = ".".join("%d" % v for v in n) + ". "
            else:
                num = "%s. " % n[-1]
            idx = len(n)
            prefixLens[idx] = max(len(num), prefixLens[idx])

        n = [0]
        for i, (n, block, boundArgs) in enumerate(spec.walkSteps()):
            if i == 0:
                n[0] += nOffset
            nn = len(n)
            a = sum(prefixLens[:nn])
            b = prefixLens[nn]
            if heading:
                f.write("\n%s\n" % heading)
                heading = None
                if n[0] == 0:
                    f.write("\n%-*sSetup\n" % (a, "1. "))
                    n[0] += 1
            f.write("\n")

            if numberMode == 0:
                num = ".".join("%d" % v for v in n) + ". "
            else:
                num = "%s. " % n[-1]
            hangStr = "%*s%-*s" % (a, "", b, num)
            for line in addHang(block, hangStr):
                if boundArgs is not None:
                    for name, value in boundArgs.iteritems():
                        if not isinstance(value, str):
                            continue
                        line = re.sub(r'\b%s\b' % name, value, line)
                f.write("%s\n" % line)

        return n[0]


# TODO: Also in Manager.py and TermDisplay.py
def addHang(lines, hangText):
    res = []
    pad = " " * len(hangText)
    for i, line in enumerate(lines):
        if i:
            res.append(pad + line)
        else:
            res.append(hangText + line)
    return res


class SphinxDoc(object):
    def __init__(self):
        from CleverSheep.Test import Tester
        self.rootDir = Tester.execDir
        self.children = []
        self.known = {}
        self.toc = []

    def addToc(self, suite):
        #print "ADD >>TOC", suite.path
        self.toc.append(suite.path)

    def prepareTest(self, pushSuites, test):
        if not pushSuites:
            return
        #for lev, suite in pushSuites:
        #    print lev, suite.uid
        lev, suite = pushSuites[0]
        if lev == 0 and suite.uid not in self.known:
            #print lev, suite.uid
            ss = SphinxSuite(lev, suite, self.rootDir, self)
            self.known[suite.uid] = ss
            self.children.append(ss)
            rest = pushSuites[1:]
        else:
            rest = pushSuites
        for child in self.children:
            for s in child.addSubSuites(rest, self.rootDir):
                self.known[s.uid] = s

    def relLevel(self):
        return 0

    def addTest(self, test):
        pathParts, klass, funcName = test.uid
        key = pathParts, klass, None
        suite = self.known[key]
        suite.addTest(test)

    def generate(self):
        if 0:
            f = open(os.path.join(options.get_option_value("sphinx"), "index.rst"), "w")
            title = "Test specification"
            ulc = ulChars[0]
            uLine = ulc * len(title)
            f.write("%s\n" % uLine)
            f.write("%s\n" % title)
            f.write("%s\n\n" % uLine)
            toc = self.toc
            if toc:
                f.write(".. toctree::\n")
                f.write("   :maxdepth: 2\n\n")
                for line in toc:
                    f.write("   %s\n" % line)
                f.write("\n\n")

        for suite in self.children:
            suite.generate()
