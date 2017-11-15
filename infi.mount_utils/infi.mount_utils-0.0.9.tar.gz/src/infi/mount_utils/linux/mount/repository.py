import platform
import re
from munch import Munch
from ...base.mount import MountRepositoryMixin

from logging import getLogger
from collections import OrderedDict
log = getLogger()

class LinuxMountRepositoryMixin(MountRepositoryMixin):
    def _read_fstab(self):
        return self._read_file("/etc/fstab")

    def _read_mtab(self):
        return self._read_file("/etc/mtab")

    def _read_utab(self):
        return self._read_file("/run/mount/utab")

    def _parse_options_for_entry(self, entry):
        string = entry["opts"]
        results = OrderedDict()
        pattern = re.compile(OPTION_PATTERN)
        for match in pattern.finditer(string):
            key = match.groupdict().get("key")
            value = match.groupdict().get("value")
            results[key] = self._translate_value(value)
        entry["opts"] = results
        return results

    def _get_entries_dict_from_utab(self):
        pattern = re.compile(UTAB_ENTRY_PATTERN_LINUX, re.MULTILINE)
        string = self._read_utab()
        log.debug(u"utab content = \n{}".format(string))
        results = dict([(match.groups()[0], self._parse_options_for_entry(match.groupdict())) for match in
                       pattern.finditer(string)])
        return results

    def _canonicalize_path(self, path):
        # HPT-2164 sometimes mtab contains devices in their "dm" names which can change between boots.
        # 'mount' command handles this by canonicalizing the paths and turning them into the real (/dev/mapper) names:
        # https://git.kernel.org/pub/scm/utils/util-linux/util-linux.git/tree/lib/canonicalize.c (canonicalize_path)
        import os
        import stat
        if not os.path.exists(path):
            return path
        canonical = os.path.abspath(os.path.realpath(path))
        if "/" in canonical:
            part = canonical.rsplit("/", 1)[1]
            if part.startswith("dm-") and part[3:].isdigit() and stat.S_ISBLK(os.stat(canonical).st_mode):
                with open("/sys/block/{}/dm/name".format(part), "r") as fd:
                    name = fd.read().strip()
                return "/dev/mapper/" + name
        return canonical

    def _get_list_of_groupdicts_from_mtab(self):
        pattern = re.compile(MOUNT_ENTRY_PATTERN_LINUX, re.MULTILINE)
        string = self._read_mtab()
        log.debug(u"mtab content = \n{}".format(string))
        utab_results = self._get_entries_dict_from_utab()
        mtab_results = [match.groupdict() for match in pattern.finditer(string)]
        mtab_results = self._parse_options_in_entries(mtab_results)
        for mtab_result in mtab_results:
            fsname = mtab_result['fsname']
            if fsname in utab_results:
                mtab_result['opts'].update(utab_results[fsname])
            mtab_result['fsname'] = self._canonicalize_path(mtab_result['fsname'])

        return mtab_results

    def _get_list_of_groupdicts_from_fstab(self):
        pattern = re.compile(MOUNT_ENTRY_PATTERN_LINUX, re.MULTILINE)
        string = self._read_fstab()
        log.debug(u"fstab content = \n{}".format(string))
        results = [match.groupdict() for match in pattern.finditer(string)]
        return self._parse_options_in_entries(results)


WORD_PATTERN = r"[^# \t\n\r\f\v]+"
FSNAME_PATTERN = r"(?P<fsname>{})".format(WORD_PATTERN)
DIRNAME_PATTERN = r"(?P<dirname>{})".format(WORD_PATTERN)
TYPNAME_PATTERN = r"(?P<typename>{})".format(WORD_PATTERN)
STRING_PATTERN = r"[^,=# \t\n\r\f\v]+"
OPTION_PATTERN = r"(?P<key>{})(?:=(?P<value>{}))?".format(STRING_PATTERN, STRING_PATTERN)
OPTS_PATTERN = r"(?P<opts>{})".format(WORD_PATTERN)
FREQ_PATTERN = r"(?P<freq>\d*)"
PASSNO_PATTERN = r"(?P<passno>[\-\d]*)"
SEP = r"[ \t]+"

MOUNT_ENTRY_PATTERN_LINUX = r"^{fsname}{sep}{dirname}{sep}{typename}{sep}{opts}{sep}{freq}{sep}{passno}$".format(
                                           sep=SEP,
                                           fsname=FSNAME_PATTERN,
                                           dirname=DIRNAME_PATTERN,
                                           typename=TYPNAME_PATTERN,
                                           opts=OPTS_PATTERN,
                                           freq=FREQ_PATTERN,
                                           passno=PASSNO_PATTERN)

UTAB_ENTRY_PATTERN_LINUX = r"^SRC={fsname}{sep}TARGET={dirname}{sep}ROOT=/{sep}OPTS={opts}$".format(
                                           sep=SEP,
                                           fsname=FSNAME_PATTERN,
                                           dirname=DIRNAME_PATTERN,
                                           opts=OPTS_PATTERN)
