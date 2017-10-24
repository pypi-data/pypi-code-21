###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''

Common model classes representing the RPM packages, and their provide
and require attributes.

:author: Ben Couturier
'''

import inspect

# Deps added by RPM by default which we just ignore
##############################################################################
IGNORED_PACKAGES = ["rpmlib(CompressedFileNames)",
                    "/bin/sh",
                    "/bin/bash",
                    "rpmlib(PayloadFilesHavePrefix)",
                    "rpmlib(PartialHardlinkSets)"]


# Little util to clean versions conatining the -release at the end
##############################################################################
def normalizeVersionRelease(version, release):
    """ Cleanup version

    :param version: the version to normalize
    :param release: the release to normalize

    :returns: tuple of normalized version and release
    """

    if version is None:
        return (version, release)

    tmpver = version
    tmprel = release
    # Just do it when release isn't specified
    if "-" in tmpver and not release:
        tmp = tmpver.split("-")
        tmpver = "-".join(tmp[:-1])
        tmprel = tmp[-1]
    return (tmpver, tmprel)


# Classes representing requirements and functionality provided by RPMs
###############################################################################
class VersionedObject(object):
    """ Ancestor for classes representing all versioned objects
    (Provides, Requires...)

    :param name: the name of the object
    :param version: the version of the object
    :param release: the release of the object
    :param epoch: the epoch of the object
    :param flags: the flags of the object
    """

    def __init__(self, name, version, release, epoch, flags):
        """ Constructor for the class """
        self.name = name
        self.version = version
        self.release = release
        self.epoch = epoch
        self.flags = flags
        self.standardVersion = VersionedObject.getStandardVersion(version)

    # version comparison methods used for dynamic lookup
    ###########################################################################
    def eq(self, x):  # IGNORE:C0103
        """ Custom  equal operator

        :param x: the object to be compared with
        :returns: the results of the equal operator
        """
        return self == x

    def lt(self, x):  # IGNORE:C0103
        """ Custom less operator

        :param x: the object to be compared with
        :returns: the results of the less operator
        """
        return x < self

    def le(self, x):  # IGNORE:C0103
        """ Custom less equal operator

        :param x: the object to be compared with
        :returns: the results of the less equal operator
        """
        # Python 3 migration: it supports only eq and lt
        return self.lt(x) or self.eq(x)

    def gt(self, x):  # IGNORE:C0103
        """ Custom greater operator

        :param x: the object to be compared with
        :returns: the results of the greater operator
        """
        # Python 3 migration: it supports only eq and lt
        return not(self.lt(x) or self.eq(x))

    def ge(self, x):  # IGNORE:C0103
        """ Custom greater equal operator

        :param x: the object to be compared with
        :returns: the results of the grater equal operator"""
        # Python 3 migration: it supports only eq and lt
        return not(self.lt(x))

    @classmethod
    def getStandardVersion(cls, version):
        """ parse the version and return the list of major,
        minor,etc version numbers

        :param version: the version to be parsed
        :returns: the list of version numbers
        """

        # First check parameters
        if version is None:
            return None

        # Old algo which leads to issues:
        # If the version is of the form: x.y.z
        # return an array with version numbers,
        # e.g. [ 1, 23, 45 ]
        # None otherwise.
        # If it is defined it should be used for comparing versions,
        # otherwise the version strings will be compared
        # if re.match('\d+(\.\d+)*$', version):
        #    standardVersion =  [ int(n) for n in version.split(".") ]

        # We just split with the points and do numerical comparison when we can
        standardVersion = [n for n in str(version).split(".")]
        return standardVersion

    @classmethod
    def cmpStandardVersion(cls, v1, v2):
        """
        Common method for comparing standard versions as arrays of numbers

        :param v1: version to be compared
        :param v2: version to be compared
        :returns: the result of the comparing standard versions
        """
        # zip actually shotens to the length of the shorter list
        # This is ok in our case
        zippedVers = zip(v1, v2)
        cmplist = [VersionedObject._cmpUtil(a, b) for (a, b) in zippedVers
                   if VersionedObject._cmpUtil(a, b) != 0]
        if len(cmplist) == 0:
            return 0
        else:
            return cmplist[0]

    @classmethod
    def _cmpUtil(cls, a, b):  # IGNORE:C0103
        """ Utility function that compares strings
        in the following manner:
        - if both string represent numbers, perform an integer comparison
        - otherwise consider both as strings..."""
        if a.isdigit() and b.isdigit():
            return int(a) - int(b)
        # Python 3 compatible
        if a < b:
            return -1
        elif a == b:
            return 0
        else:
            return 1

    # TODO: Move this method to the children, matching the name
    def provideMatches(self, provide):
        """ returns true if the provide passed in parameter
        matches the requirement

        :param provide: the provide that need to be looked up
        :returns: True if the provide matches the requirement, False otherwise
        """
        # Checking the name of course....
        if provide.name != self.name:
            return False

        # If the requirement does not have a version, then it is a match...
        # As we have name equality...
        if self.version is None or \
           (self.version is not None and len(self.version) == 0):
            return True

        # If we have a release number but the provide does not
        # it cannot be a match...
        if self.release is not None and provide.release is None:
            return False

        allmethods = inspect.getmembers(self, predicate=inspect.ismethod)
        foundMethod = None
        methodname = self.flags.lower()
        for m in allmethods:  # IGNORE:C0103
            if m[0].lower() == methodname:
                foundMethod = m[1]
                break
        return(foundMethod(provide))

    def __eq__(self, other):
        """ Equal method for dependencies """
        if other is None:
            return False
        # check if the name is different different
        if self.name != other.name:
            return False
        # At this point we check if the versions are the same
        if self.standardVersion is None or other.standardVersion is None:
            # We couldn't parse the version as a standard x.y.z for both
            # In this case we check if the strings are the same
            return self.version == other.version
        # In this case we check if the the version lists are the same
        cmpVers = VersionedObject.cmpStandardVersion(self.standardVersion,
                                                     other.standardVersion)
        if cmpVers != 0:
            # Versions are different we do not need to compare
            # release numbers
            return False
        # Comparing down to the release numbers
        r1 = self.release
        r2 = other.release
        # If one is missing a release number they potentially match
        if not r1 or not r2:
            return True
        else:
            return r1 == r2

    def __lt__(self, other):
        """ Less then method for dependencies """
        if other is None:
            return True
        # check if the name is different different
        if self.name != other.name:
            return self.name < other.name
        # At this point we check if the versions are the same
        if self.standardVersion is None or other.standardVersion is None:
            # We couldn't parse the version as a standard x.y.z for both
            # In this case we check if the strings are the same
            return self.version is None
        # In this case we check if the the version lists are the same
        cmpVers = VersionedObject.cmpStandardVersion(self.standardVersion,
                                                     other.standardVersion)
        if cmpVers != 0:
            # Versions are different we do not need to compare
            # release numbers
            return cmpVers < 0
        # Comparing down to the release numbers
        r1 = self.release
        r2 = other.release
        # If one is missing a release number they potentially match
        if not r1 or not r2:
            return False
        else:
            return r1 < r2

    def __cmp__(self, other):
        """ Comparison method for dependencies """
        if other is None:
            return -1

        # ordering by name if they are different
        if self.name != other.name:
            return cmp(self.name, other.name)
        else:
            # At this point we can compare the versions
            if self.standardVersion is None or other.standardVersion is None:
                # We couldn't parse the version as a standard x.y.z for both
                # In this case we do string comparison
                return cmp(self.version, other.version)
            else:
                # In this case we can compare the version lists
                cmpVers = VersionedObject.cmpStandardVersion(
                    self.standardVersion,
                    other.standardVersion)
                if cmpVers != 0:
                    # Versions are different we do not need to compare
                    # release numbers
                    return cmpVers
                else:
                    # Comparing down to the release numbers
                    r1 = self.release
                    r2 = other.release

                    # If one is missing a release number they potentially match
                    if not r1 or not r2:
                        return 0

                    if r1.isdigit() and r2.isdigit():
                        return cmp(int(r1), int(r2))
                    else:
                        return cmp(r1, r2)

    # Pretty printing
    ###########################################################################
    def __str__(self):
        """ Display function for the package instance """
        return "%s(%s.%s-%s)" % (self.flags, self.name,
                                 self.version, self.release)

    def __repr__(self):
        return self.__str__()


# Classes actually representing the Require and Provide of the RPM Specs
###############################################################################
class Provides(VersionedObject):
    """ Class representing a functionality provided by a package

    :param name: the name of the object
    :param version: the version of the object
    :param release: the release of the object
    :param epoch: the epoch of the object
    :param flags: the flags of the object. Default is EQual
    :param package: the package that the object provides
    """

    def __init__(self, name, version, release, epoch=None,
                 flags="EQ", package=None):
        super(Provides, self).__init__(name, version, release, epoch, flags)
        # Provides can actually know which package they provide for
        # This is useful for looking for packages in the repository
        self.package = package


class Requires(VersionedObject):

    """ Class representing a functionality required by a package

    :param name: the name of the object
    :param version: the version of the object
    :param release: the release of the object
    :param epoch: the epoch of the object
    :param flags: the flags of the object. Default is Greater or Equal
    :param pre: the required package
    """

    def __init__(self, name, version, release, epoch=None,
                 flags="GE", pre=None):
        super(Requires, self).__init__(name, version, release,
                                       epoch, flags)
        self.pre = pre


# Package: Class representing a package available for installation
###############################################################################
class Package(VersionedObject):  # IGNORE:R0902
    """ Class representing an RPM package in the repository

    :param name: the name of the object
    :param version: the version of the object
    :param release: the release of the object
    :param epoch: the epoch of the object
    :param flags: the flags of the object
    :param group: the user group of the package
    :param arch: the type of the architecture for the package
    :param location: the remote location of package rpm
    :param provides: the list of provides
    :param requires: the list of requires
    :param relocatedLocation: the location of the files after relocation
                              (installation)
    """
    #
    # Constructor and public method
    ###########################################################################
    def __init__(self, name=None, version=None, release=None,
                 epoch=None, flags=None, group=None, arch="noarch",
                 location=None, provides=None, requires=None,
                 relocatedLocation=None):
        """ Default constructor """
        super(Package, self).__init__(name, version, release, epoch, flags)
        self.group = group
        self.arch = arch
        self.location = location
        self.relocatedLocation = relocatedLocation
        if requires is not None:
            self.requires = requires
        else:
            self.requires = []
        if provides is not None:
            self.provides = provides
        else:
            self.provides = []
        self.repository = None

    def setRepository(self, repo):
        """ Sets the instance repository

        :param repo: the repository that needs to be added to the package
        """
        self.repository = repo

    def rpmName(self):
        """ Formats the name of the RPM package

        :returns: the rpm name of the package
        """
        return "%s-%s-%s" % (self.name, self.version, self.release)

    def rpmFileName(self):
        """ Formats the name of the RPM package

        :returns: the rpm file name of the package"""
        return "%s-%s-%s.%s.rpm" % (self.name, self.version,
                                    self.release, self.arch)

    def url(self):
        """ Returns the URL to download the file

        :returns: the full url of the remote rpm file"""
        return self.repository.repourl + "/" + self.location

    def fulfills(self, req):
        ''' Checks whether there is a provides for the package that
        fullfill the requirement

        :param req: the requirement that needs to be checked
        :returns: True if the packages fullfiles the requirement.'''
        for p in self.provides:
            if req.provideMatches(p):
                return True
        return False

# XXX Not needed and even harmful
# Need to Check to see why it was added...
#     def __eq__(self, other):
#         if other == None:
#             return False
#         return self.name == other.name \
#                and self.version == other.version

    def __hash__(self):
        return hash((self.name, self.version, self.group, self.arch))

    #
    # Methods for pretty display
    ###########################################################################
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """ Display function for the package instance """
        tmpstr = "Package: %s-%s-%s\t%s" % (self.name, self.version,
                                            self.release, self.group)
        if len(self.provides) > 0:
            tmpstr += "\nProvides:\n"
            for pr in self.provides:
                tmpstr += "\t%s-%s-%s\n" % (pr.name, pr.version, pr.release)
        if len(self.requires) > 0:
            tmpstr += "\nRequires:\n"
            for req in self.requires:
                tmpstr += "\t%s-%s-%s\t%s\n" % (req.name, req.version,
                                                req.release, req.flags)
        return tmpstr
