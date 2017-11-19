from os.path import join, dirname, abspath


class datafilesc(object):
    @staticmethod
    def get(filename):
        packagedir = abspath(__file__)
        fulldir = join(dirname(packagedir), 'data')
        fullname = join(fulldir, filename)
        return fullname
