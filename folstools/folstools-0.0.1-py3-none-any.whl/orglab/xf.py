import re
import os


class XFGUI:
    def __init__(self, orgexe, filepath=r"c:\xfgui", reportpath=r"d:\report.txt"):
        self._orgexe = orgexe
        self._filepath = filepath
        self._reportpath = reportpath

    def GUI2XF(self):
        scripts = []
        for file in os.listdir(self._filepath):
            m = self.Match(r"(.)XFGUI_(.*)\.xml", file)
            if m:
                scripts.append('gui2xf "%s" l:=%s;' % (m.group(2), m.group(1)))
            if len(scripts) == 50:
                self.Run(''.join(scripts))
                scripts.clear()
        if scripts:
            self.Run(''.join(scripts))
        return scripts

    def XF2GUI(self, langs):
        xfs = []
        with open(self._reportpath, "r") as fr:
            script = ""
            for i, line in enumerate(fr):
                m1 = self.Match(r".*\\(.*)\.oxf", line)
                m2 = self.Match(r"(.*) changes:", line)
                m3 = self.Match(r"(.*)\.oxf", line)
                m = m1 if m1 else (m2 if m2 else m3)
                if m:
                    xfs.append(m.group(1))
                    for c in langs:
                        script += ('xf2gui "%s" l:=%s;' % (m.group(1), c))
                        if len(script) >= 8000:
                            self.Run(script)
                            script = ''
            if script:
                self.Run(script)
        return xfs

    def Clear(self):
        for file in os.listdir(self._filepath):
            m = self.Match(r".XFGUI_.*\.xml", file)
            if m:
                os.remove(os.path.join(self._filepath, file))

    def Run(self, script):
        if len(script) != 0:
            os.system("{} -h -rs {};exit;".format(self._orgexe, script))

    def Match(self, pattern, string):
        return re.match(pattern, string, re.I)
