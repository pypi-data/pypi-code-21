from munch import Munch


class MountEntry(object):

    DIRNAME_REPLACE_COUPLES = (
       (r"\040", " "),     # HIP-688 spaces appear different in mtab
       (r"\134", "\\"),    # HPT-1905
    )

    @classmethod
    def from_groupdict(cls, groupdict):
        return cls(**groupdict)

    def __init__(self, fsname, dirname, typename, opts=dict(), freq=0, passno=0):
        self._bunch = Munch(fsname=fsname, dirname=dirname,
                            typename=typename, opts=opts,
                            freq=freq, passno=passno)

    def get_fsname(self):
        """:returns: name of mounted file system"""
        return self._bunch.fsname

    def set_fsname(self, fsname):
        self._bunch.fsname = fsname

    def get_dirname(self):
        """:returns: file system path prefix"""
        replaced_dirname = self._bunch.dirname
        for original_value, replaced_value in self.DIRNAME_REPLACE_COUPLES:
            replaced_dirname = replaced_dirname.replace(original_value, replaced_value)
        return replaced_dirname

    def get_typename(self):
        """:returns: mount type"""
        return self._bunch.typename

    def get_opts(self):
        """:returns: mount options"""
        return self._bunch.opts

    def get_freq(self):
        """:returns: dump frequency in days"""
        return self._bunch.freq

    def get_passno(self):
        """:returns: pass number on parallel fsck"""
        return self._bunch.passno

    def _str_options(self):
        if self.get_opts().keys() == []:
            return ''
        options = ''
        for key, value in self.get_opts().items():
            if value is True:
                options += "{},".format(key)
            else:
                options += "{}={},".format(key, value)
        return options.strip(',')

    def __str__(self):
        return "\t".join(item.encode("utf-8") for item in
                         [self.get_fsname(), self.get_dirname(), self.get_typename(),
                         self._str_options(), self.get_freq(), self.get_passno()])
