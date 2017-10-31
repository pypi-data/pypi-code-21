# import subprocess
# subprocess.call('dms2dfe prj',shell=True)

def test_configure():
    from dms2dfe import configure
    configure.main('prj')

# test_configure()