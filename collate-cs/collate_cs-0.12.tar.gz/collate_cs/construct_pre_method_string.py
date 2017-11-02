def _(methods, address, class_name):
    ret = []

    if 'using.cs' in methods:
        for line in methods['using.cs']:
            ret += [line]
        ret += ['']
        del(methods['using.cs'])

    ret += ['namespace ' + '.'.join(address)]
    ret += ['{']
    if 'test' in class_name:
        ret += ["    using NUnit.Framework;"]
        ret += [""]
        ret += ["    [TestFixture]"]
    ret += ["    [System.Serializable]"]


    if '_.cs' in methods:
        for line in methods['_.cs']:
            ret += ['    ' + line]
        del(methods['_.cs'])
    else:
        ret += ["    public class " + class_name]

    if '}' not in ret[-1]:
        ret += ["    {"]
        ret += ["    }"]

    ret = '\n' + '\n'.join(ret[:-1])
    return ret
