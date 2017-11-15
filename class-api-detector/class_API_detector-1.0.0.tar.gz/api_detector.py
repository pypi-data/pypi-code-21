#!/usr/bin/python
" class API detector "


def analyze_class(name, cls, obj=None, show_autogen=False, show_doc=False):
    """Analyze a class API

    Positional arguments:
        -name: name of the class (given as a string)
        -cls: class (as an object)
    Optional arguments:
        -obj: an instance of the class
        -show_autogen: show also auto-generated methods
        -show_doc: also print class' documentation

    The function will use the provided information to determine the
    attributes, methods and properties of the class, discriminating
    public, protected, private and special kinds of each. Results
    will be displayed to stdout.
    """
    # print header before possible error/warning messages
    print("-= {:} class API =-".format(name))

    # first, make sure an object is available for analysis
    if obj is None:
        # try to create an instance of the class
        try:
            # if class provides a method to create a sample object, use it
            obj = cls._get_sample()
        except AttributeError:
            # else assume there's an argument-less constructor available
            try:
                obj = cls()
            except TypeError:
                # if that didn't work either, abandon some tests
                print("couldn't create a sample object with argument-less",
                      "constructor, so attributes (if any) won't be properly",
                      "detected\nworkaround: provide a proper object with the",
                      "'obj=...' optional argument", sep=' ')

    # detect @properties
    properties = [p for p in dir(cls) if isinstance(getattr(cls, p), property)]
    privp = []
    protp = []
    publp = []
    for key in sorted(properties):
        test = key.split('_{:}'.format(name))
        if test[0] == '':
            # true for _Classname__bla_bli -> ['', '__bla_bli']
            privp.append(test[1])
        else:
            test = key.split('_')
            if test[0] == '':  # true if starts by _
                protp.append(key)
            else:
                publp.append(key)

    attributes = []
    # detect attributes, if any are available
    if obj is not None:
        try:
            attributes = obj.__dict__
        except AttributeError:
            print("No attributes detected, so this might be a 'simple type' "
                  + "rather than a 'class'. Methods may still be available.")

    priva = []
    prota = []
    publa = []
    for key in sorted(attributes):
        test = key.split('_{:}'.format(name))
        if test[0] == '':
            # true for _Classname__bla_bli -> ['', '__bla_bli']
            priva.append(test[1])
        else:
            test = key.split('_')
            if test[0] == '':  # true if starts by _
                prota.append(key)
            else:
                publa.append(key)

    # detect methods and specials
    methods = cls.__dict__
    privm = []
    protm = []
    publm = []
    spem = []
    autogen = []
    for key in sorted(methods):
        test = key.split('_{:}'.format(name))
        if test[0] == '':
            # true for _Classname__bla_bli -> ['', '__bla_bli']
            res = test[1]
            if res not in privp:
                privm.append(res)
        else:
            if '__' in key:
                if key in ['__dict__', '__doc__', '__hash__', '__module__',
                           '__weakref__']:
                    autogen.append(key)
                else:
                    spem.append(key)
            else:
                test = key.split('_')
                if test[0] == '':  # true if starts by _
                    protm.append(key)
                elif key not in publp:
                    publm.append(key)

    # display results
    if show_doc:
        print('{:}:'.format(name), cls.__doc__)

    def printif(alist, aname):
        if alist:
            aname = '-{:10s}'.format(aname)
            astring = ', '.join(alist)
            if len(astring) < 60:
                print(aname + ': ' + astring)
            else:
                # print(aname + ':\n  ' + astring)
                trunc = astring[:60]
                n = trunc.count(',')
                astring = ', '.join(alist[:n])
                print(aname + ': ' + astring + ',')
                astring = ', '.join(alist[n:])
                print('             ' + astring)
    if publa or publp or publm:
        print("PUBLIC:")
        printif(publa, 'attributes')
        printif(publp, 'properties')
        printif(publm, 'methods(*)')
    if publm:
        print("(*) known shortcoming: "
              + "class methods/attributes will also appear here")
    if prota or protp or protm:
        print("PROTECTED:")
        printif(prota, 'attributes')
        printif(protp, 'properties')
        printif(protm, 'methods')
    if priva or privp or privm:
        print("PRIVATE:")
        printif(priva, 'attributes')
        printif(privp, 'properties')
        printif(privm, 'methods')
    if spem:
        print("SPECIAL:")
        printif(spem, 'operators ')
        if show_autogen:
            printif(autogen, 'auto-gen  ')


if __name__ == "__main__":
    "example usage"

    class Dummy():
        "A dummy class for testing"
        class_variable = 42

        def class_method():
            pass

        def __init__(self, other):
            self.ble = other
            self._fee = ""
            self.__feh = []

        def foo(self, bar):
            pass

        def _bar(self, bar):
            pass

        def __bla(self, bar):
            pass

        @property
        def content(self):
            return self.content

    analyze_class('str', str, show_autogen=True)
    print()
    analyze_class('Dummy', Dummy, show_autogen=True, show_doc=True,
                  obj=Dummy(42))

# ------------------------
# CopyLeft by dalker
# create date: 2017-07-24
# modif  date: 2017-11-15
# ------------------------
