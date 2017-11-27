from __future__ import absolute_import, division, print_function
import autest.glb as glb
import hosts.output as host


def RegisterFileType(cls, typename, ext=[]):
    '''
    Registers a file class to be use instead of the default file class
    based on a type field or file ext of the file being created.
    This allow for more functional file classes to be defined allowing for 
    better testing or and logic to deal with various set of needs
    '''

    # imported here to break import cycle
    from autest.testenities.file import File

    if not issubclass(cls, File):
        host.WriteError(
            "Object must be subclass of autest.testenity.file.File")

    glb.FileTypeMap[typename] = cls
    for e in ext:
        glb.FileExtMap[e] = cls
