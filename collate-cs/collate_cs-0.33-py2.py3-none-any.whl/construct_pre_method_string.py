import namespace_override as override

def _(methods, address, class_name):
    ret = []

    if 'using.cs' in methods:
        for line in methods['using.cs']:
            ret += [line]
        ret += ['']
        del(methods['using.cs'])

    address = list(map(lambda s: override._(s), address))
    ret += ['namespace ' + '.'.join(address)]
    ret += ['{']
    if 'test' in class_name:
        ret += ["    using NUnit.Framework;"]
        ret += [""]
        ret += ["    [TestFixture]"]


    if '_.cs' in methods:
        start = list(methods['_.cs'])
        if 'interface' not in start[0]:
            ret += ["    [System.Serializable]"]
        for line in start:
            ret += ['    ' + line]
        del(methods['_.cs'])
    else:
        ret += ["    [System.Serializable]"]
        ret += ["    public class " + class_name]


    if '}' not in ret[-1]:
        ret += ["    {"]
        ret += ["    }"]

    ret = '\n' + '\n'.join(ret[:-1])
    return ret
