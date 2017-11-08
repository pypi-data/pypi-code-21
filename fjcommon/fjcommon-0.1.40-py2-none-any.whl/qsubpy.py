def sge_map(fn, num_jobs):

    pass


def run_python_function_inside_script():
    import subprocess
    import os
    otp = subprocess.check_output(['python', 'test/hello.py'],
                                  env={'PYTHONPATH':
                                       os.path.expanduser('~/Documents/Aktiv/fjcommon/fjcommon')})
    otp = otp.decode()
    print(otp)


if __name__ == '__main__':
    run_python_function_inside_script()

