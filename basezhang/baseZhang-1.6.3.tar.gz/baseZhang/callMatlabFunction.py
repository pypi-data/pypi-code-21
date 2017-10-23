import matlab_wrapper


def run_matlab_codes(matlab_root='/Applications/MATLAB_R2015b.app/'):
    matlab = matlab_wrapper.MatlabSession(matlab_root=matlab_root)

    return matlab

# matlab.put('a', 12.3)
# print matlab.get('a')
# matlab.eval('plot([1,2,3])')
# put () get() eval()
