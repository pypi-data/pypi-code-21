from . import Implementation, LanguageDependantClassInfo


class PythonImplementation(Implementation):
    _fields = ["code",
               ]


class PythonClassInfo(LanguageDependantClassInfo):
    _fields = ["id",
               "imports",
               ]
