import os
import a99


__all__ = ["ErrorCollector", "Occurrence"]


class Occurrence(object):
    """Class that carries information about an error/warning, with HTML rendering ability"""
    colors = {"undefined": "#000000",
              "warning": a99.COLOR_WARNING,
              "error": a99.COLOR_ERROR,
              "cannot open": a99.COLOR_ERROR}

    def __init__(self, filename, type_, line, message):
        # "undefined"/"warning"/"error"/"cannot open"
        self.type = type_
        self.message = message
        self.filename = filename
        self.line = line

    def get_html(self):
        message = self.message if isinstance(self.message, str) \
         else "\n".join(self.message)
        return ("<h3>File '{0!s}' (<span style=\"color: {1!s}\">{2!s}</span>)</h3>\n".format(self.filename, self.colors[self.type], self.type))+ \
         ("" if not self.line else "<b>line {0:d}</b>\n".format(self.line))+ \
         ("<pre>{0!s}</pre>".format(message) if message else "")


class ErrorCollector(object):
    """Walks through directory in search for files 'python.log' and 'fortran.log'.

    Opens these files and extracts error information from them (if found).
    """

    def __init__(self):
        # List of Occurrence
        self.occurrences = []

    def collect_errors(self, path_):
        self.occurrences = []
        for p, dirs, files in os.walk(path_):
            for file in files:
                if file == "python.log":
                    pass
                    # parses python log
                elif file == "fortran.log":
                    path__ = os.path.relpath(os.path.join(p, file), ".") # os.path.relpath(os.path.join(path_, file), path_)
                    try:
                        linetext_last = ""
                        line, flag_halting = 1, False
                        with open(path__, "r") as h:
                            for t in h:
                                linetext = t.strip()
                                if "HALTING" in linetext:
                                    if not flag_halting:
                                        occ = Occurrence(path__, "error", line, [])
                                        self.occurrences.append(occ)
                                        flag_halting = True
                                    occ.message.append(linetext)
                                else:
                                    flag_halting = False

                                if "Fortran runtime error" in linetext:
                                    occ = Occurrence(path__, "error", line,
                                     [linetext_last, linetext])
                                    self.occurrences.append(occ)

                                if "WARNING" in linetext:
                                    occ = Occurrence(path__, "warning", line, linetext)
                                    self.occurrences.append(occ)

                                line += 1
                                linetext_last = linetext
                    except IOError as E:
                        occ = Occurrence(path__, "cannot open", 0, str(E))
                        self.occurrences.append(occ)

    def get_html(self):
        oo = [occ.get_html() for occ in self.occurrences]
        if len(oo) == 0:
            return "No errors were found."
        return "\n".join(oo)

